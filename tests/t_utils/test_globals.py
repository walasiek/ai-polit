from aipolit.utils.globals import \
     AIPOLIT_DATA_DIR, \
     AIPOLIT_TWEET_GENERATORS_ROOT_DIR, \
     AIPOLIT_SEJM_ELECTION_DATA_DIR, \
     AIPOLIT_SEJM_ELECTION_RAW_DATA_DIR, \
     AIPOLIT_SEJM_ELECTION_VOTING_PLACE_RAW_DATA_FP, \
     AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR, \
     AIPOLIT_SEJM_ELECTION_RAW_DATA_PERCENT_RESULTS_FP

import pytest
import os


@pytest.mark.parametrize(
    "data_path",
    [
        (AIPOLIT_DATA_DIR),
        (AIPOLIT_TWEET_GENERATORS_ROOT_DIR),
        (AIPOLIT_SEJM_ELECTION_DATA_DIR),
        (AIPOLIT_SEJM_ELECTION_RAW_DATA_DIR),
        (AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR),
    ])
def test_all_data_dirs_exists(data_path):
    assert os.path.isdir(data_path), f"Dir {data_path} not exists. Please create such dir so every script will work correctly"


@pytest.mark.parametrize(
    "data_fp",
    [
        (AIPOLIT_SEJM_ELECTION_VOTING_PLACE_RAW_DATA_FP),
        (AIPOLIT_SEJM_ELECTION_RAW_DATA_PERCENT_RESULTS_FP),
    ])
def test_all_data_files_exists(data_fp):
    assert os.path.isfile(data_fp), f"File {data_fp} not exists. Please check aipolit.utils.globals for instruction how to create a file"
