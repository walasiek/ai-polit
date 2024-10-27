import logging
from collections import OrderedDict
from aipolit.utils.text import read_csv
from aipolit.utils.globals import \
     AIPOLIT_SEJM2023_ELECTION_RAW_DATA_GENERAL_RESULTS_FP
from aipolit.sejmvote.voting_factory_place_data import create_voting_place_data


class VotingSejm2023GeneralResults:
    """
    Stores general results (na listy) from the Sejm 2023 Elections.
    """

    INTEGER_COLUMNS = {
        'total_possible_voters',
        'total_valid_votes',
        'total_votes_lista_ko',
        'total_votes_lista_pis',
        'total_votes_lista_3d',
        'total_votes_lista_sld',
        'total_votes_lista_konfederacja',
    }

    TRANSLATE_RAW_COLUMNS = {
        'Symbol kontrolny': None,
        'TERYT Gminy': 'teryt_gminy',
        'Nr okręgu': 'sejm_okreg_number',
        'Nr komisji': 'obwod_number',
        'Liczba komisji': 'same_obwod_count',
        'Liczba uwzględnionych komisji': '',
        'Typ obszaru': 'location_type',
        'Typ obwodu': 'obwod_type',
        'Siedziba': 'location_fullname',
        'Gmina': 'gmina_name',
        'Powiat': 'powiat_name',
        'Województwo': 'region_name',
        'Komisja otrzymała kart do głosowania': None,
        'Liczba wyborców uprawnionych do głosowania': 'total_possible_voters',
        'Nie wykorzystano kart do głosowania': None,
        'Liczba wyborców, którym wydano karty do głosowania': None,
        'Liczba wyborców głosujących przez pełnomocnika': None,
        'Liczba wyborców głosujących na podstawie zaświadczenia o prawie do głosowania': None,
        'Liczba wyborców, którym wysłano pakiety wyborcze': None,
        'Liczba otrzymanych kopert zwrotnych': None,
        'Liczba kopert zwrotnych, w których nie było oświadczenia o osobistym i tajnym oddaniu głosu': None,
        'Liczba kopert zwrotnych, w których oświadczenie nie było podpisane': None,
        'Liczba kopert zwrotnych, w których nie było koperty na kartę do głosowania': None,
        'Liczba kopert zwrotnych, w których znajdowała się niezaklejona koperta na kartę do głosowania': None,
        'Liczba kopert na kartę do głosowania wrzuconych do urny': None,
        'Liczba kart wyjętych z urny': None,
        'W tym liczba kart wyjętych z kopert na kartę do głosowania': None,
        'Liczba kart nieważnych': None,
        'Liczba kart ważnych': None,
        'Liczba głosów nieważnych': None,
        'W tym z powodu postawienia znaku „X” obok nazwiska dwóch lub większej liczby kandydatów z różnych list': None,
        'W tym z powodu niepostawienia znaku „X” obok nazwiska żadnego kandydata': None,
        'W tym z powodu postawienia znaku „X” wyłącznie obok nazwiska kandydata na liście, której rejestracja została unieważniona': None,
        'Liczba głosów ważnych oddanych łącznie na wszystkie listy kandydatów': 'total_valid_votes',
        'Liczba wyborców, którym wydano karty do głosowania w lokalu wyborczym oraz w głosowaniu korespondencyjnym (łącznie)': '',
        'KOMITET WYBORCZY BEZPARTYJNI SAMORZĄDOWCY': '',
        'KOALICYJNY KOMITET WYBORCZY TRZECIA DROGA POLSKA 2050 SZYMONA HOŁOWNI - POLSKIE STRONNICTWO LUDOWE': 'total_votes_lista_3d',
        'KOMITET WYBORCZY NOWA LEWICA': 'total_votes_lista_sld',
        'KOMITET WYBORCZY PRAWO I SPRAWIEDLIWOŚĆ': 'total_votes_lista_pis',
        'KOMITET WYBORCZY KONFEDERACJA WOLNOŚĆ I NIEPODLEGŁOŚĆ': 'total_votes_lista_konfederacja',
        'KOALICYJNY KOMITET WYBORCZY KOALICJA OBYWATELSKA PO .N IPL ZIELONI': 'total_votes_lista_ko',
        'KOMITET WYBORCZY POLSKA JEST JEDNA': '',
        'KOMITET WYBORCZY WYBORCÓW RUCHU DOBROBYTU I POKOJU': '',
        'KOMITET WYBORCZY NORMALNY KRAJ': '',
        'KOMITET WYBORCZY ANTYPARTIA': '',
        'KOMITET WYBORCZY RUCH NAPRAWY POLSKI': '',
        'KOMITET WYBORCZY WYBORCÓW MNIEJSZOŚĆ NIEMIECKA': '',

    }
    def __init__(self):
        self.voting_place_data = create_voting_place_data('sejm2023')
        self.results_data = []
        self.obwod_id_to_index = dict()
        self._load_from_raw()

    def get_results_entry_by_obwod_id(self, obwod_id):
        if obwod_id in self.obwod_id_to_index:
            i = self.obwod_id_to_index[obwod_id]
            return self.results_data[i]
        return None

    def _load_from_raw(self):
        fp = AIPOLIT_SEJM2023_ELECTION_RAW_DATA_GENERAL_RESULTS_FP
        logging.info("Load raw data from the file: %s", fp)
        raw_data = read_csv(fp, delimiter=';', quotechar='"', fix_utf=True)

        first_entry = raw_data[0]

        for entry in raw_data:
            parsed_entry = self._parse_entry_keys(entry)
            if not parsed_entry:
                continue

            obwod_id = self.voting_place_data.create_id_from_entry(parsed_entry)
            parsed_entry['obwod_id'] = obwod_id
            # add frekwencja
            total = parsed_entry['total_valid_votes']
            total_possible_voters = parsed_entry['total_possible_voters']
            freq_vote = int(10000 * total / total_possible_voters) / 100

            parsed_entry['frekwencja'] = freq_vote

            self.obwod_id_to_index[obwod_id] = len(self.results_data)
            self.results_data.append(parsed_entry)
        logging.info("Loaded %i voting results from raw data file", len(self.results_data))

    def _parse_entry_keys(self, entry):
        parsed_entry = OrderedDict()
        not_parsed = []
        for k, v in entry.items():
            if k not in self.TRANSLATE_RAW_COLUMNS:
                not_parsed.append(k)
                continue

            parsed_key = self.TRANSLATE_RAW_COLUMNS.get(k, None)
            if parsed_key is None:
                continue
            if parsed_key == '':
                continue
            if parsed_key in self.INTEGER_COLUMNS:
                if v == '-':
                    return None
                try:
                    v = int(v)
                except Exception as e:
                    logging.info("(can be IGNORED if 'powiat' -> 'zagranica') => Exception parsing int key [%s / %s] in entry: %s", k, parsed_key, entry)
                    # parsing failed
                    return None

            parsed_entry[parsed_key] = v

        if len(not_parsed) > 0:
            for k in not_parsed:
                print(f"'{k}': '',")
            raise Exception(f"Unknown column names found in file {fp} columns: {', '.join(not_parsed)}")
        return parsed_entry
