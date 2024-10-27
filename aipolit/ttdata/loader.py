from aipolit.utils.text import read_tsv
from aipolit.utils.date import text_to_datetime


def load_tt_tsv_file(filepath):
    data = read_tsv(filepath)
    for entry in data:
        entry['datetime'] = text_to_datetime(entry['datetime'])
    return data
