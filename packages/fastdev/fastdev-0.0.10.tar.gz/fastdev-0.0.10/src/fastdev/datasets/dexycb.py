import os
import pickle
from dataclasses import dataclass
from glob import glob
from typing import Dict, Literal, Optional

import cv2
import numpy as np
import torch
import trimesh
from rich.progress import track
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset, default_collate
from torchvision.io import read_image

from fastdev.constants import FDEV_DATASET_ROOT, FDEV_PROCESSED_ROOT
from fastdev.io import load
from fastdev.utils import Timer

_SUBJECTS = [
    "20200709-subject-01",
    "20200813-subject-02",
    "20200820-subject-03",
    "20200903-subject-04",
    "20200908-subject-05",
    "20200918-subject-06",
    "20200928-subject-07",
    "20201002-subject-08",
    "20201015-subject-09",
    "20201022-subject-10",
]

_SERIALS = [
    "836212060125",
    "839512060362",
    "840412060917",
    "841412060263",
    "932122060857",
    "932122060861",
    "932122061900",
    "932122062010",
]

_YCB_CLASSES = {
    1: "002_master_chef_can",
    2: "003_cracker_box",
    3: "004_sugar_box",
    4: "005_tomato_soup_can",
    5: "006_mustard_bottle",
    6: "007_tuna_fish_can",
    7: "008_pudding_box",
    8: "009_gelatin_box",
    9: "010_potted_meat_can",
    10: "011_banana",
    11: "019_pitcher_base",
    12: "021_bleach_cleanser",
    13: "024_bowl",
    14: "025_mug",
    15: "035_power_drill",
    16: "036_wood_block",
    17: "037_scissors",
    18: "040_large_marker",
    19: "051_large_clamp",
    20: "052_extra_large_clamp",
    21: "061_foam_brick",
}


@dataclass(frozen=True)
class DexYCBDatasetConfig:
    """Configuration for DexYCBDataset."""

    data_root: str = os.path.join(FDEV_DATASET_ROOT, "dexycb")

    split: Literal["train", "val", "test", "all"] = "train"
    hand_side: Literal["left", "right", "both"] = "left"
    setup: Literal["s0", "s1", "s2", "s3"] = "s0"
    """

    - [s0] Seen subjects, camera views, grasped objects, unseen frames
    - [s1] Unseen subjects
    - [s2] Unseen camera views
    - [s3] Unseen grasped objects

    Reference_

    .. _Reference: https://github.com/NVlabs/dex-ycb-toolkit/blob/64551b001d360ad83bc383157a559ec248fb9100/dex_ycb_toolkit/dex_ycb.py#L126
    """
    serials: Optional[list[str]] = None  # specify serials to load

    return_color: bool = True
    return_depth: bool = False
    return_object_mesh: bool = False  # return object mesh vertices and faces in the object space
    return_as_sequence: bool = False  # return the whole sequence instead of a single frame
    return_no_hand_frames: bool = True
    # if False, filter out frames where the hand is not fully visible on image (i.e., mano pose non-zero and all joints inside the frame)

    metadata_cache_path: str = os.path.join(FDEV_PROCESSED_ROOT, "dexycb", "metadata_cache.pkl")
    # pkl is faster than npz, suitable for caching
    force_rebuild_cache: bool = False

    def __post_init__(self) -> None:
        assert os.path.exists(self.data_root), f"Data root {self.data_root} does not exist."
        if self.serials is not None:
            assert all(s in _SERIALS for s in self.serials), f"Serials {self.serials} invalid."


