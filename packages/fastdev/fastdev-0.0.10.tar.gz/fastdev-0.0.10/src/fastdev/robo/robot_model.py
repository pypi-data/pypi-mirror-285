from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

import numpy as np
import torch
import trimesh
import yourdfpy
from torch import Tensor
from torch.types import Device
from trimesh.util import concatenate

from fastdev.xform.rotation import quaternion_to_matrix
from fastdev.xform.transforms import rot_tl_to_tf_mat

ROOT_JOINT_NAME = "__root__"
JOINT_SPEC_TENSOR_SIZE = 19


class Geometry(ABC):
    @abstractmethod
    def get_trimesh(self) -> trimesh.Trimesh: ...


@dataclass
class Box(Geometry):
    size: list[float]

    def get_trimesh(self) -> trimesh.Trimesh:
        return trimesh.creation.box(self.size)


@dataclass
class Cylinder(Geometry):
    radius: float
    length: float

    def get_trimesh(self) -> trimesh.Trimesh:
        return trimesh.creation.cylinder(radius=self.radius, height=self.length)


@dataclass
class Capsule(Geometry):
    radius: float
    length: float

    def get_trimesh(self) -> trimesh.Trimesh:
        return trimesh.creation.capsule(radius=self.radius, height=self.length)


@dataclass
class Sphere(Geometry):
    radius: float

    def get_trimesh(self) -> trimesh.Trimesh:
        return trimesh.creation.icosphere(subdivisions=3, radius=self.radius)


@dataclass
class Mesh(Geometry):
    scale: list[float]

    filename: str | None = None
    vertices: np.ndarray | None = None
    faces: np.ndarray | None = None

    def get_trimesh(self) -> trimesh.Trimesh:
        if self.vertices is None or self.faces is None:
            assert self.filename is not None, "Either filename or vertices and faces must be provided"
            mesh: trimesh.Trimesh = trimesh.load_mesh(self.filename)  # type: ignore
            self.vertices, self.faces = mesh.vertices, mesh.faces
        return trimesh.Trimesh(self.vertices * np.asarray(self.scale), self.faces)


@dataclass
class Material:
    name: str | None = None
    color: np.ndarray | None = None
    texture: str | None = None


@dataclass
class Visual:
    origin: np.ndarray
    geometry: Geometry
    name: str | None = None
    material: Material | None = None

    def get_trimesh(self) -> trimesh.Trimesh:
        mesh = self.geometry.get_trimesh()
        return mesh.apply_transform(self.origin)


@dataclass
class Collision:
    origin: np.ndarray
    geometry: Geometry
    name: str | None = None

    def get_trimesh(self) -> trimesh.Trimesh:
        mesh = self.geometry.get_trimesh()
        return mesh.apply_transform(self.origin)


class JointType(Enum):
    ROOT = -1  # used for base link, which has no parent joint
    FIXED = 0
    PRISMATIC = 1
    REVOLUTE = 2  # aka. rotational


@dataclass(frozen=True)
class Joint:
    name: str
    type: JointType
    origin: Tensor
    axis: Tensor
    limit: Tensor | None

    parent_link_name: str
    child_link_name: str


@dataclass(frozen=True)
class Link:
    name: str
    visuals: list[Visual] = field(default_factory=list)
    collisions: list[Collision] = field(default_factory=list)

    joint_name: str = field(init=False)  # parent joint name in urdf

    def set_joint_name(self, joint_name: str):
        object.__setattr__(self, "joint_name", joint_name)

    def get_trimesh(self, mode: Literal["visual", "collision"] = "collision") -> trimesh.Trimesh:
        if mode == "visual":
            meshes = [visual.get_trimesh() for visual in self.visuals]
        elif mode == "collision":
            meshes = [collision.get_trimesh() for collision in self.collisions]
        else:
            raise ValueError(f"Unknown mode: {mode}")
        return concatenate(meshes)  # type: ignore


