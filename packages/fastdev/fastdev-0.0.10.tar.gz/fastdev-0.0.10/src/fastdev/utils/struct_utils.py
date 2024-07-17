from __future__ import annotations

import torch
from torch import Tensor


def list_to_packed(x: list[Tensor]) -> tuple[Tensor, Tensor, Tensor, Tensor]:
    """
    Transforms a list of N tensors each of shape (Mi, K, ...) into a single
    tensor of shape (sum(Mi), K, ...).

    Args:
      x: list of tensors.

    Returns:
        4-element tuple containing

        - x_packed: tensor consisting of packed input tensors along the
          1st dimension.
        - num_items: tensor of shape N containing Mi for each element in x.
        - item_packed_first_idx: tensor of shape N indicating the index of
          the first item belonging to the same element in the original list.
        - item_packed_to_list_idx: tensor of shape sum(Mi) containing the
          index of the element in the list the item belongs to.
    """
    if not x:
        raise ValueError("Input list is empty")

    device = x[0].device
    sizes = [xi.shape[0] for xi in x]
    sizes_total = sum(sizes)
    num_items = torch.tensor(sizes, dtype=torch.int64, device=device)
    item_packed_first_idx = torch.zeros_like(num_items)
    item_packed_first_idx[1:] = torch.cumsum(num_items[:-1], dim=0)
    item_packed_to_list_idx = torch.arange(sizes_total, dtype=torch.int64, device=device)
    item_packed_to_list_idx = torch.bucketize(item_packed_to_list_idx, item_packed_first_idx, right=True) - 1
    x_packed = torch.cat(x, dim=0)

    return x_packed, num_items, item_packed_first_idx, item_packed_to_list_idx


def packed_to_list(x: Tensor, split_size: list | int):
    """
    Transforms a tensor of shape (sum(Mi), K, L, ...) to N set of tensors of
    shape (Mi, K, L, ...) where Mi's are defined in split_size

    Args:
      x: tensor
      split_size: list, tuple or int defining the number of items for each tensor
        in the output list.

    Returns:
      x_list: A list of Tensors
    """
    return x.split(split_size, dim=0)


__all__ = ["list_to_packed", "packed_to_list"]
