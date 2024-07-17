from __future__ import annotations

import glob
import os
import shutil
from typing import Any

import numpy as np
import torch
import trimesh
from torch import Tensor
from torch.types import Device
from torch.utils.cpp_extension import _get_build_directory, load
from trimesh import Trimesh

from fastdev.constants import FDEV_CSRC_ROOT
from fastdev.utils import Timer
from fastdev.utils.cuda import cuda_toolkit_available, current_cuda_arch
from fastdev.utils.struct_utils import list_to_packed
from fastdev.utils.tui import console

os.environ["TORCH_CUDA_ARCH_LIST"] = current_cuda_arch()

name = "fastdev_point_mesh"
build_dir = _get_build_directory(name, verbose=False)
extra_include_paths: list[str] = [FDEV_CSRC_ROOT]
extra_cflags = ["-O3"]
extra_cuda_cflags = ["-O3"]

C: Any = None

sources = []
sources.extend(glob.glob(os.path.join(FDEV_CSRC_ROOT, "point_mesh", "**/*.cpp"), recursive=True))

if cuda_toolkit_available():
    extra_cflags.append("-DWITH_CUDA")
    extra_cuda_cflags.append("-DWITH_CUDA")
    sources.extend(glob.glob(os.path.join(FDEV_CSRC_ROOT, "point_mesh", "**/*.cu"), recursive=True))

try:
    if os.listdir(build_dir) != []:
        # If the build exists, we assume the extension has been built
        # and we can load it.
        with Timer("Loading fastdev.geom extension"):
            C = load(
                name=name,
                sources=sources,
                extra_cflags=extra_cflags,
                extra_cuda_cflags=extra_cuda_cflags,
                extra_include_paths=extra_include_paths,
            )
    else:
        # Build from scratch. Remove the build directory just to be safe: pytorch jit might stuck
        # if the build directory exists.
        shutil.rmtree(build_dir, ignore_errors=True)
        with Timer("Building fastdev.geom extension"), console.status(
            "[bold yellow]Building fastdev.geom extension (This may take a few minutes the first time)",
            spinner="bouncingBall",
        ):
            C = load(
                name=name,
                sources=sources,
                extra_cflags=extra_cflags,
                extra_cuda_cflags=extra_cuda_cflags,
                extra_include_paths=extra_include_paths,
            )
except Exception as e:
    console.print(f"[bold red]Error building fastdev.geom extension: {e}")
    console.print("The geom module will not be available.")


