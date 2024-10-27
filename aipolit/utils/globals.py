import os

# root dir to store all data from this project
AIPOLIT_DATA_DIR = os.path.join(os.getenv('HOME'), 'data/ai-polit')

# This will contain tweet generators (ttgen.*)
AIPOLIT_TWEET_GENERATORS_ROOT_DIR = os.path.join(AIPOLIT_DATA_DIR, 'tweet-generators')

#====================================
# SEJM 2019 ELECTIONS DATA
#====================================

# This will contain geolocation data for elections (sejm2019)
AIPOLIT_SEJM_ELECTION_DATA_DIR = os.path.join(AIPOLIT_DATA_DIR, 'sejm2019-election')

# Here you should download raw data from election:
# https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/dane_w_arkuszach -> Wyniki głosowania na kandydatów -> po obwodach Sejm CSV
# unzip the file
AIPOLIT_SEJM_ELECTION_RAW_DATA_DIR = os.path.join(AIPOLIT_SEJM_ELECTION_DATA_DIR, 'raw-results')

# Here you should download raw data from election voting results
# https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/dane_w_arkuszach
# Wyniki głosowania na listy Sejmowe -> po obwodach -> CSV
# unzip the file
AIPOLIT_SEJM_ELECTION_RAW_DATA_GENERAL_RESULTS_FP = os.path.join(AIPOLIT_SEJM_ELECTION_RAW_DATA_DIR, 'wyniki_gl_na_listy_po_obwodach_sejm.csv')

# Here will be placed data of each voting place
AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR = os.path.join(AIPOLIT_SEJM_ELECTION_DATA_DIR, 'voting-place')

# Here you should download raw data from election voting places
# https://sejmsenat2019.pkw.gov.pl/sejmsenat2019/pl/dane_w_arkuszach
# Obwody głosowania -> CSV
# unzip the file
AIPOLIT_SEJM_ELECTION_VOTING_PLACE_RAW_DATA_FP = os.path.join(AIPOLIT_SEJM_ELECTION_VOTING_PLACE_DATA_DIR, 'obwody_glosowania.csv')

#====================================
# PREZ 2020 ELECTIONS DATA
#====================================

# This will contain geolocation data for presidential elections
AIPOLIT_PREZ2020_ELECTION_DATA_DIR = os.path.join(AIPOLIT_DATA_DIR, 'prez2020-election')

# Here you should download raw data from election:
# https://prezydent20200628.pkw.gov.pl/prezydent20200628/pl/dane_w_arkuszach -> Wyniki głosowania na kandydatów w pierwszej turze wyborów -> po obwodach -> CSV
# unzip the files
AIPOLIT_PREZ2020_ELECTION_RAW_DATA_DIR = os.path.join(AIPOLIT_PREZ2020_ELECTION_DATA_DIR, 'raw-results')
AIPOLIT_PREZ2020_ELECTION_RAW_DATA_GENERAL_RESULTS_FP = os.path.join(AIPOLIT_PREZ2020_ELECTION_RAW_DATA_DIR, 'wyniki_gl_na_kand_po_obwodach_utf8.csv')

# Here will be placed data of each voting place
AIPOLIT_PREZ2020_ELECTION_VOTING_PLACE_DATA_DIR = os.path.join(AIPOLIT_PREZ2020_ELECTION_DATA_DIR, 'voting-place')

# Here you should download raw data from election voting places
# https://prezydent20200628.pkw.gov.pl/prezydent20200628/pl/dane_w_arkuszach
# Obwody głosowania w pierwszej turze wyborów -> CSV
# unzip the files
AIPOLIT_PREZ2020_ELECTION_VOTING_PLACE_RAW_DATA_FP = os.path.join(AIPOLIT_PREZ2020_ELECTION_VOTING_PLACE_DATA_DIR, 'obwody_glosowania_utf8.csv')

#====================================
# SEJM 2023 ELECTIONS DATA
#====================================

# This will contain geolocation data for elections (sejm2019)
AIPOLIT_SEJM2023_ELECTION_DATA_DIR = os.path.join(AIPOLIT_DATA_DIR, 'sejm2023-election')

# Here you should download raw data from election:
# https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach -> Wyniki głosowania na kandydatów -> po obwodach Sejm CSV
# unzip the file
AIPOLIT_SEJM2023_ELECTION_RAW_DATA_DIR = os.path.join(AIPOLIT_SEJM2023_ELECTION_DATA_DIR, 'raw-results')

# Here you should download raw data from election voting results
# https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach
# Wyniki głosowania na listy Sejmowe -> po obwodach -> CSV
# unzip the file
AIPOLIT_SEJM2023_ELECTION_RAW_DATA_GENERAL_RESULTS_FP = os.path.join(AIPOLIT_SEJM2023_ELECTION_RAW_DATA_DIR, 'wyniki_gl_na_listy_po_obwodach_sejm_utf8.csv')

# Here will be placed data of each voting place
AIPOLIT_SEJM2023_ELECTION_VOTING_PLACE_DATA_DIR = os.path.join(AIPOLIT_SEJM2023_ELECTION_DATA_DIR, 'voting-place')

# Here you should download raw data from election voting places
# https://wybory.gov.pl/sejmsenat2023/pl/dane_w_arkuszach
# Obwody głosowania -> CSV
# unzip the file
AIPOLIT_SEJM2023_ELECTION_VOTING_PLACE_RAW_DATA_FP = os.path.join(AIPOLIT_SEJM2023_ELECTION_VOTING_PLACE_DATA_DIR, 'obwody_glosowania_utf8.csv')

#====================================
# SEJM 2023+ Session Transcripts
#====================================

AIPOLIT_10TERM_SEJM_TRANSCRIPTS_DIR = os.path.join(AIPOLIT_DATA_DIR, 'hipisejm-transcripts')

#====================================
# Cache dir
#====================================

AIPOLIT_CACHE_DIR = os.path.join(AIPOLIT_DATA_DIR, "cache")
