import pytest
import torch
import trimesh
from fastdev.geom import Meshes


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is not available")
def test_query_closest_points():
    box = trimesh.creation.box((1, 1, 1))
    meshes = Meshes.from_trimesh(box)
    query_pts = torch.tensor([[[1.0, 0.0, 0.0], [0.1, 0.0, 0.0]]])
    pts, normals, dists2 = meshes.query_closest_points(query_pts)
    assert torch.allclose(pts[0], torch.tensor([[0.5, 0.0, 0.0], [0.5, 0.0, 0.0]]))
    assert torch.allclose(normals[0], torch.tensor([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]))
    assert torch.allclose(dists2[0], torch.tensor([0.25, 0.16]))

    sdf2 = ((torch.sum((query_pts[0] - pts[0]) * normals[0], dim=-1) > 0) * 2.0 - 1.0) * dists2[0]
    assert torch.allclose(sdf2, torch.tensor([0.25, -0.16]))

    if torch.cuda.is_available():
        device = torch.device("cuda")
        meshes = Meshes.from_trimesh(box, device=device)
        query_pts = torch.tensor([[[1.0, 0.0, 0.0], [0.1, 0.0, 0.0]]], device=device)
        pts, normals, dists2 = meshes.query_closest_points(query_pts)
        torch.allclose(pts[0], torch.tensor([[0.5, 0.0, 0.0], [0.5, 0.0, 0.0]], device=device))
        torch.allclose(normals[0], torch.tensor([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]], device=device))
        torch.allclose(dists2[0], torch.tensor([0.25, 0.16], device=device))
