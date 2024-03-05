from typing import Optional, Text

from languru.config import logger

# Support dtype
cpu_supported_dtype = ("float32", "float64")
mps_supported_dtype = ("float16", "float32", "float64", "bfloat16")


def validate_device(device: Optional[Text] = None) -> Text:
    if device is not None and device.strip().lower() == "auto":
        return "auto"
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


def validate_dtype(device: Text, dtype: Optional[Text] = None):
    if dtype is None:
        return
    device_str_value = device.strip().lower()
    dtype_value = dtype.strip().lower()

    if device_str_value == "cpu":
        if dtype_value not in cpu_supported_dtype:
            raise ValueError(f"Invalid dtype for CPU: {dtype}")
    elif device_str_value.startswith("mps"):
        if dtype_value not in mps_supported_dtype:
            raise ValueError(f"Invalid dtype for MPS: {dtype}")
    elif device_str_value.startswith("auto"):
        return
    elif device_str_value.startswith("cuda"):
        return
    else:
        logger.debug(f"Unhandled device and dtype yet: {device} {dtype}.")
