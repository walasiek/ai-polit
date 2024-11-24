import pytest
from aipolit.transcript.transcript_speaker_affiliation import TranscriptSpeakerAffiliation
from aipolit.transcript.person_affiliation import PersonAffiliation
from aipolit.transcript.utils import load_transcripts


sample_data_fp = "resources/test_data/political-affiliation/sejm.json"
dummy_person_affiliation = PersonAffiliation(fixed_filepath=sample_data_fp)
dummy_transcript_speaker_affiliation = TranscriptSpeakerAffiliation(dummy_person_affiliation)
sample_transcript_dir = "resources/test_data/transcripts_sejm"


@pytest.mark.parametrize(
    "input_text, input_date_txt, expected_text",
    [
        ("Jan Kowalski", "2024-12-31", "X"),
        ("Jan Nowak", "2024-09-30", "X"),
        ("Jan Nowak", "2024-10-01", "Y"),
        ("Jan Nowak", "2024-10-02", "Y"),
        ("Jan Nowak", "2024-11-01", "Z"),
        ("Jan Nowak", "2024-11-02", "Z"),
        ("Jan Kropek", "2024-11-02", "X"),
    ])
def test_dummy_affiliation_basic(input_text, input_date_txt, expected_text):
    actual_affiliation = dummy_transcript_speaker_affiliation.assign_affiliation(
        input_text,
        when_txt=input_date_txt)

    assert actual_affiliation is not None, "affiliation is defined"
    assert actual_affiliation == expected_text, "Affiliation correct as expected"


@pytest.mark.parametrize(
    "input_text, input_date_txt",
    [
        ("Jan Kowalski", "1990-12-31"),
        ("JanKowalski", "2024-12-31"),
        ("JanKowalski", "2024-12-31"),
        ("Jan Smith", "2024-12-31"),
    ])
def test_dummy_affiliation_no_club(input_text, input_date_txt):
    actual_affiliation = dummy_transcript_speaker_affiliation.assign_affiliation(
        input_text,
        when_txt=input_date_txt)

    assert actual_affiliation is None, "affiliation should be not defined"


@pytest.mark.parametrize(
    "input_text, input_date_txt, expected_text",
    [
        ("Poseł Jan Kowalski", "2024-12-31", "X"),
        ("Marszałek Sejmu Jan Kowalski", "2024-12-31", "X"),
        ("Przedstawiciel wnioskodawców inicjatywy ustawodawczej społecznego komitetu Odnowa Jan Kowalski", "2024-12-31", "X"),
    ])
def test_dummy_affiliation_with_prefix(input_text, input_date_txt, expected_text):
    actual_affiliation = dummy_transcript_speaker_affiliation.assign_affiliation(
        input_text,
        when_txt=input_date_txt)

    assert actual_affiliation is not None, "affiliation is defined"
    assert actual_affiliation == expected_text, "Affiliation correct as expected"


@pytest.mark.parametrize(
    "input_text, input_date_txt",
    [
        ("Jan Kowalski poseł", "2024-12-31"),
        ("Jan Kowalski-", "2024-12-31"),
    ])
def test_dummy_affiliation_with_suffix_no_club(input_text, input_date_txt):
    actual_affiliation = dummy_transcript_speaker_affiliation.assign_affiliation(
        input_text,
        when_txt=input_date_txt)

    assert actual_affiliation is None, "affiliation should be not defined"


@pytest.mark.parametrize(
    "input_text, input_date_txt, expected_text",
    [
        ("Jan kowalski", "2024-12-31", "X"),
        ("jan Kowalski", "2024-12-31", "X"),
        ("jan kowalski", "2024-12-31", "X"),
        ("JAN KOWALSKI", "2024-12-31", "X"),
    ])
def test_dummy_affiliation_ignore_letter_case(input_text, input_date_txt, expected_text):
    actual_affiliation = dummy_transcript_speaker_affiliation.assign_affiliation(
        input_text,
        when_txt=input_date_txt)

    assert actual_affiliation is not None, "affiliation is defined"
    assert actual_affiliation == expected_text, "Affiliation correct as expected"


@pytest.mark.parametrize(
    "input_text, input_date_txt, expected_text",
    [
        ("Leopold Maria Nowak", "2024-12-31", "X"), # two names match
        ("Leopold Nowak", "2024-12-31", "X"), # two names match, 2nd name is not in transcript, but it is in DB
        ("Jan Marian Kowalski", "2024-12-31", "X"), # two names match, 2nd name is in transcript, but it is NOT in DB
    ])
def test_dummy_affiliation_real_examples(input_text, input_date_txt, expected_text):
    actual_affiliation = dummy_transcript_speaker_affiliation.assign_affiliation(
        input_text,
        when_txt=input_date_txt)

    assert actual_affiliation is not None, "affiliation is defined"
    assert actual_affiliation == expected_text, "Affiliation correct as expected"
