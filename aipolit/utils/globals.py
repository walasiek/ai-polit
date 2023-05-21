import os

# root dir to store all data from this project
AIPOLIT_DATA_DIR = os.path.join(os.getenv('HOME'), 'data/ai-polit')

# This will contain tweet generators (ttgen.*)
AIPOLIT_TWEET_GENERATORS_ROOT_DIR = os.path.join(AIPOLIT_DATA_DIR, 'tweet-generators')

# This will contain geolocation data for elections
AIPOLIT_SEJM_ELECTION_DATA_DIR = os.path.join(AIPOLIT_DATA_DIR, 'sejm2019-election')

# Here you should download raw data from election:
# https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/dane_w_arkuszach -> Wyniki głosowania na kandydatów -> po obwodach Sejm CSV
# unzip the file
AIPOLIT_SEJM_ELECTION_RAW_DATA_DIR = os.path.join(AIPOLIT_SEJM_ELECTION_DATA_DIR, 'raw-results')

# Here will be placed data of each voting place
AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR = os.path.join(AIPOLIT_SEJM_ELECTION_DATA_DIR, 'voting-place')

# Here you should download raw data from election voting places
# https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/dane_w_arkuszach
# Obwody głosowania -> CSV
# unzip the file
AIPOLIT_SEJM_ELECTION_VOTING_PLACE_RAW_DATA_FP = os.path.join(AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR, 'obwody_glosowania.csv')
