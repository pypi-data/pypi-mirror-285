# mypy: disable-error-code="empty-body"
from typing import Literal, Optional, Tuple, Union, overload

import numpy as np
import torch
from numpy import ndarray
from torch import Tensor

from fastdev.utils.dispatch import singledispatch


@overload
@singledispatch()
def transform(pts: Tensor, tf_mat: Tensor) -> Tensor:
    if pts.ndim != tf_mat.ndim:
        raise ValueError("The dimension number of pts and tf_mat should be the same.")
    homo_pts = to_homo(pts)
    # `homo_pts @ tf_mat.T` or `(tf_mat @ homo_pts.T).T`
    new_pts = torch.matmul(homo_pts, torch.transpose(tf_mat, -2, -1))
    return new_pts[..., :3]


@overload
@singledispatch()
def transform(pts: ndarray, tf_mat: ndarray) -> ndarray:
    if pts.ndim != tf_mat.ndim:
        raise ValueError("The dimension number of pts and tf_mat should be the same.")

    homo_pts = to_homo(pts)
    new_pts = np.matmul(homo_pts, np.swapaxes(tf_mat, -2, -1))
    return new_pts[..., :3]


@singledispatch(is_impl=False)
def transform(pts: Union[Tensor, ndarray], tf_mat: Union[Tensor, ndarray]) -> Union[Tensor, ndarray]:
    """
    Apply a transformation matrix on a set of 3D points.

    Args:
        pts: 3D points, could be [..., N, 3]
        tf_mat: Transformation matrix, could be [..., 4, 4]

    Returns:
        Transformed pts.

    .. note::
        The dimension number of `pts` and `tf_mat` should be the same. The batch dimensions (...) are broadcasted_ (and
        thus must be broadcastable). We don't adopt the shapes [..., 3] and [..., 4, 4] because there is no real
        broadcasted vector-matrix multiplication in pytorch. [..., 3] and [..., 4, 4] will be converted to [..., 1, 3]
        and [..., 4, 4] and apply a broadcasted matrix-matrix multiplication.

    .. _broadcasted: https://pytorch.org/docs/stable/notes/broadcasting.html
    """
    ...


@overload
@singledispatch()
def rotate(pts: torch.Tensor, rot_mat: torch.Tensor) -> torch.Tensor:
    if pts.ndim != rot_mat.ndim:
        raise ValueError(
            f"The dimension number of pts and rot_mat should be the same, but got {pts.ndim=} and {rot_mat.ndim=}"
        )

    # `pts @ rot_mat.T` or `(rot_mat @ pts.T).T`
    new_pts = torch.matmul(pts, torch.transpose(rot_mat, -2, -1))
    return new_pts


@overload
@singledispatch()
def rotate(pts: np.ndarray, rot_mat: np.ndarray) -> np.ndarray:
    if pts.ndim != rot_mat.ndim:
        raise ValueError(
            f"The dimension number of pts and rot_mat should be the same, but got {pts.ndim=} and {rot_mat.ndim=}"
        )

    new_pts = np.matmul(pts, np.swapaxes(rot_mat, -2, -1))
    return new_pts


@singledispatch(is_impl=False)
def rotate(pts: Union[Tensor, ndarray], rot_mat: Union[Tensor, ndarray]) -> Union[Tensor, ndarray]:
    """
    Rotate a set of 3D points by a rotation matrix.

    Args:
        pts: 3D points, could be [..., N, 3]
        rot_mat: Rotation matrix, could be [..., 3, 3]

        The dimension number of pts and rot_mat should be the same.

    Returns:
        Rotated pts.
    """
    ...


@overload
def project(pts: torch.Tensor, intr_mat: torch.Tensor, return_depth: Literal[False] = False) -> torch.Tensor: ...


@overload
def project(
    pts: torch.Tensor, intr_mat: torch.Tensor, return_depth: Literal[True]
) -> Tuple[torch.Tensor, torch.Tensor]: ...


