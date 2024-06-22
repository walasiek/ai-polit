from typing import Union, List, Tuple
from hipisejm.stenparser.transcript import SpeechReaction, SpeechInterruption
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
        if isinstance(utt, str):
            return self.split_string_to_sentences(utt)
        elif isinstance(utt, SpeechReaction):
            return self.split_string_to_sentences(utt.reaction_text)
        elif isinstance(utt, SpeechInterruption):
            return self.split_string_to_sentences(utt.text)
        else:
            raise ValueError(f"Unknown object utt in SessionSpeech: {utt}")

    def split_string_to_sentences(self, text: str) -> List[Tuple[str, int]]:
        raw_split = self.splitter.split(text=text)
        current_index = 0
        result = []
        for sent in raw_split[:-1]:
            result.append((sent, current_index))
            current_leftover = text[current_index + len(sent):]
            current_leftover_strip = current_leftover.lstrip()

            current_index = current_index + len(sent) + (len(current_leftover) - len(current_leftover_strip))
        result.append((raw_split[-1], current_index))

        return result