class Meshes:
    """Meshes.

    Examples:
        >>> # doctest: +SKIP
        >>> meshes = Meshes.from_trimesh(trimesh.creation.box((1.0, 1.0, 1.0)))
        >>> query_pts = torch.tensor([[[1.0, 0.0, 0.0], [0.1, 0.0, 0.0]]])
        >>> pts, normals, dists2 = meshes.query_closest_points(query_pts)
        >>> torch.allclose(pts[0, 0], torch.tensor([0.5, 0.0, 0.0]))
        True
        >>> torch.allclose(dists2[0, 1], torch.tensor(0.16))
        True
    """

    _INTERNAL_TENSORS: list[str] = [
        "_verts_packed",
        "_verts_packed_to_mesh_idx",
        "_mesh_to_verts_packed_first_idx",
        "_num_verts_per_mesh",
        "_faces_packed",
        "_faces_packed_to_mesh_idx",
        "_mesh_to_faces_packed_first_idx",
        "_num_faces_per_mesh",
    ]

    def __init__(self, verts: Tensor | list[Tensor], faces: Tensor | list[Tensor], device: Device = None):
        if isinstance(verts, list) and isinstance(faces, list):
            self._verts_list, self._faces_list = verts, faces
        elif isinstance(verts, Tensor) and isinstance(faces, Tensor):
            self._verts_list, self._faces_list = [verts], [faces]
        else:
            raise ValueError("verts and faces should be both list or both Tensor.")

        if device is not None:
            self._verts_list = [v.to(device=device) for v in self._verts_list]
            self._faces_list = [f.to(device=device) for f in self._faces_list]
        self._device = self._verts_list[0].device

        self._num_verts_per_mesh = torch.tensor(
            [v.shape[0] for v in self._verts_list], dtype=torch.long, device=self._device
        )
        self._num_faces_per_mesh = torch.tensor(
            [f.shape[0] for f in self._faces_list], dtype=torch.long, device=self._device
        )

        verts_list_to_packed = list_to_packed(self._verts_list)
        self._verts_packed = verts_list_to_packed[0]
        if not torch.allclose(self._num_verts_per_mesh, verts_list_to_packed[1]):
            raise ValueError("The number of verts per mesh should be consistent.")
        self._mesh_to_verts_packed_first_idx = verts_list_to_packed[2]
        self._verts_packed_to_mesh_idx = verts_list_to_packed[3]

        faces_list_to_packed = list_to_packed(self._faces_list)
        faces_packed = faces_list_to_packed[0]
        if not torch.allclose(self._num_faces_per_mesh, faces_list_to_packed[1]):
            raise ValueError("The number of faces per mesh should be consistent.")
        self._mesh_to_faces_packed_first_idx = faces_list_to_packed[2]
        self._faces_packed_to_mesh_idx = faces_list_to_packed[3]
        faces_packed_offset = self._mesh_to_verts_packed_first_idx[self._faces_packed_to_mesh_idx]
        self._faces_packed = faces_packed + faces_packed_offset.view(-1, 1)

    @staticmethod
    def from_files(filenames: str | list[str], device: Device = None) -> Meshes:
        if isinstance(filenames, str):
            filenames = [filenames]
        verts, faces = [], []
        for filename in filenames:
            mesh: Trimesh = trimesh.load(filename, force="mesh", process=False)  # type: ignore
            verts.append(torch.from_numpy(mesh.vertices.astype(np.float32)))
            faces.append(torch.from_numpy(mesh.faces))
        return Meshes(verts, faces, device=device)

    @staticmethod
    def from_trimesh(mesh: Trimesh | list[Trimesh], device: Device = None) -> Meshes:
        if isinstance(mesh, Trimesh):
            mesh = [mesh]
        verts, faces = [], []
        for m in mesh:
            verts.append(torch.from_numpy(m.vertices.astype(np.float32)))
            faces.append(torch.from_numpy(m.faces))
        return Meshes(verts, faces, device=device)

    def query_closest_points(self, padded_query_points: Tensor) -> tuple[Tensor, Tensor, Tensor]:
        """Query closest points on mesh.

        Args:
            padded_query_points (Tensor): Padded query points, shape (B, N, 3). B is the same as the number of meshes.

        Returns:
            tuple[Tensor, Tensor, Tensor]: Closest points, normals and squared distances.
        """
        points_packed = padded_query_points.reshape(-1, 3)
        points_first_idx = torch.arange(0, points_packed.shape[0], padded_query_points.shape[1], device=self._device)
        max_points_per_batch = padded_query_points.shape[1]
        closest_pts, normals, dist2 = C.closest_point_on_mesh(
            points_packed,
            points_first_idx,
            self._verts_packed[self._faces_packed],
            self._mesh_to_faces_packed_first_idx,
            max_points_per_batch,
            5e-3,
        )
        return (
            closest_pts.reshape(padded_query_points.shape),
            normals.reshape(padded_query_points.shape),
            dist2.reshape(padded_query_points.shape[:-1]),
        )

    def clone(self) -> Meshes:
        verts_list = self._verts_list
        faces_list = self._faces_list
        new_verts_list = [v.clone() for v in verts_list]
        new_faces_list = [f.clone() for f in faces_list]
        other = self.__class__(verts=new_verts_list, faces=new_faces_list)
        for k in self._INTERNAL_TENSORS:
            v = getattr(self, k)
            if torch.is_tensor(v):
                setattr(other, k, v.clone())
        return other

    def to(self, device: Device) -> Meshes:
        for i in range(len(self._verts_list)):
            self._verts_list[i] = self._verts_list[i].to(device=device)
            self._faces_list[i] = self._faces_list[i].to(device=device)
        other = self.clone()
        other._verts_list = [v.to(device=device) for v in self._verts_list]
        other._faces_list = [f.to(device=device) for f in self._faces_list]
        for k in self._INTERNAL_TENSORS:
            v = getattr(self, k)
            if torch.is_tensor(v):
                setattr(other, k, v.to(device=device))
        return other


if __name__ == "__main__":
    from fastdev import Timer
    from fastdev.io.download import cached_local_path

    mesh_path = cached_local_path(
        "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/stanford-bunny.obj",
        rel_cache_path="common-meshes/bunny.obj",
    )
    with Timer("Creating meshes"):
        meshes = Meshes.from_files(mesh_path, device="cuda")

__all__ = ["Meshes"]
