import os
import time
import uuid
from typing import Optional, Sequence, Text

import torch
from openai.types import Completion, CompletionChoice, CompletionUsage
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    GenerationConfig,
    PreTrainedModel,
    StoppingCriteria,
    StoppingCriteriaList,
)

from languru.action.base import ActionBase, ModelDeploy
from languru.config import logger
from languru.utils.common import should_str_or_none
from languru.utils.hf import StopAtWordsStoppingCriteria


class TransformersAction(ActionBase):
    # Model configuration
    MODEL_NAME: Text = (os.getenv("HF_MODEL_NAME") or os.getenv("MODEL_NAME")) or ""
    model_deploys = (ModelDeploy(MODEL_NAME, MODEL_NAME),)

    # Generation configuration
    stop_words: Sequence[Text] = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Model name
        self.model_name = (
            should_str_or_none(kwargs.get("model_name")) or self.MODEL_NAME
        )
        if not self.model_name:
            raise ValueError("The `model_name` cannot be empty")
        # Model and tokenizer
        self.model: "PreTrainedModel" = AutoModelForCausalLM.from_pretrained(
            self.model_name, torch_dtype=torch.float16, trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True
        )

    def name(self):
        return "transformers_action"

    def text_completion(
        self, prompt: Text, *args, model: Text, **kwargs
    ) -> "Completion":
        # Validate parameters
        if not prompt:
            raise ValueError("The `prompt` cannot be empty")
        if model != self.model_name:
            logger.warning(
                f"The model `{model}` is not the same as the action's model `{self.model_name}`"
            )

        # Initialize completion response
        completion_res = Completion(
            id=str(uuid.uuid4()),
            choices=[],
            created=int(time.time()),
            model=self.model_name,
            object="text_completion",
        )

        # Prepare kwargs
        max_length = kwargs.get("max_tokens") or kwargs.get("max_length") or None
        if max_length is not None:
            kwargs["max_length"] = int(max_length)
        kwargs.pop("max_tokens", None)
        kwargs.pop("best_of", None)  # TODO: Implement best_of
        kwargs.pop("echo", None)  # TODO: Implement echo
        kwargs.pop("n", None)  # TODO: Implement n
        kwargs.pop("frequency_penalty", None)  # TODO: Implement frequency_penalty
        kwargs.pop("presence_penalty", None)  # TODO: Implement presence_penalty
        kwargs.pop("stream", None)  # TODO: Implement stream

        # Stopping criteria
        stop_criteria: Optional["StoppingCriteria"] = None
        if len(self.stop_words) > 0:
            stop_criteria = StopAtWordsStoppingCriteria.from_stop_words(
                self.stop_words, self.tokenizer
            )
            kwargs["stopping_criteria"] = StoppingCriteriaList([stop_criteria])

        # Tokenize prompt
        inputs = self.tokenizer(
            prompt, return_tensors="pt", return_attention_mask=False
        )
        input_ids: "torch.Tensor" = inputs["input_ids"]
        inputs_tokens_length = int(input_ids.shape[1])

        # Generate text completion
        outputs: "torch.Tensor" = self.model.generate(input_ids, **kwargs)
        outputs_tokens_length = outputs.shape[1]
        completed_text = self.tokenizer.batch_decode(outputs)[0]

        # Collect completion response
        finish_reason = "length"
        if stop_criteria is not None:
            finish_reason = stop_criteria.get_stop_reason() or finish_reason
        completion_choice = CompletionChoice(
            finish_reason=finish_reason,
            index=0,
            text=completed_text.replace(prompt, "", 1),
        )
        completion_res.choices.append(completion_choice)
        completion_res.usage = CompletionUsage(
            total_tokens=outputs_tokens_length,
            prompt_tokens=inputs_tokens_length,
            completion_tokens=outputs_tokens_length - inputs_tokens_length,
        )
        completion_res.created = int(time.time())
        return completion_res


class HuggingFaceAction(TransformersAction):
    def name(self):
        return "hugging_face_action"
