from __future__ import annotations

from subprocess import DEVNULL, call


def cuda_toolkit_available() -> bool:
    """Check if the nvcc is avaiable on the machine."""
    try:
        call(["nvcc"], stdout=DEVNULL, stderr=DEVNULL)
        return True
    except FileNotFoundError:
        return False


def current_cuda_arch() -> str:
    """Get the current CUDA architecture."""
    import torch

    if torch.cuda.is_available():
        current_device = torch.cuda.current_device()
        capability = torch.cuda.get_device_capability(current_device)
        return f"{capability[0]}.{capability[1]}"
    else:
        return ""
