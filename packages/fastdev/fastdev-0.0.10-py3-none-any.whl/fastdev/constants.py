import os

# cpp/cuda source code
FDEV_CSRC_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "csrc"))

# cache
FDEV_CACHE_ROOT = os.path.abspath(os.path.join(os.path.expanduser("~/.cache/fastdev")))

# dataset
FDEV_DATASET_ROOT = os.path.abspath(os.path.expanduser("~/data"))  # ~/data
FDEV_PROCESSED_ROOT = os.path.join(FDEV_DATASET_ROOT, "processed")  # ~/data/processed

# huggingface
FDEV_HF_CACHE_ROOT = os.path.join(FDEV_CACHE_ROOT, "hf")  # ~/.cache/fastdev/hf
FDEV_HF_REPO_ID = "jianglong-org/fastdev"  # https://huggingface.co/jianglong-org/fastdev

# github
FDEV_GH_CACHE_ROOT = os.path.join(FDEV_CACHE_ROOT, "gh")  # ~/.cache/fastdev/gh
