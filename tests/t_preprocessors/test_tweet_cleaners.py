import pytest
from aipolit.preprocessors.tweet_cleaners import remove_users_from_beg, preserve_tokens, restore_tokens


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


@pytest.mark.parametrize(
    "input_text, expected_text, expected_cache",
    [
        ("Text without user", "Text without user", dict()),
        ("Text@user", "TextLEMTOKEN0", {'LEMTOKEN0': '@user'}),
        ("Text#hash", "TextLEMTOKEN0", {'LEMTOKEN0': '#hash'}),
        ("Text with @user", "Text with LEMTOKEN0", {'LEMTOKEN0': '@user'}),
        ("Text with #hash", "Text with LEMTOKEN0", {'LEMTOKEN0': '#hash'}),
        ("Text with @user and #hash", "Text with LEMTOKEN0 and LEMTOKEN1", {'LEMTOKEN0': '@user', 'LEMTOKEN1': '#hash'}),
        ("Text with @user and #hash and 😀", "Text with LEMTOKEN0 and LEMTOKEN1 and LEMTOKEN2", {'LEMTOKEN0': '@user', 'LEMTOKEN1': '#hash', "LEMTOKEN2": '😀'}),
        ("Text nospace😀", "Text nospaceLEMTOKEN0", {'LEMTOKEN0': '😀'}),
        ("Text 😀😀😀😀😀😀", "Text LEMTOKEN0", {'LEMTOKEN0': '😀😀😀😀😀😀'}),
    ])
def test_preserve_tokens(input_text, expected_text, expected_cache):
    actual_text, actual_cache = preserve_tokens(input_text, with_tt_usernames_and_hashes=True, with_emojis=True)
    assert expected_text == actual_text
    assert expected_cache == actual_cache

    restored_text = restore_tokens(actual_text, actual_cache)
    assert input_text == restored_text
