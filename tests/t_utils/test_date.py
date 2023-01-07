from aipolit.utils.date import get_now_text, get_today_text, text_to_date, date_to_text, text_to_datetime, datetime_to_text
import re
import pytest


def test_get_now_text():
    assert re.match(r"^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d$", get_now_text())


def test_get_today_text():
    assert re.match(r"^\d\d\d\d-\d\d-\d\d$", get_today_text())


@pytest.mark.parametrize(
    "date_text, expected",
    [
        ("2022-01-01", (2022, 1, 1)),
        ("2022-12-13", (2022, 12, 13)),
    ])
def test_text_to_date_and_back(date_text, expected):
    actual = text_to_date(date_text)

    assert actual.year == expected[0]
    assert actual.month == expected[1]
    assert actual.day == expected[2]

    actual_back_to_text = date_to_text(actual)

    assert actual_back_to_text == date_text


@pytest.mark.parametrize(
    "datetime_text, expected",
    [
        ("2022-01-01 01:02:03", (2022, 1, 1, 1, 2, 3)),
        ("2022-12-13 13:14:59", (2022, 12, 13, 13, 14, 59)),
    ])
def test_text_to_datetime_and_back(datetime_text, expected):
    actual = text_to_datetime(datetime_text)

    assert actual.year == expected[0]
    assert actual.month == expected[1]
    assert actual.day == expected[2]
    assert actual.hour == expected[3]
    assert actual.minute == expected[4]
    assert actual.second == expected[5]

    actual_back_to_text = datetime_to_text(actual)

    assert actual_back_to_text == datetime_text
