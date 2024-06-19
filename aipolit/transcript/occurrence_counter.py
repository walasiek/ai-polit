import re
from tqdm import tqdm
from typing import Union, Optional, List
from sentence_splitter import SentenceSplitter
from hipisejm.stenparser.transcript import SessionTranscript, SpeechReaction, SpeechInterruption, SessionSpeech


def get_speaker_for_utt(utt, speech):
    """
    Helper method for Transcript processing
    """
    if isinstance(utt, str):
        return speech.speaker
    elif isinstance(utt, SpeechReaction):
        return None
    elif isinstance(utt, SpeechInterruption):
        return utt.interrupted_by_speaker
    else:
        raise ValueError(f"Unknown object utt in SessionSpeech: {utt}")


class PhraseOccurence:
    """
    Represents single occurrence of the phrase/word we are searching for.
    """
    def __init__(self,
                 speaker: str,
                 sentence: str,
                 utt_ref: Union[str, SpeechReaction, SpeechInterruption],
                 speech_ref: SessionSpeech,
                 prev_sentence: Optional[str],
                 prev_sentence_speaker: Optional[str]):
        self.speaker = speaker
        self.sentence = sentence
        self.utt_ref = utt_ref
        self.speech_ref = speech_ref
        self.prev_sentence = prev_sentence
        self.prev_sentence_speaker = prev_sentence_speaker

    def __str__(self):
        full_txt = f"{self.speaker}: {self.sentence}"

        if isinstance(self.utt_ref, SpeechInterruption):
            inter_txt = f" (przerywając wypowiedź <{self.prev_sentence_speaker}> o treści: {self.prev_sentence})"
            full_txt = full_txt + inter_txt
        return full_txt


class ListOccurrenceCounter:
    """
    This class counts occurrences of fixed list of phrases / words in the given transcript.
    """
    def __init__(self, searched_tokens: List[str]):
        self.searched_tokens = searched_tokens
        self.splitter = SentenceSplitter(language='pl')
        self.searched_regex = self._create_searched_regex()
        # cache objects
        self.cache = dict()
        self._init_cache()

    def run_count(self, transcript: SessionTranscript):
        """
        Returns list of counted occurrencies.
        Steps:
        1. Split into sentences using sentence-splitter
        2. Regex search for "hańba" occurrencies (and some variants like inflecional forms)

        Returns list consisting of entries (occurrence).
        Each occurrence is a tuple:
        (speaker, sentence, utt_ref, speech_ref, prev_sentence, prev_sentence_speaker)

        Where:
        - speaker (str) - name of the speaker, who used "Hańba"
        - sentence (str) - sentence in which "Hańba" occured
        - utt_ref (str, SessionReaction, Session Interruption) - reference to full utterance object
        - speech_ref (SessionSpeech) - reference to full speech during which Hańba occurred
        - prev_sentence (str) - sentence preceeding occurrence of Hańba
        - prev_sentence_speaker (str) - speaker of the preceeding sentence (may be the same as speaker)
        """
        result = []
        self._init_cache()

        for session_speech in tqdm(transcript.session_content):
            self._count_in_speech(result, session_speech)

        return result

    def _create_searched_regex(self):
        regex_txt = r"\b(?:" + "|".join(self.searched_tokens) + r")\b"
        return re.compile(regex_txt, flags=re.IGNORECASE)

    def _init_cache(self):
        self.cache['prev_sentence'] = None
        self.cache['prev_utt'] = None
        self.cache['prev_utt_speech'] = None

    def _count_in_speech(self, result, session_speech):
        speech_speaker = session_speech.speaker
        for utt in session_speech.content:
            sentences = self._split_utt_to_sentences(utt)
            for sentence in sentences:
                self._check_searched_in_sentence(result, sentence, utt, session_speech)
                self.cache['prev_sentence'] = sentence
            self.cache['prev_utt'] = utt
            self.cache['prev_utt_speech'] = session_speech

    def _split_utt_to_sentences(self, utt):
        if isinstance(utt, str):
            return self._split_string_to_sentences(utt)
        elif isinstance(utt, SpeechReaction):
            return self._split_string_to_sentences(utt.reaction_text)
        elif isinstance(utt, SpeechInterruption):
            return self._split_string_to_sentences(utt.text)
        else:
            raise ValueError(f"Unknown object utt in SessionSpeech: {utt}")

    def _split_string_to_sentences(self, text: str):
        return self.splitter.split(text=text)

    def _check_searched_in_sentence(self, result, sentence, utt, session_speech):
        pos = 0
        keep_procesing = True
        while keep_procesing:
            matched = self.searched_regex.search(sentence, pos=pos)
            if matched:
                keep_procesing = True
                pos = matched.start() + 1
                self._new_occurrence(result, sentence, utt, session_speech)
            else:
                keep_procesing = False
        return False

    def _new_occurrence(self, result, sentence, utt_ref, speech_ref):
        speaker = get_speaker_for_utt(utt_ref, speech_ref)
        prev_sentence = self.cache['prev_sentence']
        prev_sentence_speaker = get_speaker_for_utt(self.cache['prev_utt'], self.cache['prev_utt_speech'])
        occurrence = PhraseOccurence(speaker, sentence, utt_ref, speech_ref, prev_sentence, prev_sentence_speaker)
        result.append(occurrence)
