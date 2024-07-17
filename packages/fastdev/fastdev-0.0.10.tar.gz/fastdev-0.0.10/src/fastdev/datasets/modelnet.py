import os
import pickle
from dataclasses import dataclass
from typing import Literal

import numpy as np
import torch
from rich.progress import track
from torch.utils.data import Dataset

from fastdev.constants import FDEV_DATASET_ROOT
from fastdev.io import download_url, extract_archive

_MODEL_NET_URL = "https://shapenet.cs.stanford.edu/media/modelnet40_normal_resampled.zip"


def _farthest_point_sample(point, npoint):
    """
    Input:
        xyz: pointcloud data, [N, D]
        npoint: number of samples
    Return:
        centroids: sampled pointcloud index, [npoint, D]
    """
    N, D = point.shape
    xyz = point[:, :3]
    centroids = np.zeros((npoint,))
    distance = np.ones((N,)) * 1e10
    farthest = np.random.randint(0, N)
    for i in range(npoint):
        centroids[i] = farthest
        centroid = xyz[farthest, :]
        dist = np.sum((xyz - centroid) ** 2, -1)
        mask = dist < distance
        distance[mask] = dist[mask]
        farthest = np.argmax(distance, -1)
    point = point[centroids.astype(np.int32)]
    return point


def _pc_normalize(pc):
    centroid = np.mean(pc, axis=0)
    pc = pc - centroid
    m = np.max(np.sqrt(np.sum(pc**2, axis=1)))
    pc = pc / m
    return pc


@dataclass(frozen=True)
class ModelNetDatasetConfig:
    """Configuration for ModelNetDataset."""

    data_root: str = os.path.join(FDEV_DATASET_ROOT, "modelnet")
    download_if_not_exist: bool = False
    preprocess_data: bool = True

    split: Literal["train", "test"] = "train"

    num_categories: Literal[10, 40] = 40
    num_points: int = 1024

    uniform_sampling: bool = False
    return_normals: bool = False

    def __post_init__(self):
        if not os.path.exists(os.path.join(self.data_root, "filelist.txt")) and not self.download_if_not_exist:
            raise FileNotFoundError(
                f"ModelNet dataset not found at {self.data_root}, "
                "please set `download_if_not_exist=True` to download it. "
                "Or specify the correct path in `data_root`."
            )


class ModelNetDataset(Dataset):
    """ModelNet dataset."""

    def __init__(self, config: ModelNetDatasetConfig):
        self.config = config

        if not os.path.exists(os.path.join(self.config.data_root, "filelist.txt")):
            if self.config.download_if_not_exist:
                self.download_data(self.config.data_root)
            else:
                raise FileNotFoundError(f"ModelNet dataset not found at {self.config.data_root}")

        self._catfile = os.path.join(self.config.data_root, f"modelnet{self.config.num_categories}_shape_names.txt")

        with open(self._catfile, "r") as f:
            self._categories = [line.rstrip() for line in f]
        self._classes = dict(zip(self._categories, range(len(self._categories))))

        shape_ids = {}
        shape_ids["train"] = [
            line.rstrip()
            for line in open(os.path.join(self.config.data_root, f"modelnet{self.config.num_categories}_train.txt"))
        ]
        shape_ids["test"] = [
            line.rstrip()
            for line in open(os.path.join(self.config.data_root, f"modelnet{self.config.num_categories}_test.txt"))
        ]

        split = self.config.split
        shape_names = ["_".join(x.split("_")[0:-1]) for x in shape_ids[split]]
        self._datapath = [
            (shape_names[i], os.path.join(self.config.data_root, shape_names[i], shape_ids[split][i]) + ".txt")
            for i in range(len(shape_ids[split]))
        ]
        print("The size of %s data is %d" % (split, len(self._datapath)))

        if self.config.uniform_sampling:
            self._save_path = os.path.join(
                self.config.data_root,
                "modelnet%d_%s_%dpts_fps.dat" % (self.config.num_categories, split, self.config.num_points),
            )
        else:
            self._save_path = os.path.join(
                self.config.data_root,
                "modelnet%d_%s_%dpts.dat" % (self.config.num_categories, split, self.config.num_points),
            )

        if self.config.preprocess_data:
            if not os.path.exists(self._save_path):
                print("Processing data %s (only running in the first time)..." % self._save_path)
                self._list_of_points = []
                self._list_of_labels = []

                for index in track(range(len(self._datapath)), total=len(self._datapath), description="Processing"):
                    fn = self._datapath[index]
                    cls = self._classes[self._datapath[index][0]]
                    cls = np.array([cls]).astype(np.int32)
                    point_set = np.loadtxt(fn[1], delimiter=",").astype(np.float32)

                    if self.config.uniform_sampling:
                        point_set = _farthest_point_sample(point_set, self.config.num_points)
                    else:
                        point_set = point_set[0 : self.config.num_points, :]

                    self._list_of_points.append(point_set)
                    self._list_of_labels.append(cls)

                with open(self._save_path, "wb") as f:
                    pickle.dump([self._list_of_points, self._list_of_labels], f)
            else:
                print("Load processed data from %s..." % self._save_path)
                with open(self._save_path, "rb") as f:
                    self._list_of_points, self._list_of_labels = pickle.load(f)

    def __len__(self):
        return len(self._datapath)

    def __getitem__(self, index):
        if self.config.preprocess_data:
            point_set, label = self._list_of_points[index], self._list_of_labels[index]
        else:
            fn = self._datapath[index]
            cls = self._classes[self._datapath[index][0]]
            label = np.array([cls]).astype(np.int32)
            point_set = np.loadtxt(fn[1], delimiter=",").astype(np.float32)

            if self.config.uniform_sampling:
                point_set = _farthest_point_sample(point_set, self.config.num_points)
            else:
                point_set = point_set[0 : self.config.num_points, :]

        point_set[:, 0:3] = _pc_normalize(point_set[:, 0:3])

        if not self.config.return_normals:
            point_set = point_set[:, 0:3]

        return {
            "points": torch.from_numpy(point_set).float(),
            "labels": torch.from_numpy(label).long(),
        }

    @staticmethod
    def download_data(data_root: str):
        os.makedirs(data_root, exist_ok=True)
        download_url(_MODEL_NET_URL, data_root, verify=False)
        extract_archive(os.path.join(data_root, "modelnet40_normal_resampled.zip"), data_root, remove_top_dir=True)
        os.remove(os.path.join(data_root, "modelnet40_normal_resampled.zip"))


__all__ = ["ModelNetDataset", "ModelNetDatasetConfig"]
