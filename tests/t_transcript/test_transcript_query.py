import pytest
from aipolit.transcript.transcript_query import TranscriptQuery


sample_transcript_dir = "resources/test_data/transcripts_sejm"
transcript_query = TranscriptQuery(
    fixed_transcript_dir=sample_transcript_dir)


def test_simple_query():
    assert transcript_query.count_transcripts() == 1, "Check if no of transcripts loaded correctly"

@pytest.mark.parametrize(
    "what_to_dump, expected_count, first_element, last_element",
    [
        ('speech_speaker', 318, 'Marszałek Szymon Hołownia', 'Wicemarszałek Krzysztof Bosak'),
        ('utt', 1103, 'Otwieram posiedzenie.', 'Oklaski'),
        ('utt_norm', 614, 'Otwieram posiedzenie.', 'Dziękuję bardzo, pani poseł. Na tym zakończyliśmy oświadczenia poselskie . Zarządzam przerwę w posiedzeniu do jutra, tj. do 22 lutego 2024 r., do godz. 9. Dobrej nocy.'),
        ('utt_interrupt', 223, 'Sprzeciw.', 'Brawo!'),
        ('utt_interrupt_by', 223, 'Poseł Grzegorz Braun', 'Głos z sali'),
        ('utt_reaction', 266, 'Marszałek trzykrotnie uderza laską marszałkowską', 'Oklaski'),
    ])
def test_query_with_what(what_to_dump, expected_count, first_element, last_element):
    dumped = []
    transcript_query.query(what_to_dump=what_to_dump, to_list=dumped)

    assert len(dumped) == expected_count, f"{what_to_dump} expected_count = {expected_count} actual {len(dumped)}"
    assert dumped[0] == first_element, f"{what_to_dump} first element = {first_element}"
    assert dumped[-1] == last_element, f"{what_to_dump} last element = {last_element}"
