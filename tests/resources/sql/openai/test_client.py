from typing import Text

from languru.resources.sql.openai.backend import OpenaiBackend


def test_openai_backend(session_id_fixture: Text):
    openai_backend = OpenaiBackend(url="sqlite:///:memory:")
    openai_backend.touch()
