import numpy as np
import torch
from torch import Tensor
from torch.nn import functional as F

COMMON_COORDS = {
    "opencv": "x: right, y: down, z: front",
    "opengl": "x: right, y: up, z: back",
    "pytorch3d": "x: left, y: up, z: front",
    "sapien": "x: front, y: left, z: up",
}


def coord_conversion(rule="opencv -> opengl", check_handness=True):
    """
    Construct a rotation matrix based on a given rule.

    Following rules are equivalent:
        - "x: right, y: down, z: front -> x: right, y: up, z: back"
        - "right, down, front -> right, up, back"
        - "opencv -> opengl"
        - "x, -y, -z"

    Args:
        rule: rule string
        return_tensor: if True return torch.Tensor, else return np.ndarray
        check_handness: if True check if the handness of the rotation matrix is correct

    Returns:
        rot_mat
    """
    if "->" in rule:
        # replace_list = [("backward", "back"), ("forward", "front")]
        # rule = [rule.replace(*item) for item in replace_list][0]
        coords = rule.split("->")
        coords = [coord.strip().lower() for coord in coords]
        coords = [COMMON_COORDS.get(coord, coord) for coord in coords]

        for idx, coord in enumerate(coords):
            if "x" in coord:
                dirs = {item.split(":")[0]: item.split(":")[1] for item in coord.split(",")}
                dirs = {k.strip(): v.strip() for k, v in dirs.items()}
                dirs = [dirs[axis] for axis in ["x", "y", "z"]]
                coords[idx] = dirs  # type: ignore
            else:
                coords[idx] = [x.strip() for x in coord.split(",")]  # type: ignore

        src_coord, dst_coord = coords

        opp_dirs = {
            "left": "right",
            "right": "left",
            "up": "down",
            "down": "up",
            "front": "back",
            "back": "front",
        }
        src_axes = [
            ["x", "y", "z"][src_coord.index(dir)]
            if dir in src_coord
            else "-" + ["x", "y", "z"][src_coord.index(opp_dirs[dir])]
            for dir in dst_coord
        ]
    else:
        src_axes = rule.split(",")
        src_axes = [axis.strip().lower() for axis in src_axes]

    negs = [-1 if "-" in axis else 1 for axis in src_axes]
    axes = [["x", "y", "z"].index(axis.replace("-", "")) for axis in src_axes]
    rot_mat = np.zeros((3, 3), np.float32)
    rot_mat[np.arange(3), axes] = negs

    if check_handness:
        if np.linalg.det(rot_mat) < 0:
            raise RuntimeWarning("The rotation matrix is not right-hand.")

    return rot_mat


def compose_intr_mat(fu: float, fv: float, cu: float, cv: float, skew: float = 0.0) -> np.ndarray:
    """
    Args:
        fu: horizontal focal length (width)
        fv: vertical focal length (height)
        cu: horizontal principal point (width)
        cv: vertical principal point (height)
        skew: skew coefficient, default to 0
    """
    intr_mat = np.array([[fu, skew, cu], [0.0, fv, cv], [0.0, 0.0, 1.0]], dtype=np.float32)
    return intr_mat


# Ref: https://github.com/facebookresearch/pytorch3d/blob/main/pytorch3d/renderer/cameras.py
def look_at_rotation(camera_position: Tensor, at: Tensor, up: Tensor) -> Tensor:
    """
    This function takes a vector `camera_position` which specifies the location of the camera in world coordinates and
    two vectors `at` and `up` which indicate the position of the object and the up directions of the world
    coordinate system respectively.

    The output is a rotation matrix representing the rotation from camera coordinates to world coordinates.

    We use the OpenGL coordinate in this function, i.e. x -> right, y -> up, z -> backward.
    Hence, z_axis: pos - at, x_axis: cross(up, z_axis), y_axis: cross(z_axis, x_axis)

    Note that our implementation differs from pytorch3d.
        1. our matrix is in the OpenGL coordinate
        2. our matrix is column-major
        3. our matrix is camera-to-world

    Args:
        camera_position: position of the camera in world coordinates
        at: position of the object in world coordinates
        up: vector specifying the up direction in the world coordinate frame.
    The input camera_position, at and up can each be a
        - torch.tensor of shape (3) or (N, 3)
    Returns:
        R: rotation matrices of shape (3, 3) or (N, 3, 3)
    """
    dtype, device = camera_position.dtype, camera_position.device
    at, up = torch.broadcast_to(at, camera_position.shape), torch.broadcast_to(up, camera_position.shape)
    z_axis = F.normalize(camera_position - at, eps=1e-5, dim=-1)
    x_axis = F.normalize(torch.cross(up, z_axis, dim=-1), eps=1e-5, dim=-1)
    y_axis = F.normalize(torch.cross(z_axis, x_axis, dim=-1), eps=1e-5, dim=-1)
    is_close = torch.isclose(x_axis, torch.tensor(0.0, dtype=dtype, device=device), atol=5e-3)
    is_close = is_close.all(dim=-1, keepdim=True)
    if is_close.any():
        replacement = F.normalize(torch.cross(y_axis, z_axis, dim=-1), eps=1e-5)
        x_axis = torch.where(is_close, replacement, x_axis)
    rot_mat = torch.cat((x_axis[..., None, :], y_axis[..., None, :], z_axis[..., None, :]), dim=-2)
    return rot_mat.transpose(-2, -1)


__all__ = ["coord_conversion", "compose_intr_mat", "look_at_rotation"]
