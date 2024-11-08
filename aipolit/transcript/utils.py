import os
import re

from aipolit.utils.globals import AIPOLIT_10TERM_SEJM_TRANSCRIPTS_DIR
from hipisejm.stenparser.transcript import SessionTranscript


def load_transcripts(fixed_dir=None):
    """
    Loads transcripts from given directory.

    If fixed_dir is not None, then uses this dir with files
    Otherwise it uses: default AIPOLIT_10TERM_SEJM_TRANSCRIPTS_DIR
    """
    TRANSCRIPT_TYPE_TO_PROCESS = 'sejm'

    processing_dir = fixed_dir
    if processing_dir is None:
        processing_dir=os.path.join(AIPOLIT_10TERM_SEJM_TRANSCRIPTS_DIR, TRANSCRIPT_TYPE_TO_PROCESS)

    print("AAAAAAAAAA", processing_dir)
    transcripts = []
    for filename in sorted(os.listdir(processing_dir)):
        if re.match(r"^.*\.xml$", filename):
            filepath = os.path.join(processing_dir, filename)
            transcript = SessionTranscript()
            transcript.load_from_xml(filepath)
            transcripts.append(transcript)

    return transcripts
