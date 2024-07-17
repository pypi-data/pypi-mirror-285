import numpy as np
import torch
from fastdev.xform import rot_tl_to_tf_mat, transform
from packaging.version import Version


def test_transforms():
    pts = torch.tensor([[1, 2, 3], [4, 5, 6]], dtype=torch.float32)
    rot_mat = torch.tensor([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=torch.float32)
    tl = torch.tensor([1, 2, 3], dtype=torch.float32)
    tf_mat = rot_tl_to_tf_mat(rot_mat, tl)

    new_pts = transform(pts, tf_mat)

    tgt_pts = torch.tensor([[3, 5, 4], [6, 8, 7]], dtype=torch.float32)
    assert torch.allclose(new_pts, tgt_pts)

    new_pts = transform(pts.numpy(), tf_mat.numpy())
    assert torch.allclose(torch.tensor(new_pts), tgt_pts)

    new_pts = transform(pts[None], tf_mat[None])[0]
    assert torch.allclose(new_pts, tgt_pts)

    dtype = torch.float16 if Version(torch.__version__) > Version("2.0.0") else torch.float64
    new_pts = transform(pts.to(dtype=dtype), tf_mat.to(dtype=dtype))
    assert torch.allclose(new_pts, tgt_pts.to(dtype=dtype))
    assert new_pts.dtype == dtype


def test_rot_tl_to_tf_mat():
    rot_mat = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=np.float32)
    tf_mat = rot_tl_to_tf_mat(rot_mat)
    assert tf_mat.shape == (4, 4)
    assert np.allclose(tf_mat, np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], dtype=np.float32))

    tl = np.array([1, 2, 3], dtype=np.float32)
    tf_mat = rot_tl_to_tf_mat(rot_mat, tl)
    assert tf_mat.shape == (4, 4)
    assert np.allclose(tf_mat, np.array([[0, 1, 0, 1], [0, 0, 1, 2], [1, 0, 0, 3], [0, 0, 0, 1]], dtype=np.float32))

    rot_mat = np.random.rand(1, 3, 3).astype(np.float32)
    tf_mat = rot_tl_to_tf_mat(rot_mat)
    assert tf_mat.shape == (1, 4, 4)
    assert np.allclose(tf_mat[..., :3, :3], rot_mat)

    rot_mat = torch.tensor([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=torch.float32)
    tf_mat = rot_tl_to_tf_mat(rot_mat)
    assert tf_mat.shape == (4, 4)
    assert torch.allclose(
        tf_mat, torch.tensor([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], dtype=torch.float32)
    )

    tl = torch.tensor([1, 2, 3], dtype=torch.float32)
    tf_mat = rot_tl_to_tf_mat(rot_mat, tl)
    assert tf_mat.shape == (4, 4)
    assert torch.allclose(
        tf_mat, torch.tensor([[0, 1, 0, 1], [0, 0, 1, 2], [1, 0, 0, 3], [0, 0, 0, 1]], dtype=torch.float32)
    )

    rot_mat = torch.rand((1, 3, 3), dtype=torch.float32)
    tf_mat = rot_tl_to_tf_mat(rot_mat)
    assert tf_mat.shape == (1, 4, 4)
    assert torch.allclose(tf_mat[..., :3, :3], rot_mat)


if __name__ == "__main__":
    test_rot_tl_to_tf_mat()
