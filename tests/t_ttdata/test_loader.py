from aipolit.ttdata.loader import load_tt_tsv_file
import datetime


def test_load_tt_tsv_file():
    data = load_tt_tsv_file("resources/test_data/sample_tt_data.tsv")
    assert len(data) == 2
    assert type(data[0]['datetime']) is datetime.datetime
    assert data[1]['datetime'] > data[0]['datetime']