class DexYCBDataset(Dataset):
    """DexYCBDataset.

    Args:
        config (DexYCBDatasetConfig): configuration for the dataset.

    Examples:
        >>> # doctest: +SKIP
        >>> from fastdev.datasets.dexycb import DexYCBDataset, DexYCBDatasetConfig
        >>> dataset = DexYCBDataset(DexYCBDatasetConfig())
    """

    ycb_classes = _YCB_CLASSES

    def __init__(self, config: DexYCBDatasetConfig) -> None:
        self.config = config

        self._data_dir = self.config.data_root
        self._calib_dir = os.path.join(self._data_dir, "calibration")
        self._model_dir = os.path.join(self._data_dir, "models")
        self._color_format = "color_{:06d}.jpg"
        self._depth_format = "aligned_depth_to_color_{:06d}.png"
        self._label_format = "labels_{:06d}.npz"
        self._h = 480
        self._w = 640
        self._obj_file = {k: os.path.join(self._model_dir, v, "textured_simple.obj") for k, v in _YCB_CLASSES.items()}
        self._obj_mesh_cache = {}

        # ----------- Cache Metadata -----------
        if (not os.path.exists(self.config.metadata_cache_path)) or self.config.force_rebuild_cache:
            intrinsics = {}
            for serial in _SERIALS:
                intr_file = os.path.join(
                    self._calib_dir,
                    "intrinsics",
                    "{}_{}x{}.yml".format(serial, self._w, self._h),
                )
                intr = load(intr_file)
                intrinsics[serial] = intr["color"]

            extrinsics = {}
            extr_dirs = sorted(glob(os.path.join(self._calib_dir, "extrinsics_*")))
            for extr_dir in extr_dirs:
                extr = load(os.path.join(extr_dir, "extrinsics.yml"))
                extrinsics[os.path.basename(extr_dir).split("extrinsics_")[-1]] = extr

            mano_calibs = {}
            mano_calib_dirs = sorted(glob(os.path.join(self._calib_dir, "mano_*")))
            for mano_calib_dir in mano_calib_dirs:
                mano_calib = load(os.path.join(mano_calib_dir, "mano.yml"))
                mano_calibs[os.path.basename(mano_calib_dir).split("mano_")[-1]] = mano_calib

            seq_metas = {}
            for subject in track(_SUBJECTS, description="Caching seq metadata"):
                seqs = sorted(os.listdir(os.path.join(self._data_dir, subject)))
                seqs = [os.path.join(subject, seq) for seq in seqs]
                assert len(seqs) == 100, "Each subject in DexYCB should have 100 sequences."
                for seq in seqs:
                    seq_meta = load(os.path.join(self._data_dir, seq, "meta.yml"))
                    seq_metas[seq] = seq_meta
                    seq_metas[seq]["valid_frame_range"] = {}
                    seq_metas[seq]["joint_2d"], seq_metas[seq]["joint_3d"] = {}, {}
                    seq_metas[seq]["pose_m"], seq_metas[seq]["pose_y"] = {}, {}

                    seq_pose_m = np.load(os.path.join(self._data_dir, seq, "pose.npz"))["pose_m"][:, 0]
                    non_zero_pose_frames = np.any(seq_pose_m != 0, axis=-1)

                    for serial in _SERIALS:
                        label_files = sorted(glob(os.path.join(self._data_dir, seq, serial, "labels_*.npz")))
                        label_data = [np.load(label_file) for label_file in label_files]
                        joint_2d = np.stack([label["joint_2d"][0] for label in label_data])

                        joints_inside_frames = np.all(
                            np.logical_and(
                                np.logical_and(joint_2d[..., 0] >= 0, joint_2d[..., 0] < self._w),
                                np.logical_and(joint_2d[..., 1] >= 0, joint_2d[..., 1] < self._h),
                            ),
                            axis=-1,
                        )
                        valid_frames = np.logical_and(non_zero_pose_frames, joints_inside_frames)
                        if np.any(valid_frames):
                            valid_begin_frame, valid_end_frame = np.where(valid_frames)[0][[0, -1]]
                        else:
                            # no valid frames
                            valid_begin_frame, valid_end_frame = -1, -1

                        # range is always half-open
                        seq_metas[seq]["valid_frame_range"][serial] = (
                            valid_begin_frame,
                            valid_end_frame + 1,
                        )
                        seq_metas[seq]["joint_2d"][serial] = joint_2d
                        seq_metas[seq]["joint_3d"][serial] = np.stack([label["joint_3d"][0] for label in label_data])
                        seq_metas[seq]["pose_m"][serial] = np.stack([label["pose_m"][0] for label in label_data])
                        seq_metas[seq]["pose_y"][serial] = np.stack([label["pose_y"][0] for label in label_data])

            os.makedirs(os.path.dirname(self.config.metadata_cache_path), exist_ok=True)
            with open(self.config.metadata_cache_path, "wb") as f:
                pickle.dump(
                    {
                        "intrinsics": intrinsics,
                        "extrinsics": extrinsics,
                        "mano_calibs": mano_calibs,
                        "seq_metas": seq_metas,
                    },
                    f,
                )
        with Timer(print_tmpl="Loading metadata cache: {:.4f}s"):
            with open(self.config.metadata_cache_path, "rb") as f:
                metadata_cache = pickle.load(f)
                self._intrinsics = metadata_cache["intrinsics"]
                self._extrinsics = metadata_cache["extrinsics"]
                self._mano_calibs = metadata_cache["mano_calibs"]
                cached_seq_metas = metadata_cache["seq_metas"]

        # ----------- Filter sequences, serials, frames -----------
        # Seen subjects, camera views, grasped objects.
        if self.config.setup == "s0":
            if self.config.split == "train":
                subject_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = [i for i in range(100) if i % 5 != 4]
            if self.config.split == "val":
                subject_ind = [0, 1]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = [i for i in range(100) if i % 5 == 4]
            if self.config.split == "test":
                subject_ind = [2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = [i for i in range(100) if i % 5 == 4]
        # Unseen subjects.
        if self.config.setup == "s1":
            if self.config.split == "train":
                subject_ind = [0, 1, 2, 3, 4, 5, 9]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = list(range(100))
            if self.config.split == "val":
                subject_ind = [6]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = list(range(100))
            if self.config.split == "test":
                subject_ind = [7, 8]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = list(range(100))
        # Unseen camera views.
        if self.config.setup == "s2":
            if self.config.split == "train":
                subject_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [0, 1, 2, 3, 4, 5]
                sequence_ind = list(range(100))
            if self.config.split == "val":
                subject_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [6]
                sequence_ind = list(range(100))
            if self.config.split == "test":
                subject_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [7]
                sequence_ind = list(range(100))
        # Unseen grasped objects.
        if self.config.setup == "s3":
            if self.config.split == "train":
                subject_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = [i for i in range(100) if i // 5 not in (3, 7, 11, 15, 19)]
            if self.config.split == "val":
                subject_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = [i for i in range(100) if i // 5 in (3, 19)]
            if self.config.split == "test":
                subject_ind = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                serial_ind = [0, 1, 2, 3, 4, 5, 6, 7]
                sequence_ind = [i for i in range(100) if i // 5 in (7, 11, 15)]
        if self.config.split == "all":
            subject_ind = list(range(10))
            serial_ind = list(range(8))
            sequence_ind = list(range(100))

        self._subjects = [_SUBJECTS[i] for i in subject_ind]  # type: ignore
        self._serials = [_SERIALS[i] for i in serial_ind] if self.config.serials is None else self.config.serials  # type: ignore
        self._sequences, self._seq_metas = [], []

        for subject in self._subjects:
            seqs = sorted([seq for seq in cached_seq_metas.keys() if subject in seq])
            seqs = [seqs[i] for i in sequence_ind]  # type: ignore
            for seq in seqs:
                meta = cached_seq_metas[seq]
                assert len(meta["mano_sides"]) == 1, "Each sequence in DexYCB only has one mano side."
                if self.config.hand_side != "both" and meta["mano_sides"][0] != self.config.hand_side:
                    continue
                else:
                    self._sequences.append(seq)
                    self._seq_metas.append(meta)

        self._mapping = []  # type: ignore
        for seq_idx, (seq, meta) in enumerate(zip(self._sequences, self._seq_metas)):
            for serial_idx, serial in enumerate(self._serials):
                # range is always half-open
                valid_frame_range = meta["valid_frame_range"][serial]
                if valid_frame_range == (-1, 0) and not self.config.return_no_hand_frames:
                    # no valid frames
                    continue

                if not self.config.return_no_hand_frames:
                    frame_range = valid_frame_range
                else:
                    frame_range = (0, meta["num_frames"])
                if not self.config.return_as_sequence:
                    frame_indices = np.arange(*frame_range)
                    seq_indices = seq_idx * np.ones_like(frame_indices)
                    serial_indices = serial_idx * np.ones_like(frame_indices)

                    mapping = np.vstack((seq_indices, serial_indices, frame_indices)).T
                    self._mapping.append(mapping)  # type: ignore
                else:
                    self._mapping.append(np.array([seq_idx, serial_idx]))  # type: ignore

        self._mapping: np.ndarray = np.vstack(self._mapping)  # type: ignore

    def __len__(self):
        return len(self._mapping)

    def _load_frame_data(self, data_dir, frame_idx):
        frame_data = {}
        if self.config.return_color:
            color_file = os.path.join(data_dir, self._color_format.format(frame_idx))
            frame_data["color"] = read_image(color_file)
        if self.config.return_depth:
            depth_file = os.path.join(data_dir, self._depth_format.format(frame_idx))
            depth = cv2.imread(depth_file, cv2.IMREAD_ANYDEPTH)
            frame_data["depth"] = torch.from_numpy(depth.astype(np.float32) / 1000)
        return frame_data

    def _load_object_mesh(self, ycb_id: int) -> Dict[Literal["vertices", "faces"], torch.Tensor]:
        if ycb_id not in self._obj_mesh_cache:
            obj_file = self._obj_file[ycb_id]
            obj_mesh = trimesh.load(obj_file)
            vertices = torch.tensor(obj_mesh.vertices, dtype=torch.float32)  # type: ignore
            faces = torch.tensor(obj_mesh.faces, dtype=torch.int32)  # type: ignore
            self._obj_mesh_cache[ycb_id] = {"vertices": vertices, "faces": faces}
        return self._obj_mesh_cache[ycb_id]

    def __getitem__(self, idx):
        if not self.config.return_as_sequence:
            seq_idx, serial_idx, frame_idx = self._mapping[idx]
            # range is always half-open
            frame_range = (frame_idx, frame_idx + 1)
        else:
            seq_idx, serial_idx = self._mapping[idx]
            if self.config.return_no_hand_frames:
                frame_range = (0, self._seq_metas[seq_idx]["num_frames"])
            else:
                frame_range = self._seq_metas[seq_idx]["valid_frame_range"][self._serials[serial_idx]]

        data_dir = os.path.join(self._data_dir, self._sequences[seq_idx], self._serials[serial_idx])
        seq_meta = self._seq_metas[seq_idx]
        extr = self._extrinsics[seq_meta["extrinsics"]]["extrinsics"][self._serials[serial_idx]]
        extr = torch.tensor(extr, dtype=torch.float32).reshape(3, 4)
        sample = {
            "sequence": self._sequences[seq_idx],
            "serial": self._serials[serial_idx],
            "frame_range": torch.tensor(frame_range, dtype=torch.int32),
            "intrinsics": self._intrinsics[self._serials[serial_idx]],
            "extrinsics": extr,
            "ycb_grasp_id": seq_meta["ycb_ids"][seq_meta["ycb_grasp_ind"]],
            "mano_side": seq_meta["mano_sides"][0],
            "mano_betas": torch.tensor(
                self._mano_calibs[seq_meta["mano_calib"][0]]["betas"],
                dtype=torch.float32,
            ),
        }

        pose_y = torch.from_numpy(
            seq_meta["pose_y"][self._serials[serial_idx]][frame_range[0] : frame_range[1]]
        ).float()
        sample["object_pose"] = pose_y
        object_mesh = self._load_object_mesh(sample["ycb_grasp_id"])
        sample["object_vertices"] = object_mesh["vertices"]
        sample["object_faces"] = object_mesh["faces"]

        frames_data = [self._load_frame_data(data_dir, frame_idx) for frame_idx in range(*frame_range)]
        for key in frames_data[0].keys():
            sample[key] = torch.stack([frame_data[key] for frame_data in frames_data], dim=0)
            if not self.config.return_as_sequence:
                sample[key].squeeze_(0)
        pose_m = torch.from_numpy(
            seq_meta["pose_m"][self._serials[serial_idx]][frame_range[0] : frame_range[1]]
        ).float()
        sample["mano_global_orient"] = pose_m[..., :3]
        sample["mano_hand_pose"] = pose_m[..., 3:48]
        sample["mano_transl"] = pose_m[..., 48:51]

        if not self.config.return_as_sequence:
            sample["mano_global_orient"].squeeze_(0)
            sample["mano_hand_pose"].squeeze_(0)
            sample["mano_transl"].squeeze_(0)
            sample["object_pose"].squeeze_(0)
        return sample

    @property
    def h(self):
        return self._h

    @property
    def w(self):
        return self._w

    @property
    def subjects(self):
        return self._subjects

    @property
    def serials(self):
        return self._serials

    @property
    def sequences(self):
        return self._sequences

    def select_indices(self, seq: str, serial: Optional[str] = None):
        assert seq in self._sequences, f"Sequence {seq} not found in the dataset."
        if serial is None:
            return np.where(self._mapping[:, 0] == self._sequences.index(seq))[0]
        else:
            assert serial in self._serials, f"Serial {serial} not found in the dataset."
            return np.where(
                np.logical_and(
                    self._mapping[:, 0] == self._sequences.index(seq),
                    self._mapping[:, 1] == self._serials.index(serial),
                )
            )[0]

    def build_collate_fn(self):
        def _seq_collate_fn(batch):
            collated_batch = {}
            for key in batch[0].keys():
                if key in [
                    "color",
                    "depth",
                    "mano_global_orient",
                    "mano_hand_pose",
                    "mano_transl",
                ]:
                    collated_batch[key] = pad_sequence([sample[key] for sample in batch], batch_first=True)
                else:
                    collated_batch[key] = default_collate([sample[key] for sample in batch])
            return collated_batch

        if not self.config.return_as_sequence:
            return default_collate
        else:
            return _seq_collate_fn


__all__ = ["DexYCBDataset", "DexYCBDatasetConfig"]
