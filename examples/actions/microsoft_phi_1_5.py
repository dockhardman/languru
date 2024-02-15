from textwrap import dedent

import torch
from rich import print

from languru.action.base import ActionBase, ModelDeploy
from languru.action.hf import TransformersAction
from languru.types.completions import CompletionRequest
from languru.utils.common import debug_print
from languru.utils.device import validate_device

torch.set_default_device(validate_device())


def run_action_text_completion(action: "ActionBase"):
    completion_params = CompletionRequest.model_validate(
        {
            "model": "microsoft/phi-1_5",
            "prompt": dedent(
                """
                Alice: I don't know why, I'm struggling to maintain focus while studying. Any suggestions?
                Bob: Well, have you tried creating a study schedule and sticking to it?
                Alice: Yes, I have, but it doesn't seem to help much.
                Bob: Hmm, maybe you should try studying in a quiet environment, like the library.
                Alice:
                """
            ).strip(),
            "max_tokens": 200,
            "stop": ["\nAlice:", "\nBob:"],
        }
    )
    completion_res = action.text_completion(
        **completion_params.model_dump(exclude_none=True)
    )
    print()
    debug_print(
        completion_params.model_dump(exclude_none=True),
        completion_res.model_dump(exclude_none=True),
        title=f"Model {completion_params.model} Text Completion",
    )


class MicrosoftPhi2Action(TransformersAction):
    # Model configuration
    MODEL_NAME = "microsoft/phi-1_5"

    model_deploys = (
        ModelDeploy("microsoft/phi-1_5", "microsoft/phi-1_5"),
        ModelDeploy("phi-1_5", "microsoft/phi-1_5"),
    )


if __name__ == "__main__":

    action = MicrosoftPhi2Action()

    run_action_text_completion(action)
