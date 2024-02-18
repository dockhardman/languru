from typing import TYPE_CHECKING, Literal, TypeVar, overload

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from torch import Tensor

FloatType = TypeVar("FloatType", np.float16, np.float32, np.float64)


def mean_pooling(
    last_hidden_states: NDArray[FloatType], attention_mask: NDArray[FloatType]
) -> NDArray[FloatType]:
    # Convert attention_mask to boolean
    # and expand its dimensions to match last_hidden_states
    attention_mask_expanded = np.expand_dims(attention_mask, axis=-1).astype(bool)
    # Use the attention mask to zero out positions in last_hidden_states
    last_hidden = np.where(attention_mask_expanded, last_hidden_states, 0.0)
    # Sum along the specified axis and compute the average
    sum_hidden = last_hidden.sum(axis=1)
    mask_sum = attention_mask.sum(axis=1, keepdims=True)
    # Avoid division by zero
    mask_sum = np.where(mask_sum == 0, 1, mask_sum)

    average_hidden = sum_hidden / mask_sum
    return average_hidden


@overload
def tensor_to_np(
    tensor: "Tensor", precision: Literal["float16", "half"] = "float16"
) -> NDArray[np.float16]: ...


@overload
def tensor_to_np(
    tensor: "Tensor", precision: Literal["float32", "float"] = "float32"
) -> NDArray[np.float32]: ...


@overload
def tensor_to_np(
    tensor: "Tensor", precision: Literal["float64", "double"] = "float64"
) -> NDArray[np.float64]: ...


def tensor_to_np(
    tensor: "Tensor",
    precision: Literal[
        "float16", "float32", "float64", "half", "float", "double"
    ] = "float32",
) -> NDArray[FloatType]:
    return tensor.detach().cpu().float().numpy()
