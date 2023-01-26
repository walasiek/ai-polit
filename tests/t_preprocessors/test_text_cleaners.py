import pytest
from aipolit.preprocessors.text_cleaners import \
     remove_emojis, \
     remove_emails, \
     remove_non_alphanumeric, \
     remove_urls


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Text without emoji", "Text without emoji"),
        ("No emoji but traditional emoticon :-)", "No emoji but traditional emoticon :-)"),
        ("Text and emoji 😀", "Text and emoji "),
        ("Text and 😀 emoji", "Text and  emoji"),
        ("Text and😀emoji", "Text andemoji"),
        ("😀 Text and emoji", " Text and emoji"),
        ("😀", ""),
        ("2022 🇵🇱", "2022 "),
    ])
def test_remove_emojis(input_text, expected_text):
    assert expected_text == remove_emojis(input_text)


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Text without url", "Text without url"),
        ("www.example.com", "www.example.com"), # not supported by default
        ("http://www.example.com", ""),
        ("https://www.example.com", ""),
        ("HTTPS://www.example.com", ""),
        ("HTTPS://www.example.com/a/a/v.html", ""),
        ("HTTPS://www.example.com/a/a/v.html?a=4&c=1", ""),
        ("before HTTPS://www.example.com/a/a/v.html?a=4&c=1 after", "before  after"),
    ])
def test_remove_urls(input_text, expected_text):
    assert expected_text == remove_urls(input_text)


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Text without email", "Text without email"),
        ("john@example.com", ""),
        ("before john@example.com after", "before  after"),
    ])
def test_remove_emails(input_text, expected_text):
    assert expected_text == remove_emails(input_text)


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Text without email", "Text without email"),
        ("Who are you?", "Who are you"),
        ("Mr. 123", "Mr 123"),
    ])
def test_remove_non_alphanumeric(input_text, expected_text):
    assert expected_text == remove_non_alphanumeric(input_text)
