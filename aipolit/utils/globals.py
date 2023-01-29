import os

# root dir to store all data from this project
TT_DATA_DIR = os.path.join(os.getenv('HOME'), 'data/ai-polit')

# This will contain tweet generators (ttgen.*)
TT_TWEET_GENERATORS_ROOT_DIR = os.path.join(TT_DATA_DIR, 'tweet-generators')
