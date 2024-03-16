import importlib
import logging
from typing import TYPE_CHECKING, Text, Type

from languru.config import logger

if TYPE_CHECKING:
    from languru.action.base import ActionBase


def load_action(
    action: Text, *, logger: "logging.Logger" = logger, **kwargs
) -> "ActionBase":
    from languru.action.base import ActionBase

    logger.info(f"Loading action class '{action}'")
    action_module_path, action_class_name = action.rsplit(".", 1)
    action_cls: Type["ActionBase"] = getattr(
        importlib.import_module(action_module_path), action_class_name
    )
    if issubclass(action_cls, ActionBase) is False:
        raise ValueError(f"Action class '{action}' is not a subclass of ActionBase")
    action_instance = action_cls(**kwargs)
    if action_instance.model_deploys is None:
        raise ValueError(f"Action '{action}' model_deploys is not defined")
    return action_instance
