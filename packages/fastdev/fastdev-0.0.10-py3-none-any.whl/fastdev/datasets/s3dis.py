import glob
import os
from dataclasses import dataclass
from typing import Literal

import numpy as np
import torch
from rich.progress import track
from torch.utils.data import Dataset

from fastdev.constants import FDEV_DATASET_ROOT
from fastdev.io.archive import extract_archive
from fastdev.io.download import download_url
from fastdev.utils.tui import console

_S3DIS_URL = "https://cvg-data.inf.ethz.ch/s3dis/Stanford3dDataset_v1.2_Aligned_Version.zip"
_ANNO_FILE_URL = (
    "https://raw.githubusercontent.com/yanx27/Pointnet_Pointnet2_pytorch/master/data_utils/meta/anno_paths.txt"
)
_CLASS_NAMES_FILE_URL = (
    "https://raw.githubusercontent.com/yanx27/Pointnet_Pointnet2_pytorch/master/data_utils/meta/class_names.txt"
)


def collect_point_label(anno_path, out_filename, class_names_path, file_format="txt"):
    """Convert original dataset files to data_label file (each line is XYZRGBL).
        We aggregated all the points from each instance in the room.

    Args:
        anno_path: path to annotations. e.g. Area_1/office_2/Annotations/
        out_filename: path to save collected points and labels (each line is XYZRGBL)
        file_format: txt or numpy, determines what file format to save.
    Returns:
        None
    Note:
        the points are shifted before save, the most negative point is now at origin.
    """
    with open(class_names_path, "r") as f:
        g_classes = [x.rstrip() for x in f.readlines()]
    g_class2label = {cls: i for i, cls in enumerate(g_classes)}

    points_list = []
    for f in glob.glob(os.path.join(anno_path, "*.txt")):
        cls = os.path.basename(f).split("_")[0]
        if cls not in g_classes:  # note: in some room there is 'staris' class..
            cls = "clutter"

        try:
            points = np.loadtxt(f)
        except Exception:
            assert "Area_5/hallway_6/Annotations/ceiling_1.txt" in f
            with open(f, "r") as ff:
                lines = ff.readlines()
                lines = lines[:180388] + lines[180389:]
            with open(f, "w") as ff:
                ff.writelines(lines)
            points = np.loadtxt(f)

        labels = np.ones((points.shape[0], 1)) * g_class2label[cls]
        points_list.append(np.concatenate([points, labels], 1))  # Nx7

    data_label = np.concatenate(points_list, 0)
    xyz_min = np.amin(data_label, axis=0)[0:3]
    data_label[:, 0:3] -= xyz_min

    if file_format == "txt":
        fout = open(out_filename, "w")
        for i in range(data_label.shape[0]):
            fout.write(
                "%f %f %f %d %d %d %d\n"
                % (
                    data_label[i, 0],
                    data_label[i, 1],
                    data_label[i, 2],
                    data_label[i, 3],
                    data_label[i, 4],
                    data_label[i, 5],
                    data_label[i, 6],
                )
            )
        fout.close()
    elif file_format == "numpy":
        np.save(out_filename, data_label)
    else:
        raise ValueError("Unsupported file format.")


@dataclass
class S3DISDatasetConfig:
    """Configuration for S3DISDataset."""

    data_root: str = os.path.join(FDEV_DATASET_ROOT, "s3dis")
    download_if_not_exist: bool = False

    split: Literal["train", "test"] = "train"

    num_points: int = 4096

    test_area: int = 5
    block_size: float = 1.0
    sample_rate: float = 1.0


