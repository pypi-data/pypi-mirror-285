from __future__ import annotations

import os

import requests
import urllib3
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from fastdev.utils.tui import console
from fastdev.constants import FDEV_CACHE_ROOT

_PROGRESS = Progress(
    TextColumn("{task.fields[filename]}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    DownloadColumn(),
    "•",
    TransferSpeedColumn(),
    "•",
    TimeRemainingColumn(elapsed_when_finished=True),
    console=console,
)


def _truncate(text: str, length: int = 15) -> str:
    return text if len(text) <= length else text[: length - 3] + "..."


def download_url(url: str, local_path: str, verify: bool = True, force_redownload: bool = False) -> str:
    """Download url to local path.

    Args:
        url (str): URL to download.
        local_path (str): Local path to save the downloaded file.
            If the local path is a directory, the file will be saved to the directory with the same name as the URL basename.
        verify (bool, optional): Verify SSL certificate. Defaults to True.
        force_redownload (bool, optional): Whether to force redownload the file even if it exists. Defaults to False.

    Returns:
        str: Local path of the downloaded file.
    """
    if not verify:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if os.path.isdir(local_path):
        local_path = os.path.join(local_path, os.path.basename(url))

    if not force_redownload and os.path.exists(local_path):
        with requests.head(url, verify=verify) as response:
            response.raise_for_status()
            remote_size = int(response.headers.get("Content-length", 0))

        if os.path.getsize(local_path) == remote_size:
            console.log(f"{local_path} File exists with same size, skipping...")
            return local_path
        else:
            console.log(f"{local_path} File exists but with different size, redownloading...")

    with _PROGRESS, requests.get(url, stream=True, verify=verify) as response:
        console.log(f"Requesting {url}")
        response.raise_for_status()
        task = _PROGRESS.add_task(
            "download",
            total=int(response.headers.get("Content-length", 0)),
            filename=_truncate(os.path.basename(local_path)),
        )
        with open(local_path, "wb") as dest_file:
            for data in response.iter_content(chunk_size=32768):
                dest_file.write(data)
                _PROGRESS.advance(task, advance=len(data))

    console.log(f"Saved to {local_path}")
    return local_path


def cached_local_path(url: str, rel_cache_path: str | None = None, cache_root: str = FDEV_CACHE_ROOT) -> str:
    """Get the cached local path of the URL.

    Args:
        url (str): Remote URL.
        rel_cache_path (str | None, optional): Relative local path in the cache root.
            Use the URL relative path if None. Defaults to None.
        cache_root (str, optional): Cache root. Defaults to FDEV_CACHE_ROOT.
    """
    local_path = os.path.join(cache_root, rel_cache_path or url.lstrip("https://"))
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if not os.path.exists(local_path):
        download_url(url, local_path)
    return local_path


__all__ = ["download_url", "cached_local_path"]
