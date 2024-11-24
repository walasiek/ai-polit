import pytest
from aipolit.transcript.transcript_speaker_affiliation import TranscriptSpeakerAffiliation
from aipolit.transcript.person_affiliation import PersonAffiliation
from aipolit.transcript.utils import load_transcripts


sample_transcript_dir = "resources/test_data/transcripts_sejm"
person_affiliation = PersonAffiliation()
transcript_speaker_affiliation = TranscriptSpeakerAffiliation(person_affiliation)


def test_create_affiliation_to_utts_from_transcripts():
    transcipts = load_transcripts(fixed_dir=sample_transcript_dir)
    affiliation_to_entries = transcript_speaker_affiliation.create_affiliation_to_utts_from_transcripts(transcipts)

    for party in ['KO', 'PiS', 'PL2050', 'Konfederacja', 'Lewica', 'PSL']:
        assert party in affiliation_to_entries, f"Party {party} should be returned in affiliation_to_entries"

    pis_entries = affiliation_to_entries['PiS']

    # first is rather regular
    pis_speech1 = pis_entries[0]

    assert pis_speech1['canon_name'] == 'Łukasz Kmita', "first speech PiS - canon name"
    assert pis_speech1['speaker_name'] == 'Sekretarz Poseł Łukasz Kmita', "first speech PiS - raw speaker name"
    assert pis_speech1['utts_raw'] == "Panie Marszałku! Wysoka Izbo! Uprzejmie informuję, że dziś odbędą się posiedzenia Komisji: — Rolnictwa i Rozwoju Wsi – godz. 10.30, — Energii, Klimatu i Aktywów Państwowych wspólnie z Komisją Ochrony Środowiska, Zasobów Naturalnych i Leśnictwa – godz. 11, — do Spraw Służb Specjalnych – godz. 11, — do Spraw Unii Europejskiej – godz. 11, — Etyki Poselskiej – godz. 11, — Finansów Publicznych – godz. 11.30, — Regulaminowej, Spraw Poselskich i Immunitetowych – godz. 12, — do Spraw Unii Europejskiej – godz. 14, — Samorządu Terytorialnego i Polityki Regionalnej – godz. 14, — Zdrowia – godz. 14, — do Spraw Energii, Klimatu i Aktywów Państwowych – godz. 15, — do Spraw Petycji – godz. 15, — Kultury Fizycznej, Sportu i Turystyki – godz. 16, — Obrony Narodowej – godz. 16, — Rolnictwa i Rozwoju Wsi – godz. 17, — Obrony Narodowej – godz. 17.30, — Sprawiedliwości i Praw Człowieka – godz. 19. Jednocześnie informuję, że harmonogram planowanych posiedzeń zespołów parlamentarnych dostępny jest w Systemie Informacyjnym Sejmu. Bardzo dziękuję.", "first speech PiS - utts"

    # in the testing data 3rd speech from piS is interesting because it is interrupted by Marszałek (so the speeches should be merged)
    pis_speech3 = pis_entries[2]

    assert pis_speech3['canon_name'] == 'Robert Telus', "3rd speech PiS - canon name"
    assert pis_speech3['speaker_name'] == 'Poseł Robert Telus', "3rd speech PiS - raw speaker name"

    assert pis_speech3['utts_raw'].startswith("Będę musiał jeszcze raz powtórzyć to, co mówiłem,"), "3rd speech PiS - utts raw start"
    assert pis_speech3['utts_raw'].endswith("To nie jest zwijanie europejskiego i polskiego rolnictwa, ale to jest jego zabicie. Jesteśmy temu przeciwni."), "3rd speech PiS - utts raw end"


def test_create_affiliation_to_utts_from_transcripts_with_only_process_parties():
    transcipts = load_transcripts(fixed_dir=sample_transcript_dir)
    affiliation_to_entries = transcript_speaker_affiliation.create_affiliation_to_utts_from_transcripts(transcipts, only_process_parties=['KO', 'PiS'])

    for party in ['KO', 'PiS']:
        assert party in affiliation_to_entries, f"Party {party} should be returned in affiliation_to_entries"

    for party in ['PL2050', 'Konfederacja', 'Lewica', 'PSL']:
        assert party not in affiliation_to_entries, f"Party {party} should NOT be returned in affiliation_to_entries"