def project(
    pts: torch.Tensor, intr_mat: torch.Tensor, return_depth: bool = False
) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    """
    Project 3D points in the camera space to the image plane.

    Args:
        pts: 3D points, could be Nx3 or BxNx3.
        intr_mat: Intrinsic matrix, could be 3x3 or Bx3x3.

    Returns:
        pixels: the order is uv other than xy.
        depth (if return_depth): depth in the camera space.
    """
    pts = torch.clone(pts)
    new_pts = pts / pts[..., 2:3]
    new_pts = torch.matmul(new_pts, torch.transpose(intr_mat, -2, -1))

    if not return_depth:
        return new_pts[..., :2]
    else:
        return new_pts[..., :2], pts[..., 2]


def unproject(pixels, depth, intr_mat):
    """
    Unproject pixels in the image plane to 3D points in the camera space.

    Args:
        pixels: Pixels in the image plane, could be Nx2 or BxNx2. The order is uv rather than xy.
        depth: Depth in the camera space, could be N, Nx1, BxN or BxNx1.
        intr_mat: Intrinsic matrix, could be 3x3 or Bx3x3.
    Returns:
        pts: 3D points, Nx3 or BxNx3.
    """
    if depth.ndim < pixels.ndim:
        depth = depth[..., None]  # N -> Nx1, BxN -> BxNx1
    principal_point = torch.unsqueeze(intr_mat[..., :2, 2], dim=-2)  # 1x2, Bx1x2
    focal_length = torch.cat([intr_mat[..., 0:1, 0:1], intr_mat[..., 1:2, 1:2]], dim=-1)  # 1x2, Bx1x2
    xys = (pixels - principal_point) * depth / focal_length
    pts = torch.cat([xys, depth], dim=-1)
    return pts


@overload
@singledispatch()
def inverse(rot_or_tf_mat: torch.Tensor) -> torch.Tensor:
    if rot_or_tf_mat.shape[-1] == 3:  # rotation matrix
        new_mat = torch.transpose(rot_or_tf_mat, -2, -1)
    else:  # transformation matrix
        new_rot_mat = torch.transpose(rot_or_tf_mat[..., :3, :3], -2, -1)
        ori_tl = torch.unsqueeze(rot_or_tf_mat[..., :3, 3], dim=-2)  # 1x3, Bx1x3
        new_tl = torch.squeeze(-rotate(ori_tl, new_rot_mat), dim=-2)  # 3, Bx3
        new_mat = rot_tl_to_tf_mat(new_rot_mat, new_tl)
    return new_mat


@overload
@singledispatch()
def inverse(rot_or_tf_mat: ndarray) -> ndarray:
    if rot_or_tf_mat.shape[-1] == 3:
        new_mat = np.swapaxes(rot_or_tf_mat, -2, -1)
    else:
        new_rot_mat = np.swapaxes(rot_or_tf_mat[..., :3, :3], -2, -1)
        ori_tl = np.expand_dims(rot_or_tf_mat[..., :3, 3], axis=-2)
        new_tl = np.squeeze(-rotate(ori_tl, new_rot_mat), axis=-2)
        new_mat = rot_tl_to_tf_mat(new_rot_mat, new_tl)
    return new_mat


@singledispatch(is_impl=False)
def inverse(rot_or_tf_mat: Union[Tensor, ndarray]) -> Union[Tensor, ndarray]:
    """Inverse a rotation matrix or a transformation matrix. Reference_

    Args:
        rot_or_tf_mat (Union[Tensor, ndarray]): Rotation matrix (in shape [..., 3, 3]) or transformation matrix (in shape [..., 4, 4]).

    Returns:
        Union[Tensor, ndarray]: Inversed matrix.

    Examples:
        >>> import torch
        >>> tf_mat = torch.tensor([[0, 1, 0, 1], [0, 0, 1, 2], [1, 0, 0, 3], [0, 0, 0, 1]], dtype=torch.float32)
        >>> inverse(tf_mat)
        >>> torch.allclose(inverse(tf_mat) @ tf_mat, torch.eye(4))
        True
        >>> rot_mat = torch.tensor([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=torch.float32)
        >>> inverse(rot_mat)
        >>> torch.allclose(inverse(rot_mat) @ rot_mat, torch.eye(3))
        True

    .. _Reference: https://math.stackexchange.com/a/1315407/757569
    """
    ...


