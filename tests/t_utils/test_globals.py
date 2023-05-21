from aipolit.utils.globals import AIPOLIT_DATA_DIR, AIPOLIT_TWEET_GENERATORS_ROOT_DIR
import pytest
import os


@pytest.mark.parametrize(
    "data_path",
    [
        (AIPOLIT_DATA_DIR),
        (AIPOLIT_TWEET_GENERATORS_ROOT_DIR),
    ])
def test_all_data_dirs_exists(data_path):
    assert os.path.isdir(data_path), f"Dir {data_path} not exists. Please create such dir so every script will work correctly"
