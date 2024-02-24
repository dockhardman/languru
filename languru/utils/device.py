from typing import TYPE_CHECKING, Optional, Text

from languru.config import logger

if TYPE_CHECKING:
    import torch


# Support dtype
cpu_supported_dtype = ("float32", "float64")
mps_supported_dtype = ("float16", "float32", "float64")


def validate_device(device: Optional[Text] = None) -> Text:
    if device is not None and device.strip().lower() == "cpu":
        return "cpu"
    try:
        import torch
    except ImportError:
        logger.warning("Torch is not installed. The device will be CPU.")
        return "cpu"
    # Try to find the device
    if device is None:
        if torch.cuda.is_available():
            logger.debug("Device found: CUDA")
            return "cuda"
        elif torch.backends.mps.is_available():
            logger.debug("Device found: MPS")
            return "mps"
        else:
            logger.debug("Device found: CPU")
            return "cpu"
    # Validate cuda device
    if device.strip().startswith("cuda"):
        if not torch.cuda.is_available():
            logger.warning("CUDA is not available. The device will be CPU.")
            return "cpu"
        return device
    # Validate mps device
    if device.strip().startswith("mps"):
        if not torch.backends.mps.is_available():
            logger.warning("MPS is not available. The device will be CPU.")
            return "cpu"
        return device
    # Validate cpu device
    if device.strip() == "cpu":
        return device
    # Validate unknown device
    logger.warning(f"Unknown device: {device}. The device will be CPU.")
    return "cpu"


def validate_dtype(device: Text, dtype: Text) -> "torch.dtype":
    import torch

    device_str_value = device.strip().lower()
    dtype_value = dtype.strip().lower()
    torch_dtype: Optional["torch.dtype"] = getattr(torch, dtype_value, None)
    if device_str_value is None and dtype_value is None:
        raise ValueError(f"Invalid device and dtype: {device} {dtype}")
    if device_str_value == "cpu":
        if dtype_value not in cpu_supported_dtype:
            raise ValueError(f"Invalid dtype for CPU: {dtype}")
    elif device_str_value.startswith("mps"):
        if dtype_value not in mps_supported_dtype:
            raise ValueError(f"Invalid dtype for MPS: {dtype}")
    elif device_str_value.startswith("cuda"):
        if torch_dtype is None:
            raise ValueError(f"Invalid dtype for CUDA: {dtype}")
    else:
        logger.debug(f"Unhandled device and dtype yet: {device} {dtype}.")
    if torch_dtype is None:
        raise ValueError(f"Invalid dtype for unknown device: {dtype}")
    return torch_dtype
