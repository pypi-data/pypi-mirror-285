import torch
from fastdev.robo.robot_model import RobotModel, RobotModelConfig


def test_robot_model():
    device = "cpu"
    robot_model = RobotModel(RobotModelConfig(urdf_path="assets/robot_description/panda.urdf", device=device))
    assert robot_model.num_dofs == 9
    joint_values = torch.tensor([[0.1, 0.2, 0.3, -0.5, 0.1, 0.2, 0.3, 0.02, 0.02]], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)
    link_poses = robot_model.forward_kinematics(joint_values)
    expected_link_pose = torch.tensor(
        [
            [0.4639, 0.7548, -0.4637, 0.2874],
            [0.8131, -0.5706, -0.1155, 0.1212],
            [-0.3518, -0.3235, -0.8784, 0.7954],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    assert torch.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)
    link_poses[:, -2, :3, 3].abs().sum().backward()
    joint_values_grad = joint_values.grad.clone()  # type: ignore
    expected_grad = torch.tensor(
        [[0.2193, 0.1663, 0.1481, -0.0204, 0.0791, 0.2665, -0.0185, -0.1392, 0.0000]], device=device
    )
    assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)

    if torch.cuda.is_available():
        device = "cuda"
        robot_model = RobotModel(RobotModelConfig(urdf_path="assets/robot_description/panda.urdf", device=device))
        joint_values = torch.tensor(
            [[0.1, 0.2, 0.3, -0.5, 0.1, 0.2, 0.3, 0.02, 0.02]], dtype=torch.float32, device=device
        )
        joint_values.requires_grad_(True)
        link_poses = robot_model.forward_kinematics(joint_values)
        expected_link_pose = torch.tensor(
            [
                [0.4639, 0.7548, -0.4637, 0.2874],
                [0.8131, -0.5706, -0.1155, 0.1212],
                [-0.3518, -0.3235, -0.8784, 0.7954],
                [0.0000, 0.0000, 0.0000, 1.0000],
            ],
            device=device,
        )
        assert torch.allclose(link_poses[0, -1], expected_link_pose, atol=1e-4)
        link_poses[:, -2, :3, 3].abs().sum().backward()
        joint_values_grad = joint_values.grad.clone()  # type: ignore
        expected_grad = torch.tensor(
            [[0.2193, 0.1663, 0.1481, -0.0204, 0.0791, 0.2665, -0.0185, -0.1392, 0.0000]], device=device
        )
        assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    robot_model = RobotModel(RobotModelConfig(urdf_path="assets/robot_description/kuka_iiwa.urdf", device=device))
    joint_values = torch.tensor([[0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1]], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)
    link_poses = robot_model.forward_kinematics(joint_values)
    expected_link_pose = torch.tensor(
        [
            [-0.8229, 0.5582, 0.1066, 0.1027],
            [-0.5629, -0.8263, -0.0190, 0.0048],
            [0.0775, -0.0756, 0.9941, 0.9550],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    assert torch.allclose(link_poses[0, -3], expected_link_pose, atol=1e-4)
    link_poses[:, -1, :3, :3].abs().sum().backward()
    joint_values_grad = joint_values.grad.clone()  # type: ignore
    expected_grad = torch.tensor([[0.4059, 1.4686, 0.3498, -1.4969, 0.3350, 1.4344, 0.4556]], device=device)
    assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)


def test_robot_model_mjcf():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    robot_model = RobotModel(
        RobotModelConfig(
            mjcf_path="assets/robot_description/kuka_iiwa14.xml",
            device=device,
            mjcf_assets={
                "link_0.obj": "",
                "link_1.obj": "",
                "link_2_orange.obj": "",
                "link_2_grey.obj": "",
                "link_3.obj": "",
                "band.obj": "",
                "kuka.obj": "",
                "link_4_orange.obj": "",
                "link_4_grey.obj": "",
                "link_5.obj": "",
                "link_6_orange.obj": "",
                "link_6_grey.obj": "",
                "link_7.obj": "",
            },
        )
    )
    joint_values = torch.tensor([[0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1]], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)
    link_poses = robot_model.forward_kinematics(joint_values)

    expected_link_pose = torch.tensor(
        [
            [-0.8229, 0.5582, 0.1066, 0.1027],
            [-0.5629, -0.8263, -0.0190, 0.0048],
            [0.0775, -0.0756, 0.9941, 0.9550],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    assert torch.allclose(link_poses[0, -3], expected_link_pose, atol=1e-4)

    link_poses[:, -1, :3, :3].abs().sum().backward()
    joint_values_grad = joint_values.grad.clone()  # type: ignore
    expected_grad = torch.tensor([[0.4059, 1.4686, 0.3498, -1.4969, 0.3350, 1.4344, 0.4556]], device=device)
    assert torch.allclose(joint_values_grad, expected_grad, atol=1e-4)


def test_robot_model_multi_chain():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    robot_model = RobotModel(
        RobotModelConfig(urdf_path="assets/robot_description/shadow_hand_right.urdf", device=device)
    )
    joint_values = torch.tensor([[0.15] * 24], dtype=torch.float32, device=device)
    joint_values.requires_grad_(True)

    expected_link_pose = torch.tensor(
        [
            [-0.1538, -0.7761, 0.6115, 0.0726],
            [0.9513, 0.0511, 0.3041, 0.0148],
            [-0.2672, 0.6285, 0.7305, 0.4143],
            [0.0000, 0.0000, 0.0000, 1.0000],
        ],
        device=device,
    )
    link_poses = robot_model.forward_kinematics(joint_values)
    assert torch.allclose(link_poses[0, -2], expected_link_pose, atol=1e-4)

    link_poses[:, :, :3, :3].abs().sum().backward()
    grad = joint_values.grad.clone()  # type: ignore
    # fmt: off
    expected_grad = torch.tensor(
        [[25.4212, 34.2540, -0.8519,  3.3568,  2.0163,  1.0683, -0.8519,  3.3568, 2.0163,  1.0683,  7.9247,  3.8035,
        2.2961, 1.2243,  6.8456,  7.5744, 2.8183,  2.0165,  1.0392,  3.0932,  7.3272,  5.6045, -0.1056, -0.3911]],
        device=device,
    )
    # fmt: on
    assert torch.allclose(grad, expected_grad, atol=1e-3)
