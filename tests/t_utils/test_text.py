import pytest
import tempfile
import os
from aipolit.utils.text import emojize_case_insensitive, save_list_as_tsv, read_tsv, save_dict_as_tsv, load_dict_from_tsv


@pytest.mark.parametrize(
    "input_text, expected_text",
    [
        (":germany:", "🇩🇪"),
        (":Germany:", "🇩🇪"),
        (":germany::Germany:", "🇩🇪🇩🇪"),
        (":Germany::Germany:", "🇩🇪🇩🇪"),
        (":Germany::germany:", "🇩🇪🇩🇪"),
        (":Germany: :germany:", "🇩🇪 🇩🇪"),
        (":such_token_does_not_exist:", ":such_token_does_not_exist:"),
        ("No emojis here:", "No emojis here:"),
        ("", ""),
        ("::", "::"),
        (":?:", ":?:"),
    ])
def test_emojize_case_insensitive(input_text, expected_text):
    actual = emojize_case_insensitive(input_text)
    assert expected_text == actual


@pytest.mark.parametrize(
    "test_list, header, expected_after_save",
    [
        (   # simple example
            [
                [1, '2'],
                [3, '4'],
            ],
            ['a', 'b'],
            [
                {'a': '1', 'b': '2'},
                {'a': '3', 'b': '4'},
            ]
        ),
    ])
def test_save_list_as_tsv(test_list, header, expected_after_save):
    with tempfile.TemporaryDirectory() as tmpdirname:
        fp = os.path.join(tmpdirname, "test.tsv")
        save_list_as_tsv(fp, test_list, header)
        actual = read_tsv(fp)
        assert actual == expected_after_save


@pytest.mark.parametrize(
    "input_dict, expected_dict",
    [
        (
            {'key1': '1', 'key2': '2'}, {'key1': '1', 'key2': '2'},
        ),
        (
            {'key1': 1, 'key2': 2}, {'key1': '1', 'key2': '2'},
        ),
        (
            {'key1': '', 'key2': None}, {'key1': '', 'key2': ''},
        ),
    ])
def test_save_load_dict_as_tsv(input_dict, expected_dict):
    with tempfile.TemporaryDirectory() as tmpdirname:
        fp = os.path.join(tmpdirname, "test.tsv")
        save_dict_as_tsv(fp, input_dict)
        actual_dict = load_dict_from_tsv(fp)
        assert actual_dict == expected_dict