# Ref: https://www.scratchapixel.com/lessons/mathematics-physics-for-computer-graphics/geometry/row-major-vs-column-major-vector # noqa
def swap_major(rot_or_tf_mat: torch.Tensor) -> torch.Tensor:
    return torch.transpose(rot_or_tf_mat, -2, -1)


@overload
@singledispatch()
def rot_tl_to_tf_mat(rot_mat: torch.Tensor, tl: Optional[torch.Tensor] = None) -> torch.Tensor:
    tf_mat = torch.eye(4, device=rot_mat.device, dtype=rot_mat.dtype).repeat(rot_mat.shape[:-2] + (1, 1))
    tf_mat[..., :3, :3] = rot_mat
    if tl is not None:
        tf_mat[..., :3, 3] = tl
    return tf_mat


@overload
@singledispatch()
def rot_tl_to_tf_mat(rot_mat: ndarray, tl: Optional[ndarray] = None) -> ndarray:
    tf_mat = np.tile(np.eye(4, dtype=rot_mat.dtype), rot_mat.shape[:-2] + (1, 1))
    tf_mat[..., :3, :3] = rot_mat
    if tl is not None:
        tf_mat[..., :3, 3] = tl
    return tf_mat


@singledispatch(is_impl=False)
def rot_tl_to_tf_mat(
    rot_mat: Union[Tensor, ndarray], tl: Optional[Union[Tensor, ndarray]] = None
) -> Union[Tensor, ndarray]:
    """Build transformation matrix with rotation matrix and translation vector.

    Args:
        rot_mat (Union[Tensor, ndarray]): rotation matrix, could be [..., 3, 3]
        tl (Optional[Union[Tensor, ndarray]], optional): translation vector, could be [..., 3]. If None, translation will be 0. Defaults to None.

    Returns:
        Union[Tensor, ndarray]: transformation matrix, in shape [..., 4, 4].


    Examples:
        >>> import torch
        >>> rot_mat = torch.tensor([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=torch.float32)
        >>> tl = torch.tensor([1, 2, 3], dtype=torch.float32)
        >>> rot_tl_to_tf_mat(rot_mat, tl)
        tensor([[0., 1., 0., 1.],
                [0., 0., 1., 2.],
                [1., 0., 0., 3.],
                [0., 0., 0., 1.]])
    """
    ...


@overload
@singledispatch()
def to_homo(pts_3d: Tensor) -> Tensor:
    return torch.cat([pts_3d, torch.ones_like(pts_3d[..., :1])], dim=-1)


@overload
@singledispatch()
def to_homo(pts_3d: ndarray) -> ndarray:
    return np.concatenate([pts_3d, np.ones_like(pts_3d[..., :1])], axis=-1)


@singledispatch(is_impl=False)
def to_homo(pts_3d: Union[Tensor, ndarray]) -> Union[Tensor, ndarray]:
    """
    Convert Cartesian 3D points to Homogeneous 4D points.

    Args:
      pts_3d: 3D points in Cartesian coord, could be ...x3.
    Returns:
      ...x4 points in the Homogeneous coord.
    """
    ...


def expand_tf_mat(tf_mat: torch.Tensor) -> torch.Tensor:
    """
    Expand transformation matrix to [..., 4, 4].

    Args:
        tf_mat: transformation matrix, could be ...x3x4 or ...x4x4.

    Returns:
        tf_mat, expanded transformation matrix.
    """
    if tf_mat.shape[-2:] == (3, 4):
        tf_mat = torch.cat(
            [
                tf_mat,
                torch.tensor([0.0, 0.0, 0.0, 1.0], dtype=tf_mat.dtype, device=tf_mat.device).repeat(
                    tf_mat.shape[:-2] + (1, 1)
                ),
            ],
            dim=-2,
        )
    return tf_mat


__all__ = [
    "transform",
    "rotate",
    "project",
    "unproject",
    "inverse",
    "swap_major",
    "rot_tl_to_tf_mat",
    "to_homo",
    "expand_tf_mat",
]
