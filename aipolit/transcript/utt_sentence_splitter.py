from typing import Union, List, Tuple
from hipisejm.stenparser.transcript import SpeechReaction, SpeechInterruption
from hipisejm.stenparser.transcript_utils import get_utt_text
from sentence_splitter import SentenceSplitter


class UttSentenceSplitter:
    """
    Splits <utt> objects of the speech to sentences.
    Uses SentenceSplitter module for segmentation.

    WARNING: Due to limitations of SentenceSplitter assumes that text splitted is normalized in terms of spaces, so there are NO:
    - spaces in the beginning or ending
    - double/triple etc. spaces

    If such thing will occur then sentence_int positions will be computed incorrectly :(
    """
    def __init__(self):
        self.splitter = SentenceSplitter(language='pl')

    def split_utt_to_sentences(self, utt: Union[str, SpeechReaction, SpeechInterruption]) -> List[Tuple[str, int]]:
        return self.split_string_to_sentences(get_utt_text(utt))

    def estimate_start_index_of_each_sentence_matching(self, utt: Union[str, SpeechReaction, SpeechInterruption], raw_split: List[str]) -> List[int]:
        text = get_utt_text(utt)
        current_index = 0
        result = []
        for sent in raw_split[:-1]:
            result.append(current_index)
            current_leftover = text[current_index + len(sent):]
            current_leftover_strip = current_leftover.lstrip()

            current_index = current_index + len(sent) + (len(current_leftover) - len(current_leftover_strip))
        if len(raw_split) > 0:
            result.append(current_index)
        return result

    def split_string_to_sentences(self, text: str) -> List[str]:
        return self.splitter.split(text=text)
