import os
from typing import Literal, Optional, Tuple

import torch
from huggingface_hub import hf_hub_download  # type: ignore

try:
    from smplx import MANO  # type: ignore
    from smplx.lbs import blend_shapes, vertices2joints  # type: ignore
except ImportError:
    raise ImportError(
        "Please install `smplx` to enable this feature. \nIt can be installed by running `pip install smplx`."
    )

import fastdev.xform as xform
from fastdev.constants import FDEV_HF_CACHE_ROOT, FDEV_HF_REPO_ID


def get_local_mano_model_path(hand_side: Literal["left", "right"] = "left") -> str:
    mano_path = os.path.join(FDEV_HF_CACHE_ROOT, "smplx", "mano", f"MANO_{hand_side.upper()}.pkl")
    if not os.path.exists(mano_path):
        hf_hub_download(
            repo_id=FDEV_HF_REPO_ID,
            filename=f"smplx/mano/MANO_{hand_side.upper()}.pkl",
            local_dir=FDEV_HF_CACHE_ROOT,
        )
    return mano_path


def build_mano_layer(
    hand_side: Literal["left", "right"] = "left",
    create_transl: bool = False,
    flat_hand_mean: bool = False,
    use_pca: bool = False,
    num_pca_comps: int = 6,
) -> MANO:
    mano = MANO(
        model_path=get_local_mano_model_path(hand_side),
        create_transl=create_transl,
        use_pca=use_pca,
        num_pca_comps=num_pca_comps,
        flat_hand_mean=flat_hand_mean,
        is_rhand=(hand_side == "right"),
    )

    # workround for https://github.com/vchoutas/smplx/issues/192#issue-2272600127
    mano.use_pca = use_pca
    mano.num_pca_comps = num_pca_comps
    if mano.use_pca:
        mano.register_buffer(
            "hand_components",
            torch.tensor(mano.np_hand_components, dtype=torch.float32),
        )

    return mano


def build_mano_layer_manopth(
    hand_side: Literal["left", "right"] = "left",
    flat_hand_mean: bool = False,
    use_pca: bool = False,
    num_pca_comps: int = 6,
):
    import warnings

    import numpy as np

    # fix for chumpy
    np.bool = np.bool_  # type: ignore
    np.int = np.int_  # type: ignore
    np.float = np.float_  # type: ignore
    np.complex = np.complex_  # type: ignore
    np.object = np.object_  # type: ignore
    np.str = np.str_  # type: ignore
    from manopth.manolayer import ManoLayer  # type: ignore

    if not os.path.exists(os.path.join(FDEV_HF_CACHE_ROOT, "smplx", "mano", "MANO_LEFT.pkl")):
        hf_hub_download(
            repo_id=FDEV_HF_REPO_ID,
            filename="smplx/mano/MANO_LEFT.pkl",
            local_dir=FDEV_HF_CACHE_ROOT,
        )
        hf_hub_download(
            repo_id=FDEV_HF_REPO_ID,
            filename="smplx/mano/MANO_RIGHT.pkl",
            local_dir=FDEV_HF_CACHE_ROOT,
        )

    warnings.filterwarnings("ignore", category=UserWarning, module="manopth")
    return ManoLayer(
        flat_hand_mean=flat_hand_mean,
        ncomps=num_pca_comps,
        side=hand_side,
        mano_root=os.path.join(FDEV_HF_CACHE_ROOT, "smplx", "mano"),
        use_pca=use_pca,
    )


def transform_mano_pose(
    mano: MANO,
    betas: torch.Tensor,
    global_orient: torch.Tensor,
    transl: torch.Tensor,
    tf_rot: torch.Tensor,
    tf_transl: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Change mano parameters to the new coordinate system.

    Reference_

    .. _Reference: https://www.dropbox.com/scl/fi/zkatuv5shs8d4tlwr8ecc/Change-parameters-to-new-coordinate-system.paper?rlkey=lotq1sh6wzkmyttisc05h0in0&dl=
    """
    v_shaped = mano.v_template + blend_shapes(betas, mano.shapedirs)  # type: ignore
    pelvis = vertices2joints(mano.J_regressor[0:1], v_shaped).squeeze(dim=1)  # type: ignore

    new_global_orient = xform.matrix_to_axis_angle(
        xform.axis_angle_to_matrix(tf_rot) @ xform.axis_angle_to_matrix(global_orient)
    )
    if tf_transl is None:
        tf_transl = torch.zeros_like(transl)
    new_transl = (
        xform.rotate((pelvis + transl).unsqueeze(1), xform.axis_angle_to_matrix(tf_rot)).squeeze(1) - pelvis + tf_transl
    )

    return new_global_orient, new_transl


__all__ = ["build_mano_layer", "build_mano_layer_manopth", "transform_mano_pose"]