class S3DISDataset(Dataset):
    """S3DIS dataset."""

    def __init__(self, config: S3DISDatasetConfig):
        self.config = config
        data_root = self.config.data_root
        split = self.config.split
        test_area = self.config.test_area
        sample_rate = self.config.sample_rate
        self.num_points = self.config.num_points
        self.block_size = self.config.block_size

        if not os.path.exists(os.path.join(self.config.data_root, "Area_1")):
            if self.config.download_if_not_exist:
                self.download_data(self.config.data_root)
            else:
                raise FileNotFoundError(f"Data not found at {self.config.data_root}")

        cache_dir = os.path.join(self.config.data_root, "cache")
        if not os.path.exists(os.path.join(cache_dir, "Area_1_hallway_1.npy")):
            console.log("Processing data...")
            os.makedirs(cache_dir, exist_ok=True)
            anno_file = download_url(_ANNO_FILE_URL, os.path.join(data_root, "anno_paths.txt"))
            class_names_file = download_url(_CLASS_NAMES_FILE_URL, os.path.join(data_root, "class_names.txt"))
            with open(anno_file, "r") as f:
                anno_paths = [line.rstrip() for line in f]
                anno_paths = [os.path.join(data_root, p) for p in anno_paths]

            # note: there is an extra character in the v1.2 data in area_5/hallway_6. it's fixed manually.
            for anno_path in track(anno_paths, console=console):
                elements = anno_path.split("/")
                out_filename = elements[-3] + "_" + elements[-2] + ".npy"  # Area_1_hallway_1.npy
                collect_point_label(anno_path, os.path.join(cache_dir, out_filename), class_names_file, "numpy")

        rooms = sorted(os.listdir(cache_dir))
        rooms = [room for room in rooms if "Area_" in room]
        if self.config.split == "train":
            rooms_split = [room for room in rooms if "Area_{}".format(test_area) not in room]
        else:
            rooms_split = [room for room in rooms if "Area_{}".format(test_area) in room]

        self.room_points, self.room_labels = [], []
        self.room_coord_min, self.room_coord_max = [], []
        num_point_all = []
        labelweights = np.zeros(13)

        for room_name in track(rooms_split, total=len(rooms_split), description="Loading data", console=console):
            room_path = os.path.join(cache_dir, room_name)
            room_data = np.load(room_path)  # xyzrgbl, N*7
            points, labels = room_data[:, 0:6], room_data[:, 6]  # xyzrgb, N*6; l, N
            tmp, _ = np.histogram(labels, range(14))
            labelweights += tmp
            coord_min, coord_max = np.amin(points, axis=0)[:3], np.amax(points, axis=0)[:3]
            self.room_points.append(points)
            self.room_labels.append(labels)
            self.room_coord_min.append(coord_min)
            self.room_coord_max.append(coord_max)
            num_point_all.append(labels.size)
        labelweights = labelweights.astype(np.float32)
        labelweights = labelweights / np.sum(labelweights)
        self.labelweights = np.power(np.amax(labelweights) / labelweights, 1 / 3.0)
        console.log(self.labelweights)
        sample_prob = num_point_all / np.sum(num_point_all)
        num_iter = int(np.sum(num_point_all) * sample_rate / self.num_points)
        room_idxs = []
        for index in range(len(rooms_split)):
            room_idxs.extend([index] * int(round(sample_prob[index] * num_iter)))
        self.room_idxs = np.array(room_idxs)
        console.log("Totally {} samples in {} set.".format(len(self.room_idxs), split))

    def __getitem__(self, idx):
        room_idx = self.room_idxs[idx]
        points = self.room_points[room_idx]  # N * 6
        labels = self.room_labels[room_idx]  # N
        N_points = points.shape[0]

        while True:
            center = points[np.random.choice(N_points)][:3]
            block_min = center - [self.block_size / 2.0, self.block_size / 2.0, 0]
            block_max = center + [self.block_size / 2.0, self.block_size / 2.0, 0]
            point_idxs = np.where(
                (points[:, 0] >= block_min[0])
                & (points[:, 0] <= block_max[0])
                & (points[:, 1] >= block_min[1])
                & (points[:, 1] <= block_max[1])
            )[0]
            if point_idxs.size > 1024:
                break

        if point_idxs.size >= self.num_points:
            selected_point_idxs = np.random.choice(point_idxs, self.num_points, replace=False)
        else:
            selected_point_idxs = np.random.choice(point_idxs, self.num_points, replace=True)

        # normalize
        selected_points = points[selected_point_idxs, :]  # num_point * 6
        current_points = np.zeros((self.num_points, 9))  # num_point * 9
        current_points[:, 6] = selected_points[:, 0] / self.room_coord_max[room_idx][0]
        current_points[:, 7] = selected_points[:, 1] / self.room_coord_max[room_idx][1]
        current_points[:, 8] = selected_points[:, 2] / self.room_coord_max[room_idx][2]
        selected_points[:, 0] = selected_points[:, 0] - center[0]
        selected_points[:, 1] = selected_points[:, 1] - center[1]
        selected_points[:, 3:6] /= 255.0
        current_points[:, 0:6] = selected_points
        current_labels = labels[selected_point_idxs]

        return {
            "points": torch.from_numpy(current_points).float(),
            "labels": torch.from_numpy(current_labels).long(),
        }

    def __len__(self):
        return len(self.room_idxs)

    @staticmethod
    def download_data(data_root: str):
        os.makedirs(data_root, exist_ok=True)
        download_url(_S3DIS_URL, data_root)
        extract_archive(
            os.path.join(data_root, "Stanford3dDataset_v1.2_Aligned_Version.zip"), data_root, remove_top_dir=True
        )
        os.remove(os.path.join(data_root, "Stanford3dDataset_v1.2_Aligned_Version.zip"))
