from pathlib import Path
from typing import Text

import requests

from languru.action.openai import OpenaiAction
from languru.utils.common import remove_punctuation

test_chat_model_name = "gpt-3.5-turbo"
test_text_completion_model_name = "gpt-3.5-turbo-instruct"
test_embedding_model_name = "text-embedding-3-small"
test_moderation_model_name = "text-moderation-latest"
test_sentence = "你好"
test_tts_model_name = "tts-1"
test_tts_voice = "nova"
test_tts_language = "zh"
test_asr_model_name = "whisper-1"
test_image_model_name = "dall-e-2"


def test_openai_action_health():
    action = OpenaiAction()
    assert action.name() == "openai_action"
    assert action.health() is True


def test_openai_action_chat():
    action = OpenaiAction()
    chat_completion = action.chat(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    )
    assert chat_completion.choices[0].message.content


def test_openai_action_chat_stream():
    action = OpenaiAction()
    answer = ""
    for chat_chunk in action.chat_stream(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ],
        model=test_chat_model_name,
    ):
        if chat_chunk.choices[0].delta.content:
            answer += chat_chunk.choices[0].delta.content
    assert answer


def test_openai_action_text_completion():
    action = OpenaiAction()
    text_completion = action.text_completion(
        prompt="The reverse of a dog is a",
        model=test_text_completion_model_name,
        max_tokens=20,
    )
    assert text_completion.choices[0].text


def test_openai_action_text_completion_stream():
    action = OpenaiAction()
    answer = ""
    for text_chunk in action.text_completion_stream(
        prompt="The reverse of a dog is a",
        model=test_text_completion_model_name,
        max_tokens=20,
    ):
        if text_chunk.choices[0].text:
            answer += text_chunk.choices[0].text
    assert answer


def test_openai_action_embeddings():
    action = OpenaiAction()
    embedding = action.embeddings(
        input=[
            "Discover your spirit of adventure and indulge your thirst for "
            + "wanderlust with the touring bike that has dominated the segment "
            + "for the past 50 years: the Honda Gold Wing Tour, Gold Wing Tour "
            + "Automatic DCT, and Gold Wing Tour Airbag Automatic DCT.",
            "R1M: This is the most advanced production motorcycle for riders "
            + "who are at the very top of their game.",
        ],
        model=test_embedding_model_name,
    )
    assert len(embedding.data[0].embedding) == 1536


def test_openai_action_moderation():
    action = OpenaiAction()
    moderation = action.moderations(
        input="I am a helpful assistant.",
        model=test_moderation_model_name,
    )
    for res in moderation.results:
        assert res.categories.harassment is False
        assert res.categories.hate is False
        assert res.categories.self_harm is False
        assert res.categories.sexual is False
        assert res.categories.violence is False
        assert res.flagged is False
        assert res.category_scores.harassment < 0.001
        assert res.category_scores.hate < 0.001
        assert res.category_scores.self_harm < 0.001


def test_openai_action_audio_speech(session_id_fixture: Text):
    action = OpenaiAction()
    audio_filepath = Path(f"data/test_audio_speech_{session_id_fixture}.mp3")
    audio_filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(audio_filepath, "wb") as f:
        for data in action.audio_speech(
            input=test_sentence,
            model=test_tts_model_name,
            voice=test_tts_voice,
        ):
            f.write(data)
    assert audio_filepath.exists()


def test_openai_action_audio_transcriptions(session_id_fixture: Text):
    action = OpenaiAction()
    audio_filepath = Path(f"data/test_audio_speech_{session_id_fixture}.mp3")
    assert audio_filepath.exists()
    transcription_res = action.audio_transcriptions(
        file=audio_filepath,
        model=test_asr_model_name,
        language=test_tts_language,
        temperature=0.0,
    )
    assert remove_punctuation(transcription_res.text) == remove_punctuation(
        test_sentence
    )


def test_openai_action_audio_translations(session_id_fixture: Text):
    action = OpenaiAction()
    audio_filepath = Path(f"data/test_audio_speech_{session_id_fixture}.mp3")
    assert audio_filepath.exists()
    translation_res = action.audio_translations(
        file=audio_filepath,
        model=test_asr_model_name,
        temperature=0.0,
    )
    assert remove_punctuation(translation_res.text) == remove_punctuation(test_sentence)


def test_openai_action_images_generations(session_id_fixture: Text):
    action = OpenaiAction()
    image_filepath = Path(f"data/test_image_{session_id_fixture}.png")
    image_filepath.parent.mkdir(parents=True, exist_ok=True)
    image_res = action.images_generations(
        prompt="A cute baby sea otter",
        model=test_image_model_name,
        size="256x256",
    )
    assert image_res.data[0].url is not None
    # Download image in to file
    with open(image_filepath, "wb") as f:
        response = requests.get(image_res.data[0].url, stream=True)
        response.raise_for_status()
        f.write(response.content)