@dataclass
class RobotModelConfig:
    """Robot model configuration."""

    device: Device = "cpu"

    urdf_path: str | None = None
    mjcf_path: str | None = None
    mesh_dir: str | None = None
    mjcf_assets: dict[str, Any] | None = None

    ee_link_names: list[str] | None = None  # will be inferred if not provided

    def __post_init__(self):
        if self.urdf_path is None and self.mjcf_path is None:
            raise ValueError("Either urdf_path or mjcf_path must be provided")
        elif self.urdf_path is not None and self.mjcf_path is not None:
            raise ValueError("Only one of urdf_path and mjcf_path should be provided")


class RobotModel:
    """Robot model.

    Args:
        config (RobotModelConfig): Robot model configuration.

    Examples:
        >>> robot_model = RobotModel(RobotModelConfig(urdf_path="assets/robot_description/panda.urdf", device="cpu"))
        >>> robot_model.num_dofs
        9
        >>> link_poses = robot_model.forward_kinematics(torch.zeros(1, 9))
        >>> torch.allclose(link_poses[0, -1, :3, 3], torch.tensor([0.10323, 0, 0.86668]), atol=1e-3)
        True
    """

    def __init__(self, config: RobotModelConfig) -> None:
        self.config = config

        if config.urdf_path is not None:
            self.joint_map, self.link_map = self.parse_urdf()
        elif config.mjcf_path is not None:
            self.joint_map, self.link_map = self.parse_mjcf()

        # infer active joint names
        self.active_joint_names: list[str] = [
            joint_name
            for joint_name, joint in self.joint_map.items()
            if joint.type not in [JointType.FIXED, JointType.ROOT]
        ]

        # infer number of DOFs
        self.num_dofs = len(self.active_joint_names)

        # set base link name
        self.base_link_name = self.joint_map[ROOT_JOINT_NAME].child_link_name
        # infer ee link names if not provided
        if isinstance(self.config.ee_link_names, list):
            pass
        if isinstance(self.config.ee_link_names, str):
            self.config.ee_link_names = [self.config.ee_link_names]
        elif self.config.ee_link_names is None:
            _link_names = list(self.link_map.keys())
            for joint in self.joint_map.values():
                if joint.parent_link_name in _link_names:
                    _link_names.remove(joint.parent_link_name)
            if len(_link_names) == 0:
                raise ValueError("Could not determine end effector link.")
            self.config.ee_link_names = _link_names
        self.ee_link_names = self.config.ee_link_names
        # sort all links in topological order
        cur_links = [self.base_link_name]
        topological_order = []
        while cur_links:
            next_links = []
            for link_name in cur_links:
                topological_order.append(link_name)
                for joint in self.joint_map.values():
                    if joint.parent_link_name == link_name:
                        next_links.append(joint.child_link_name)
            cur_links = next_links
        self.link_names = topological_order

        # collect joint limits
        joint_limits = []
        if self.joint_map[self.active_joint_names[0]].limit is None:
            self.joint_limits = None
        else:
            for joint_name in self.active_joint_names:
                joint = self.joint_map[joint_name]
                if joint.limit is None:
                    raise ValueError(f"Joint {joint_name} has no limit")
                joint_limits.append(joint.limit)
            self.joint_limits = torch.stack(joint_limits, dim=0)

    def parse_urdf(self) -> tuple[dict[str, Joint], dict[str, Link]]:
        """Parse URDF file and return kinematics configuration.

        Args:
            urdf_path (str): URDF file path.
            mesh_dir (str | None, optional): Directory containing mesh files. Defaults to None.
            base_link_name (str | None, optional): Base link name, will be inferred if not provided. Defaults to None.
            ee_link_names (str | list[str] | None, optional): End effector link names, will be inferred if not provided.
                Defaults to None.
            parallel_chains (bool, optional): If True, all kinematic chains will be calculated in parallel, otherwise
                sequentially (num_chains == 1). Parallel calculation is faster but requires more memory. Defaults to False.

        Returns:
            KinematicsConfig: Kinematics configuration.
        """

        def urdf_str_to_joint_type(joint_type_str: str) -> JointType:
            if joint_type_str == "fixed":
                return JointType.FIXED
            elif joint_type_str == "prismatic":
                return JointType.PRISMATIC
            elif joint_type_str == "revolute":
                return JointType.REVOLUTE
            else:
                raise ValueError(f"Unknown joint type: {joint_type_str}")

        def build_joint_from_urdf(joint_spec: yourdfpy.urdf.Joint) -> Joint:
            joint_type = urdf_str_to_joint_type(joint_spec.type)
            if (
                joint_spec.limit is not None
                and joint_spec.limit.lower is not None
                and joint_spec.limit.upper is not None
            ):
                limit = torch.tensor(
                    [joint_spec.limit.lower, joint_spec.limit.upper], dtype=torch.float32, device=self.config.device
                )
            else:
                limit = None
            return Joint(
                name=joint_spec.name,
                type=joint_type,
                origin=torch.from_numpy(joint_spec.origin).to(device=self.config.device, dtype=torch.float32),
                axis=torch.from_numpy(joint_spec.axis).to(device=self.config.device, dtype=torch.float32),
                limit=limit,
                parent_link_name=joint_spec.parent,
                child_link_name=joint_spec.child,
            )

        def build_geometry_from_urdf(urdf_geometry: yourdfpy.urdf.Geometry, mesh_dir: str) -> Geometry:
            if urdf_geometry.box is not None:
                return Box(size=urdf_geometry.box.size.tolist())
            elif urdf_geometry.cylinder is not None:
                return Cylinder(radius=urdf_geometry.cylinder.radius, length=urdf_geometry.cylinder.length)
            elif urdf_geometry.sphere is not None:
                return Sphere(radius=urdf_geometry.sphere.radius)
            elif urdf_geometry.mesh is not None:
                scale_spec = urdf_geometry.mesh.scale
                if isinstance(scale_spec, float):
                    scale: list[float] = [scale_spec, scale_spec, scale_spec]
                elif isinstance(scale_spec, np.ndarray):
                    scale = scale_spec.tolist()
                elif scale_spec is None:
                    scale = [1.0, 1.0, 1.0]
                else:
                    raise ValueError(f"Unknown scale type: {scale_spec}")
                mesh_path = os.path.join(mesh_dir, urdf_geometry.mesh.filename)
                return Mesh(filename=mesh_path, scale=scale)
            else:
                raise ValueError(f"Unknown geometry type: {urdf_geometry}")

        def build_material_from_urdf(urdf_material: yourdfpy.urdf.Material) -> Material:
            return Material(
                name=urdf_material.name,
                color=urdf_material.color.rgba if urdf_material.color is not None else None,
                texture=urdf_material.texture.filename if urdf_material.texture is not None else None,
            )

        def build_link_from_urdf(link_spec: yourdfpy.urdf.Link, mesh_dir: str) -> Link:
            link = Link(name=link_spec.name)
            for visual_spec in link_spec.visuals:
                assert visual_spec.geometry is not None, f"Visual {visual_spec.name} has no geometry"
                if visual_spec.origin is None:
                    origin = np.eye(4, dtype=np.float32)
                else:
                    origin = visual_spec.origin
                visual = Visual(
                    origin=origin,
                    geometry=build_geometry_from_urdf(visual_spec.geometry, mesh_dir=mesh_dir),
                    name=visual_spec.name,
                    material=build_material_from_urdf(visual_spec.material)
                    if visual_spec.material is not None
                    else None,
                )
                link.visuals.append(visual)
            for collision_spec in link_spec.collisions:
                if collision_spec.origin is None:
                    origin = np.eye(4, dtype=np.float32)
                else:
                    origin = collision_spec.origin
                collision = Collision(
                    origin=origin,
                    geometry=build_geometry_from_urdf(collision_spec.geometry, mesh_dir=mesh_dir),
                    name=collision_spec.name,
                )
                link.collisions.append(collision)
            return link

        if self.config.urdf_path is None:
            raise ValueError("URDF path must be provided")
        if self.config.mesh_dir is None:
            self.config.mesh_dir = os.path.dirname(self.config.urdf_path)

        # parse URDF
        urdf = yourdfpy.URDF.load(
            self.config.urdf_path,
            load_meshes=False,
            build_scene_graph=False,
            mesh_dir=self.config.mesh_dir,
            filename_handler=yourdfpy.filename_handler_null,
        )

        # build joint maps
        joint_map: dict[str, Joint] = {
            joint_name: build_joint_from_urdf(joint_spec) for joint_name, joint_spec in urdf.joint_map.items()
        }
        # infer base link name
        link_names: list[str] = list(urdf.link_map.keys())
        for joint in joint_map.values():
            if joint.child_link_name in link_names:
                link_names.remove(joint.child_link_name)
        if len(link_names) != 1:
            raise ValueError(f"Expected exactly one base link, got {len(link_names)}")
        base_link_name = link_names[0]
        # add a root  joint for base link
        joint_map[ROOT_JOINT_NAME] = Joint(
            name=ROOT_JOINT_NAME,
            type=JointType.ROOT,
            origin=torch.eye(4, dtype=torch.float32, device=self.config.device),
            axis=torch.zeros(3, dtype=torch.float32, device=self.config.device),
            limit=torch.tensor([0.0, 0.0], dtype=torch.float32, device=self.config.device),
            parent_link_name="",
            child_link_name=base_link_name,
        )

        # build link maps
        link_map = {
            link_name: build_link_from_urdf(link_spec, mesh_dir=self.config.mesh_dir)
            for link_name, link_spec in urdf.link_map.items()
        }
        # set parent joint names for links
        for joint_name, joint in joint_map.items():
            link_map[joint.child_link_name].set_joint_name(joint_name)

        return joint_map, link_map

    def parse_mjcf(self) -> tuple[dict[str, Joint], dict[str, Link]]:
        def build_geometry_from_mjcf(geom_spec) -> Geometry:
            if geom_spec.type == "box":
                return Box(size=geom_spec.size * 2)
            elif geom_spec.type == "cylinder":
                raise NotImplementedError("Cylinder geometry is not supported in MJCF")
            elif geom_spec.type == "mesh" or geom_spec.mesh is not None:
                scale_spec = geom_spec.size
                if isinstance(scale_spec, float):
                    scale: list[float] = [scale_spec, scale_spec, scale_spec]
                elif isinstance(scale_spec, np.ndarray):
                    scale = scale_spec.tolist()
                elif scale_spec is None:
                    scale = [1.0, 1.0, 1.0]
                else:
                    raise ValueError(f"Unknown scale type: {scale_spec}")
                mesh = trimesh.load(
                    trimesh.util.wrap_as_stream(geom_spec.mesh.file.contents),
                    file_type=geom_spec.mesh.file.extension.replace(".", ""),
                    force="mesh",
                    process=False,
                )
                return Mesh(vertices=np.asarray(mesh.vertices), faces=np.asarray(mesh.faces), scale=scale)  # type: ignore
            elif geom_spec.type == "capsule":
                return Capsule(radius=geom_spec.size[0], length=geom_spec.size[1] * 2)
            elif geom_spec.type == "sphere" or geom_spec.type is None:
                return Sphere(radius=geom_spec.size)
            else:
                raise ValueError(f"Unknown geometry type: {geom_spec.type}")

        def build_pose_from_mjcf(quat: np.ndarray | None, pos: np.ndarray | None) -> np.ndarray:
            rot_mat = quaternion_to_matrix(quat) if quat is not None else np.eye(3)
            return rot_tl_to_tf_mat(rot_mat=rot_mat, tl=pos)

        def build_link_from_mjcf(link_spec) -> Link:
            link = Link(name=link_spec.name)
            for geom in link_spec.geom:
                origin = build_pose_from_mjcf(geom.quat, geom.pos)
                visual = Visual(origin=origin, geometry=build_geometry_from_mjcf(geom), name=geom.name)
                collision = Collision(origin=origin, geometry=build_geometry_from_mjcf(geom), name=geom.name)
                link.visuals.append(visual)
                link.collisions.append(collision)
            return link

        def mjcf_str_to_joint_type(joint_type_str: str | None = "hinge") -> JointType:
            # https://mujoco.readthedocs.io/en/stable/XMLreference.html#body-joint
            if joint_type_str == "fixed":
                return JointType.FIXED
            elif joint_type_str == "slide":
                return JointType.PRISMATIC
            elif joint_type_str == "hinge" or joint_type_str is None:
                return JointType.REVOLUTE
            else:
                raise ValueError(f"Unknown joint type: {joint_type_str}")

        def build_joint_from_mjcf(joint_spec, origin: np.ndarray, parent_link_name: str, child_link_name: str) -> Joint:
            joint_type = mjcf_str_to_joint_type(joint_spec.type)
            if joint_spec.range is not None:
                limit = torch.tensor(joint_spec.range, dtype=torch.float32, device=self.config.device)
            else:
                limit = None
            if joint_spec.axis is None:
                axis = torch.tensor([0.0, 0.0, 1.0], dtype=torch.float32, device=self.config.device)
            else:
                axis = torch.tensor(joint_spec.axis, dtype=torch.float32, device=self.config.device)

            return Joint(
                name=joint_spec.name,
                type=joint_type,
                origin=torch.from_numpy(origin).to(device=self.config.device, dtype=torch.float32),
                axis=axis,
                limit=limit,
                parent_link_name=parent_link_name,
                child_link_name=child_link_name,
            )

        if self.config.mjcf_path is None:
            raise ValueError("MJCF path must be provided")

        try:
            import dm_control.mjcf
        except ImportError:
            raise ImportError("dm_control is required to parse MJCF files, please install by `pip install dm_control`")

        mjcf = dm_control.mjcf.from_path(self.config.mjcf_path, assets=self.config.mjcf_assets)
        base_link_spec = mjcf.worldbody.body[0]  # type: ignore
        base_link_name = str(base_link_spec.name)

        link_map: dict[str, Link] = {}
        joint_map: dict[str, Joint] = {}
        link_specs = [(base_link_spec, "")]
        while link_specs:
            link_spec, parent_link_name = link_specs.pop()
            link_map[link_spec.name] = build_link_from_mjcf(link_spec)
            if len(link_spec.joint) > 0:
                if len(link_spec.joint) > 1:
                    raise ValueError(f"Link {link_spec.name} has multiple joints")
                joint_map[link_spec.joint[0].name] = build_joint_from_mjcf(
                    link_spec.joint[0],
                    origin=build_pose_from_mjcf(link_spec.quat, link_spec.pos),
                    parent_link_name=parent_link_name,
                    child_link_name=link_spec.name,
                )
                link_map[link_spec.name].set_joint_name(link_spec.joint[0].name)
            link_specs.extend([(child_link, link_spec.name) for child_link in link_spec.body])
        # add a root joint for base link
        joint_map[ROOT_JOINT_NAME] = Joint(
            name=ROOT_JOINT_NAME,
            type=JointType.ROOT,
            origin=torch.eye(4, dtype=torch.float32, device=self.config.device),
            axis=torch.zeros(3, dtype=torch.float32, device=self.config.device),
            limit=torch.tensor([0.0, 0.0], dtype=torch.float32, device=self.config.device),
            parent_link_name="",
            child_link_name=base_link_name,
        )
        link_map[base_link_name].set_joint_name(ROOT_JOINT_NAME)
        return joint_map, link_map

    def compute_compact_tensor(self) -> tuple[Tensor, list[str]]:
        """
        compact tensor spec (shape: 1 + num_chains + sum(chain_lengths) * 16)
        1. num_unique_links (shape: 1)
        2. num_chains (shape: 1)
        3. chain_lengths (shape: num_chains)
        4. chain_links (shape: sum(chain_lengths) x 16)

        link/link's parent_joint spec (shape: 19)
        - joint_type (shape: 1)
        - active_joint_index (shape: 1, data range: [-1, num_dofs - 1], -1 for non-active joint)
        - parent_link_index_in_chain (shape: 1, data range: [-1, chain_lengths - 1], -1 for base link)
        - link_index_in_compact_tensor (shape: 1, data range: [-1, num_unique_links - 1], -1 for redundant link)
        - joint_origin (shape: 12)
        - joint_axis (shape: 3)
        """
        chain_links, link_order = [], []
        for link_name in self.link_names:
            joint_name = self.link_map[link_name].joint_name
            joint = self.joint_map[joint_name]
            joint_type = torch.tensor([joint.type.value], dtype=torch.float32)
            if joint_name in self.active_joint_names:
                active_joint_index = torch.tensor([self.active_joint_names.index(joint_name)], dtype=torch.float32)
            else:
                active_joint_index = torch.tensor([-1], dtype=torch.float32)
            if link_name == self.base_link_name:
                parent_link_index = torch.tensor([-1], dtype=torch.float32)
            else:
                parent_link_index = torch.tensor([self.link_names.index(joint.parent_link_name)], dtype=torch.float32)
            joint_origin = joint.origin[:3].reshape(-1)
            if link_name not in link_order:
                link_order.append(link_name)
                link_index_in_order = torch.tensor([len(link_order) - 1], dtype=torch.float32)
            else:
                link_index_in_order = torch.tensor([-1], dtype=torch.float32)
            joint_tensor = torch.cat(
                [
                    joint_type,
                    active_joint_index,
                    parent_link_index,
                    link_index_in_order,
                    joint_origin,
                    joint.axis,
                ],
                dim=0,
            )
            if joint_tensor.shape[0] != JOINT_SPEC_TENSOR_SIZE:
                raise ValueError(f"Unexpected joint tensor shape: {joint_tensor.shape}")
            chain_links.append(joint_tensor)

        num_unique_links = torch.tensor([len(link_order)], dtype=torch.float32)
        compact_tensor = torch.cat([num_unique_links] + chain_links, dim=0).to(device=self.config.device)
        compact_tensor.requires_grad_(False)
        return compact_tensor, link_order

    def get_link_mesh_verts_faces(
        self, mode: Literal["visual", "collision"] = "collision"
    ) -> tuple[list[Tensor], list[Tensor]]:
        meshes = [self.link_map[link_name].get_trimesh(mode=mode) for link_name in self.link_names]
        verts = [torch.from_numpy(mesh.vertices).to(device=self.config.device, dtype=torch.float32) for mesh in meshes]
        faces = [torch.from_numpy(mesh.faces).to(device=self.config.device, dtype=torch.long) for mesh in meshes]
        return verts, faces

    @staticmethod
    def _build_joint_transform(joint: Joint, joint_value: Tensor | None = None) -> Tensor:
        if joint.type == JointType.REVOLUTE:
            if joint_value is None:
                raise ValueError("Joint value must be provided for revolute joint.")
            c = torch.cos(joint_value)
            s = torch.sin(joint_value)
            t = 1 - c
            x, y, z = joint.axis
            rot_mat = torch.stack(
                [
                    t * x * x + c,
                    t * x * y - s * z,
                    t * x * z + s * y,
                    t * x * y + s * z,
                    t * y * y + c,
                    t * y * z - s * x,
                    t * x * z - s * y,
                    t * y * z + s * x,
                    t * z * z + c,
                ],
                dim=-1,
            ).reshape(-1, 3, 3)
            tf_mat = torch.eye(4, device=rot_mat.device, dtype=rot_mat.dtype).repeat(rot_mat.shape[:-2] + (1, 1))
            tf_mat[..., :3, :3] = rot_mat
            return tf_mat
        elif joint.type == JointType.PRISMATIC:
            if joint_value is None:
                raise ValueError("Joint value must be provided for revolute joint.")
            x, y, z = joint.axis
            tl = torch.stack([x * joint_value, y * joint_value, z * joint_value], dim=-1).reshape(-1, 3)
            tf_mat = torch.eye(4, device=tl.device, dtype=tl.dtype).repeat(tl.shape[:-1] + (1, 1))
            tf_mat[..., :3, -1] = tl
            return tf_mat
        elif joint.type == JointType.FIXED:
            return torch.eye(4, dtype=torch.float32, device=joint.axis.device)
        else:
            raise NotImplementedError(f"Joint type {joint.type} is not supported.")

    def forward_kinematics(self, joint_values: Tensor, root_poses: Tensor | None = None) -> Tensor:
        batch_size = joint_values.shape[0]

        if root_poses is None:
            root_poses = torch.eye(4, device=joint_values.device, dtype=joint_values.dtype)
            root_poses = root_poses.unsqueeze(0).expand(batch_size, 4, 4)
        else:
            if root_poses.shape != (batch_size, 4, 4):
                raise ValueError(
                    f"Root poses shape {root_poses.shape} is not compatible with joint values shape {joint_values.shape}"
                )

        if self.joint_limits is not None:
            joint_values = torch.clamp(joint_values, self.joint_limits[:, 0], self.joint_limits[:, 1])

        link_poses: list[Tensor] = []
        for link_name in self.link_names:
            joint_name = self.link_map[link_name].joint_name
            joint = self.joint_map[joint_name]
            if joint.type == JointType.ROOT:
                glb_joint_pose = root_poses
            else:
                parent_joint_pose = link_poses[self.link_names.index(joint.parent_link_name)]
                if joint_name in self.active_joint_names:
                    local_joint_tf = self._build_joint_transform(
                        joint, joint_values[:, self.active_joint_names.index(joint_name)]
                    )
                else:
                    local_joint_tf = self._build_joint_transform(joint)
                glb_joint_pose = torch.matmul(torch.matmul(parent_joint_pose, joint.origin), local_joint_tf)
            link_poses.append(glb_joint_pose)
        return torch.stack(link_poses, dim=1)  # [batch, num_links, 4, 4]


