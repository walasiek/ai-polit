import os
import hashlib
import openai
import logging


from keybert.llm import OpenAI
from keybert import KeyLLM
from diskcache import Cache
from aipolit.utils.globals import AIPOLIT_CACHE_DIR


class KeyBertLLMCached:
    """
    Wrapper to KeyBert LLM model, which allows to cache keywords retrieved by KeyBert on disk.
    This is to minimize cost of OpenAI ChatGPT usage!

    Some drawbacks:
    - the class does not check change of prompt (OPENAI_PROMPT) or ChatGPT model (CHAT_MODEL_TO_USE)
      if you want to change them, then please run .clear_cache() method manually (or remove cached dir manually)
    - the class uses md5 hash for document hashing (so there is small possibility of collision ;) )
    """
    MY_CACHE_DIR = "chatgpt-keybert-hanbazdrada"
    CHAT_MODEL_TO_USE = 'gpt-4o'
    OPENAI_PROMPT = """
Podam Ci listę fragmentów wypowiedzi polskich polityków.
Twoim zadaniem będzie streszczenie wypowiedzi danego polityka za pomocą kilku krótkich tematów.
Każdy temat powinien składać się z maksymalnie 3 słów i być frazą rzeczownikową, rzeczownikiem lub nazwą własną.
Tematy powinny dobrze podsumowywać o czym mowa w całości danej wypowiedzi, czyli pokrywać możliwie szeroki kontekst.
Tematy powinny być w języku polskim.
Znormalizuj pozyskane tematy do form podstawowych.
Odpowiedź wyłącznie za pomocą listy pozyskanych tematów oddzielonych przecinkiem.
Jeśli nie umiesz określić tematów, to zwróć frazę "brak tematów"

Dokument:
- Natomiast wiadomo, że wy stosujecie zasadę odwracania znaczeń słów i odznaczania znaczeń sytuacji. Wy nieustannie próbujecie uznać się za opozycję demokratyczną, a macie do tego dokładnie takie samo prawo jak Blok Demokratyczny z lat 40. Dokładnie takie samo prawo. A nawet dzisiaj posuwacie się już dalej niż oni, bo oni przynajmniej formalnie nie deklarowali, że zlikwidują państwo polskie. I to wszystko, co mam do powiedzenia.

Tematy: odwracanie znaczeń słów, opozycja demokratyczna, likwidacja państwa

Dokument:
- Jeśli pan dobrze liczy, panie pośle Śmiszek… Ale pan dobrze nie liczy. To jest prawie 6 mln wyborców więcej. 6 mln wyborców więcej oddało głos na listy wyborcze, z których startował pan minister Ziobro, aniżeli na Lewicę. I pan z tej mównicy wyrzuca ministra Ziobrę z polityki? Pan z tego państwa przed momentem wyrzucił ponad 6 mln ludzi, więcej, 7660 tys. ludzi.

Tematy: minister Ziobro, wyrzucenie z polityki

Dokument:
- [DOCUMENT]

Tematy:"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPEN_AI_API_KEY'))
        self.llm = OpenAI(self.client, prompt=self.OPENAI_PROMPT, model=self.CHAT_MODEL_TO_USE, chat=True)
        self.kw_model = KeyLLM(self.llm)
        self.cache = Cache(directory=os.path.join(AIPOLIT_CACHE_DIR, self.MY_CACHE_DIR))
        logging.info("Loaded %i records from cache for KeyBertLLMCached", len(self.cache))

    def extract_keywords(self, documents):
        index_to_result = dict()

        to_retrieve = dict()
        for i, doc in enumerate(documents):
            doc_hash = self._get_persistent_hash(doc)
            if doc_hash in self.cache:
                index_to_result[i] = self.cache[doc_hash]
            else:
                to_retrieve[i] = doc

        self._retrieve_keywords(to_retrieve, index_to_result)

        result = []
        for _, val in sorted(index_to_result.items(), key=lambda k_v: k_v[0]):
            result.append(val)
        return result

    def clear_cache(self):
        self.cache.clear()

    def close(self):
        self.cache.close()

    def _retrieve_keywords(self, to_retrieve, index_to_result):
        if len(to_retrieve) <= 0:
            return

        logging.info(f"WARNING: Will retrieve {len(to_retrieve)} from ChatGPT. This will cause real $$$ cost!")
        docs_to_send = []
        docs_indices = []

        for i, doc in to_retrieve.items():
            docs_to_send.append(doc)
            docs_indices.append(i)

        keywords = self.kw_model.extract_keywords(docs_to_send)

        for i, doc, keys_for_doc in zip(docs_indices, docs_to_send, keywords):
            doc_hash = self._get_persistent_hash(doc)
            index_to_result[i] = keys_for_doc
            self.cache[doc_hash] = keys_for_doc
        self.cache.close()

    def _get_persistent_hash(self, doc):
        return hashlib.md5(doc.encode('utf-8')).hexdigest()
