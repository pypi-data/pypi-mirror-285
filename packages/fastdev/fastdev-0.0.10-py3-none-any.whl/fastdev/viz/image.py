from typing import Optional

import cv2
import numpy as np

COMMON_COLOR = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}


def draw_points(
    img: np.ndarray,
    pts: np.ndarray,
    colors: Optional[np.ndarray] = None,
    radius=1,
    order="uv",
) -> np.ndarray:
    """
    Args:
        img (ndarray): original image
        pts (ndarray): points in xy order, shaped (n x 2) or (2)
        colors (ndarray): color, shaped (n x 3) or (3)
        radius (int): radius of points
        order (str): order of points, "uv" or "xy", default "uv" (since most keypoints dataset use uv order)
    """
    assert order in ["xy", "uv"], "order should be xy or uv"
    if colors is None:
        colors = np.asarray(COMMON_COLOR["red"])
    pts, colors = np.asarray(pts), np.asarray(colors)

    assert (pts.ndim == 1 or pts.ndim == 2) and pts.shape[-1] == 2, f"wrong pts shape: {pts.shape}"
    assert (colors.ndim == 1 or colors.ndim == 2) and colors.shape[-1] in [
        3,
        4,
    ], f"wrong colors shape: {colors.shape}"

    if pts.ndim == 1:
        pts = pts[None, :]
    if colors.ndim == 2:
        assert colors.shape[0] == pts.shape[0], "colors and pts should in the same number"
    if order == "xy":
        pts = pts[:, ::-1]

    vis_img = img.copy()  # avoid modifying the original image
    pts = pts.astype(int)  # round to int
    for i in range(pts.shape[0]):
        # opencv use the uv order
        color = colors if colors.ndim == 1 else colors[i]
        cv2.circle(
            vis_img,
            center=tuple(pts[i].tolist()),
            color=tuple(color.tolist()),
            radius=radius,
            thickness=-1,
        )
    return vis_img


__all__ = ["draw_points"]
