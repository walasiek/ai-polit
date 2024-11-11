import pytest

from aipolit.transcript.person_affiliation import PersonAffiliation


sample_data_fp = "resources/test_data/political-affiliation/sejm.json"
person_affiliation = PersonAffiliation(fixed_filepath=sample_data_fp)


def test_count_persons():
    assert person_affiliation.count() == 4

    assert person_affiliation.count(only_active=True) == 3


def test_club_simple():
    person = person_affiliation.get_person_by_name("Jan Kowalski")
    assert person is not None

    assert person.f_name == "Jan"
    assert person.s_name == "Kowalski"

    assert person.get_club() == "X"
    assert person.get_club(when="2024-10-01") == "X"
    assert person.get_club(when="2023-10-01") is None


def test_club_with_changes():
    person = person_affiliation.get_person_by_name("Jan Nowak")
    assert person is not None

    assert person.f_name == "Jan"
    assert person.s_name == "Nowak"

    assert person.get_club(when="2024-01-01") == "X"
    assert person.get_club(when="2024-10-01") == "Y"
    assert person.get_club(when="2024-10-05") == "Y"
    assert person.get_club(when="2024-11-01") == "Z"
    assert person.get_club(when="2024-11-03") == "Z"
    assert person.get_club() == "Z"


def test_club_with_changes_and_deactivation():
    person = person_affiliation.get_person_by_name("Jan Smith")
    assert person is not None

    assert person.get_club(when="2024-01-01") == "X"
    assert person.get_club(when="2024-10-01") == "Y"
    assert person.get_club(when="2024-10-05") == "Y"
    assert person.get_club(when="2024-10-31") == "Y"
    assert person.get_club(when="2024-11-01") is None
    assert person.get_club(when="2024-11-03") is None
    assert person.get_club() is None


def test_club_no_from_or_to():
    person = person_affiliation.get_person_by_name("Jan Kropek")
    assert person is not None

    assert person.get_club() == "X"
    assert person.get_club(when="2024-10-01") == "X"
    assert person.get_club(when="2023-10-01") == "X"
    assert person.get_club(when="2999-10-01") == "X"
    assert person.get_club(when="1222-10-01") == "X"
