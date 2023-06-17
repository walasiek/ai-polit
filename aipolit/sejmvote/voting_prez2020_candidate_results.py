import logging
import os
import re
from collections import OrderedDict
from aipolit.utils.text import read_csv
from aipolit.utils.globals import \
     AIPOLIT_PREZ2020_ELECTION_RAW_DATA_DIR
from aipolit.sejmvote.voting_factory import create_voting_place_data


class VotingPrez2020CandidateResults:
    INSTANCE = dict()

    INTEGER_COLUMNS = {
        'total_possible_voters',
        'total_valid_votes',
        'total_votes_lista_1_tura',
    }

    TRANSLATE_RAW_COLUMNS = {
        "Symbol kontrolny": '',
        "Nr OKW": 'okreg_no',
        "Kod TERYT": 'teryt_gminy',
        "Typ gminy": None,
        "Numer obwodu": 'obwod_number',
        "Typ obszaru": 'location_type',
        "Typ obwodu": 'obwod_type',
        "Siedziba": 'location_fullname',
        "Gmina": 'gmina_name',
        "Powiat": 'powiat_name',
        "Województwo": 'region_name',
        "Komisje obwodowe otrzymały kart do głosowania": None,
        "Liczba wyborców uprawnionych do głosowania": 'total_possible_voters',
        "Nie wykorzystano kart do głosowania": None,
        "Liczba wyborców, którym wydano karty do głosowania": None,
        "Liczba wyborców głosujących przez pełnomocnika": None,
        "Liczba wyborców głosujących na podstawie zaświadczenia o prawie do głosowania": None,
        "Liczba wyborców, którym wysłano pakiety wyborcze": None,
        "Liczba otrzymanych kopert zwrotnych": None,
        "Liczba kopert zwrotnych, w których nie było oświadczenia o osobistym i tajnym oddaniu głosu": None,
        "Liczba kopert zwrotnych, w których oświadczenie nie było podpisane": None,
        "Liczba kopert zwrotnych, w których nie było koperty na kartę do głosowania": None,
        "Liczba kopert zwrotnych, w których znajdowała się niezaklejona koperta na kartę do głosowania": None,
        "Liczba kopert na kartę do głosowania wrzuconych do urny": None,
        "Liczba kart wyjętych z urny": None,
        "W tym liczba kart wyjętych z kopert na kartę do głosowania": None,
        "Liczba kart nieważnych": None,
        "Liczba kart ważnych": None,
        "Liczba głosów nieważnych": None,
        "W tym z powodu postawienia znaku „X” obok nazwiska dwóch lub większej liczby kandydatów": None,
        "W tym z powodu niepostawienia znaku „X” obok nazwiska żadnego kandydata": None,
        "W tym z powodu postawienia znaku „X” wyłącznie obok skreślonego nazwiska kandydata": None,
        "Liczba głosów ważnych oddanych łącznie na wszystkich kandydatów": 'total_valid_votes',
        "Robert BIEDROŃ": "",
        "Krzysztof BOSAK": "",
        "Andrzej Sebastian DUDA": "",
        "Szymon Franciszek HOŁOWNIA": "",
        "Marek JAKUBIAK": "",
        "Władysław Marcin KOSINIAK-KAMYSZ": "",
        "Mirosław Mariusz PIOTROWSKI": "",
        "Paweł Jan TANAJNO": "",
        "Rafał Kazimierz TRZASKOWSKI": "",
        "Waldemar Włodzimierz WITKOWSKI": "",
        "Stanisław Józef ŻÓŁTEK": "",
    }

    def __init__(self, okreg_no):
        self.okreg_no = okreg_no
        self.voting_place_data = create_voting_place_data("prez2020")

        # each results data has keys: total_votes_lista_{party_name}_cand_{cand_no}
        # party_name := 1_tura | 2_tura (not implemented)
        # where cand_no starts from 0!
        self.results_data = []

        # key lista_id (1_tura, 2_tura) -> value array (names of candidates)
        self.lista_id_to_candidate_names = OrderedDict()
        # translates row header into tuple (lista_id, index of cand in lista_id_to_candidate_names[lista_id])
        self.row_header_to_lista_id_and_cand_id = dict()

        self.obwod_id_to_index = dict()
        self._load_from_raw()

    @classmethod
    def get_instance(cls, okreg_no):
        if cls.INSTANCE.get(okreg_no, None) is None:
            cls.INSTANCE[okreg_no] = VotingPrez2020CandidateResults(okreg_no)
        return cls.INSTANCE[okreg_no]

    @classmethod
    def create_result_key(cls, lista_id, cand_index):
        assert lista_id in {"1_tura", "2_tura"}
        return f"total_votes_lista_{lista_id}_cand_{cand_index}"

    def get_results_entry_by_obwod_id(self, obwod_id):
        if obwod_id in self.obwod_id_to_index:
            i = self.obwod_id_to_index[obwod_id]
            return self.results_data[i]
        return None

    def get_candidate_result(self, obwod_id, lista_id, cand_index):
        obwod_results = self.get_results_entry_by_obwod_id(obwod_id)
        return obwod_results[self.create_result_key(lista_id, cand_index)]

    def get_candidate_name(self, lista_id, cand_index):
        return self.lista_id_to_candidate_names[lista_id][cand_index]

    def get_filename(self):
        return f"wyniki_gl_na_kand_po_obwodach_utf8.csv"

    def _load_from_raw(self):
        fp = os.path.join(AIPOLIT_PREZ2020_ELECTION_RAW_DATA_DIR, self.get_filename())
        logging.info("Load raw data from the file: %s", fp)
        raw_data = read_csv(fp, delimiter=';', quotechar='"')

        for row in raw_data:
            parsed_entry = OrderedDict()

            if len(self.results_data) == 0:
                # first row
                self._parse_raw_header(row)

            for key, value in row.items():
                if key in self.row_header_to_lista_id_and_cand_id:
                    lista_id, cand_index = self.row_header_to_lista_id_and_cand_id[key]
                    entry_key = self.create_result_key(lista_id, cand_index)
                    if value == '-':
                        value = 0
                    parsed_entry[entry_key] = int(value)
                elif key in self.TRANSLATE_RAW_COLUMNS:
                    parsed_key = self.TRANSLATE_RAW_COLUMNS[key]
                    if parsed_key in self.INTEGER_COLUMNS:
                        if value == '-':
                            value = 0
                        value = int(value)
                    parsed_entry[parsed_key] = value

            obwod_id = self.voting_place_data.create_id_from_entry(parsed_entry)
            parsed_entry['obwod_id'] = obwod_id

            if self.okreg_no is not None:
                if self.okreg_no != parsed_entry['okreg_no']:
                    continue

            # add frekwencja
            total = parsed_entry['total_valid_votes']
            total_possible_voters = parsed_entry['total_possible_voters']
            freq_vote = 0
            if total_possible_voters > 0:
                freq_vote = int(10000 * total / total_possible_voters) / 100
            parsed_entry['frekwencja'] = freq_vote

            parsed_entry['total_votes_lista_1_tura'] = parsed_entry['total_valid_votes']

            self.obwod_id_to_index[obwod_id] = len(self.results_data)
            self.results_data.append(parsed_entry)

    def _parse_raw_header(self, row):
        current_lista_id = None
        current_candidates_raw = []
        for key in row.keys():
            if re.match(r"^Liczba głosów ważnych oddanych łącznie na wszystkich kandydatów", key):
                self._add_new_lista_with_candidates(current_lista_id, current_candidates_raw)
                current_candidates_raw = []
                current_lista_id = "1_tura"
            else:
                if current_lista_id:
                    current_candidates_raw.append(key)

        if len(current_candidates_raw):
            self._add_new_lista_with_candidates(current_lista_id, current_candidates_raw)

    def _add_new_lista_with_candidates(self, lista_id_raw, candidate_names_raw):
        if not lista_id_raw:
            return
        if not len(candidate_names_raw):
            return

        lista_id = lista_id_raw
        candidate_names = []

        for i, raw_name in enumerate(candidate_names_raw):

            candidate_name = raw_name
            candidate_no = i

            self.row_header_to_lista_id_and_cand_id[raw_name] = (lista_id, len(candidate_names))
            candidate_names.append(candidate_name)
            assert len(candidate_names) == candidate_no + 1

        self.lista_id_to_candidate_names[lista_id] = candidate_names
