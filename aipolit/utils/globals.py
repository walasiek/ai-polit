import os

# root dir to store all data from this project
AIPOLIT_DATA_DIR = os.path.join(os.getenv('HOME'), 'data/ai-polit')

# This will contain tweet generators (ttgen.*)
AIPOLIT_TWEET_GENERATORS_ROOT_DIR = os.path.join(AIPOLIT_DATA_DIR, 'tweet-generators')
