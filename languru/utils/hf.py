from typing import Sequence, Text, Union

import torch
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast, StoppingCriteria


class StopAtWordsStoppingCriteria(StoppingCriteria):

    def __init__(self, stop_words_ids: Sequence["torch.LongTensor"]):
        """Create a stopping criteria that stops when the model generates a
        sequence of tokens that matches any of the stop words.

        Parameters
        ----------
        stop_words_ids: Sequence["torch.LongTensor"]
            A sequence of token ids to stop at. e.g.: [tensor(50256, device='mps:0'), tensor([  58,   47, 2885,   60])]
        """

        super().__init__()

        self.stop_words_ids = stop_words_ids

    def __call__(self, input_ids: "torch.LongTensor", scores: "torch.FloatTensor"):
        for stop_words_id in self.stop_words_ids:
            if torch.all((stop_words_id == input_ids[0][-len(stop_words_id) :])).item():
                return True
        return False

    @classmethod
    def from_stop_words(
        cls,
        stop_words: Sequence[Text],
        tokenizer: Union["PreTrainedTokenizer", "PreTrainedTokenizerFast"],
    ) -> "StopAtWordsStoppingCriteria":
        """Create a stopping criteria from a sequence of stop words.

        Parameters
        ----------
        stop_words: Sequence[Text]
            A sequence of stop words. e.g.: ["[END]", "[STOP]"
        tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast
            A tokenizer to convert the stop words to token ids.

        Returns
        -------
        StopAtWordsStoppingCriteria
            A stopping criteria that stops when the model generates
            a sequence of tokens that matches any of the stop words.
        """

        if not stop_words:
            raise ValueError("The `stop_words` cannot be empty")

        stop_words_ids = [
            tokenizer(stop_word, return_tensors="pt")["input_ids"].squeeze()
            for stop_word in stop_words
        ]
        return cls(stop_words_ids=stop_words_ids)