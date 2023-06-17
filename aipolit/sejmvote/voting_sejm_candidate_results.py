import logging
import os
import re
from collections import OrderedDict
from aipolit.utils.text import read_csv
from aipolit.utils.globals import \
     AIPOLIT_SEJM_ELECTION_RAW_DATA_DIR
from aipolit.sejmvote.voting_place_data import VotingPlaceData


class VotingSejmCandidateResults:
    INSTANCE = dict()

    LISTA_RAW_NAME_TO_LISTA_ID = {
        'KOALICJA OBYWATELSKA PO .N IPL ZIELONI': 'ko',
        'KONFEDERACJA WOLNOŚĆ I NIEPODLEGŁOŚĆ': 'konfederacja',
        'POLSKIE STRONNICTWO LUDOWE': 'psl',
        'PRAWO I SPRAWIEDLIWOŚĆ': 'pis',
        'SOJUSZ LEWICY DEMOKRATYCZNEJ': 'sld',
    }

    TRANSLATE_RAW_COLUMNS = {
        'Kod TERYT': 'teryt_gminy',
        'Okręg': 'sejm_okreg_number',
        'Numer': 'obwod_number',
        'Typ obszaru': 'location_type',
        'Typ obwodu': 'obwod_type',
        'Siedziba': 'location_fullname',
        'Gmina': 'gmina_name',
        'Powiat': 'powiat_name',
        'Województwo': 'region_name',
    }

    def __init__(self, okreg_no):
        self.okreg_no = okreg_no

        self.voting_place_data = VotingPlaceData.get_instance()

        # each results data has keys: total_votes_lista_{party_name}_cand_{cand_no}
        # where cand_no starts from 0!
        self.results_data = []

        # key lista_id (ko, pis, sld, ...) -> value array (names of candidates)
        self.lista_id_to_candidate_names = OrderedDict()
        # translates row header into tuple (lista_id, index of cand in lista_id_to_candidate_names[lista_id])
        self.row_header_to_lista_id_and_cand_id = dict()

        self.obwod_id_to_index = dict()
        self._load_from_raw()

    @classmethod
    def get_instance(cls, okreg_no):
        if cls.INSTANCE.get(okreg_no, None) is None:
            cls.INSTANCE[okreg_no] = VotingSejmCandidateResults(okreg_no)
        return cls.INSTANCE[okreg_no]

    @classmethod
    def create_result_key(cls, lista_id, cand_index):
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
        return f"wyniki_gl_na_kand_po_obwodach_sejm_okr_{self.okreg_no}.csv"

    def _load_from_raw(self):
        fp = os.path.join(AIPOLIT_SEJM_ELECTION_RAW_DATA_DIR, self.get_filename())
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
                    parsed_entry[parsed_key] = value

            obwod_id = self.voting_place_data.create_id_from_entry(parsed_entry)
            parsed_entry['obwod_id'] = obwod_id
            self.obwod_id_to_index[obwod_id] = len(self.results_data)
            self.results_data.append(parsed_entry)

        print(self.results_data[0]['obwod_id'])

    def _parse_raw_header(self, row):
        current_lista_id = None
        current_candidates_raw = []
        for key in row.keys():
            if re.match(r"^Lista nr \d+ - ", key):
                self._add_new_lista_with_candidates(current_lista_id, current_candidates_raw)
                current_candidates_raw = []
                current_lista_id = key
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

        lista_id = None
        for lista_raw_cand in self.LISTA_RAW_NAME_TO_LISTA_ID:
            if lista_raw_cand in lista_id_raw:
                lista_id = self.LISTA_RAW_NAME_TO_LISTA_ID[lista_raw_cand]
                break

        if not lista_id:
            return

        candidate_names = []

        for raw_name in candidate_names_raw:
            match = re.match(r"^(.*) - nr na liście (\d+)", raw_name)
            if not match:
                raise Exception(f"Unexpected header to parse candidate for lista_raw: {lista_id_raw} header: {raw_name}")

            candidate_name = match.group(1)
            candidate_no = int(match.group(2))

            self.row_header_to_lista_id_and_cand_id[raw_name] = (lista_id, len(candidate_names))
            candidate_names.append(candidate_name)
            assert len(candidate_names) == candidate_no

        self.lista_id_to_candidate_names[lista_id] = candidate_names
