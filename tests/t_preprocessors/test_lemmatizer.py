import pytest
from aipolit.preprocessors.lemmatizer import PLLemmatizer


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Ala ma kota", "ala mieć kot"),
        ("Ala ma kota 😀", "ala mieć kot 😀"),
        ("Ala ma kota #kłamstwa", "ala mieć kot # kłamstwo"),
        ("Ala ma @Kłamstwa", "ala mieć @Kłamstwo"),
        ("Kiedy biegałaś z Marcinem?", "kiedy biegać z Marcin ?"),
        ("Kiedy byłaś z Marcinem?", "kiedy być z Marcin ?"),
        ("Kiedy byliśmy z Marcinem?", "kiedy być z Marcin ?"),
    ])
def test_simple_pl_lemmatizer(input_text, expected_text):
    lemmatizer = PLLemmatizer.get_instance()

    actual = lemmatizer.process_text(
        input_text,
        ignore_tt_usernames_and_hashes=False,
        ignore_emojis=False,
    )

    assert expected_text == actual


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Ala ma kota #kłamstwa", "ala mieć kot #kłamstwa"),
        ("Ala ma @Kłamstwa", "ala mieć @Kłamstwa"),
    ])
def test_pl_lemmatizer_preserve_hashes(input_text, expected_text):
    lemmatizer = PLLemmatizer.get_instance()

    actual = lemmatizer.process_text(
        input_text,
        ignore_tt_usernames_and_hashes=True,
        ignore_emojis=False,
    )

    assert expected_text == actual


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        ("Ala ma kota 😀", "ala mieć kot 😀"),
    ])
def test_pl_lemmatizer_preserve_emojis(input_text, expected_text):
    lemmatizer = PLLemmatizer.get_instance()

    actual = lemmatizer.process_text(
        input_text,
        ignore_tt_usernames_and_hashes=False,
        ignore_emojis=True,
    )

    assert expected_text == actual
