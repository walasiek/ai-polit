from typing import Union, List
from hipisejm.stenparser.transcript import SpeechReaction, SpeechInterruption
from sentence_splitter import SentenceSplitter


class UttSentenceSplitter:
    """
    Splits <utt> objects of the speech to sentences.
    Uses SentenceSplitter module for segmentation.
    """
    def __init__(self):
        self.splitter = SentenceSplitter(language='pl')

    def split_utt_to_sentences(self, utt: Union[str, SpeechReaction, SpeechInterruption]) -> List[str]:
        if isinstance(utt, str):
            return self.split_string_to_sentences(utt)
        elif isinstance(utt, SpeechReaction):
            return self.split_string_to_sentences(utt.reaction_text)
        elif isinstance(utt, SpeechInterruption):
            return self.split_string_to_sentences(utt.text)
        else:
            raise ValueError(f"Unknown object utt in SessionSpeech: {utt}")

    def split_string_to_sentences(self, text: str) -> List[str]:
        return self.splitter.split(text=text)
