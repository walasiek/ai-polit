import pytest
from aipolit.preprocessors.tweet_cleaners import remove_users_from_beg


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Text without user", "Text without user"),
        ("Text user @johndoe", "Text user @johndoe"),
        ("@johndoe1 @johndoe2 @johndoe3 Text user @johndoe", "Text user @johndoe"),
        ("@johndoe1 Text user @johndoe", "Text user @johndoe"),
        (".@johndoe1 Text user @johndoe", ".@johndoe1 Text user @johndoe"),
    ])
def test_remove_users_from_beg(input_text, expected_text):
    assert expected_text == remove_users_from_beg(input_text)