# os.environ["TORCH_CUDA_ARCH_LIST"] = current_cuda_arch()

# name = "fastdev_kinematics"
# build_dir = _get_build_directory(name, verbose=False)
# extra_include_paths: list[str] = [FDEV_CSRC_ROOT]
# extra_cflags = ["-O3", "-DWITH_CUDA"]
# extra_cuda_cflags = ["-O3", "-DWITH_CUDA"]

# C: Any = None

# sources = []
# for ext in ["cpp", "cu"]:
#     sources.extend(glob.glob(os.path.join(FDEV_CSRC_ROOT, "kinematics", f"**/*.{ext}"), recursive=True))


# # if failed, try with JIT compilation
# if cuda_toolkit_available():
#     if os.listdir(build_dir) != []:
#         # If the build exists, we assume the extension has been built
#         # and we can load it.
#         with Timer("Loading extension"):
#             C = load(
#                 name=name,
#                 sources=sources,
#                 extra_cflags=extra_cflags,
#                 extra_cuda_cflags=extra_cuda_cflags,
#                 extra_include_paths=extra_include_paths,
#             )
#     else:
#         # Build from scratch. Remove the build directory just to be safe: pytorch jit might stuck
#         # if the build directory exists.
#         shutil.rmtree(build_dir, ignore_errors=True)
#         with Timer("Building extension"), console.status(
#             "[bold yellow]Building extension (This may take a few minutes the first time)",
#             spinner="bouncingBall",
#         ):
#             C = load(
#                 name=name,
#                 sources=sources,
#                 extra_cflags=extra_cflags,
#                 extra_cuda_cflags=extra_cuda_cflags,
#                 extra_include_paths=extra_include_paths,
#             )
# else:
#     console.print("[yellow]No CUDA toolkit found. NeuralTeleop will be disabled.[/yellow]")


# class Kinematics(Function):
#     @staticmethod
#     def forward(
#         ctx,
#         kin_config_tensor: Tensor,
#         joint_values: Tensor,
#         root_poses: Tensor,
#     ):
#         return C.kinematics_forward(kin_config_tensor, joint_values, root_poses)
#     @staticmethod
#     def backward(ctx, grad_output):
#         pass


__all__ = ["RobotModelConfig", "RobotModel"]
