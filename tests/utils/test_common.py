from languru.utils.common import remove_punctuation


def test_remove_punctuation():
    assert remove_punctuation("Hello, World!") == "Hello World"
    assert remove_punctuation("Hello, World！") == "Hello World"
    assert remove_punctuation("Hello, World❤️", extra_punctuation="❤️") == "Hello World"
