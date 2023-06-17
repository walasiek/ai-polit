import logging
from collections import OrderedDict
from aipolit.utils.text import read_csv
from aipolit.utils.globals import \
     AIPOLIT_SEJM_ELECTION_RAW_DATA_GENERAL_RESULTS_FP
from aipolit.sejmvote.voting_factory import create_voting_place_data


class VotingSejmGeneralResults:
    """
    Stores general results (na listy) from the Sejm Elections.
    """

    INTEGER_COLUMNS = {
        'total_possible_voters',
        'total_valid_votes',
        'total_votes_lista_ko',
        'total_votes_lista_pis',
        'total_votes_lista_psl',
        'total_votes_lista_sld',
        'total_votes_lista_konfederacja',
    }

    TRANSLATE_RAW_COLUMNS = {
        'Symbol kontrolny': None,
        'Kod TERYT': 'teryt_gminy',
        'Okręg': 'sejm_okreg_number',
        'Numer': 'obwod_number',
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
        'KOALICYJNY KOMITET WYBORCZY KOALICJA OBYWATELSKA PO .N IPL ZIELONI - ZPOW-601-6/19': 'total_votes_lista_ko',
        'KOMITET WYBORCZY AKCJA ZAWIEDZIONYCH EMERYTÓW RENCISTÓW - ZPOW-601-21/19': None,
        'KOMITET WYBORCZY KONFEDERACJA WOLNOŚĆ I NIEPODLEGŁOŚĆ - ZPOW-601-5/19': 'total_votes_lista_konfederacja',
        'KOMITET WYBORCZY POLSKIE STRONNICTWO LUDOWE - ZPOW-601-19/19': 'total_votes_lista_psl',
        'KOMITET WYBORCZY PRAWICA - ZPOW-601-20/19': None,
        'KOMITET WYBORCZY PRAWO I SPRAWIEDLIWOŚĆ - ZPOW-601-9/19': 'total_votes_lista_pis',
        'KOMITET WYBORCZY SKUTECZNI PIOTRA LIROYA-MARCA - ZPOW-601-17/19': None,
        'KOMITET WYBORCZY SOJUSZ LEWICY DEMOKRATYCZNEJ - ZPOW-601-1/19': 'total_votes_lista_sld',
        'KOMITET WYBORCZY WYBORCÓW KOALICJA BEZPARTYJNI I SAMORZĄDOWCY - ZPOW-601-10/19': None,
        'KOMITET WYBORCZY WYBORCÓW MNIEJSZOŚĆ NIEMIECKA - ZPOW-601-15/19': None,
    }
    def __init__(self):
        self.voting_place_data = create_voting_place_data('sejm2019')
        self.results_data = []
        self.obwod_id_to_index = dict()
        self._load_from_raw()

    def get_results_entry_by_obwod_id(self, obwod_id):
        if obwod_id in self.obwod_id_to_index:
            i = self.obwod_id_to_index[obwod_id]
            return self.results_data[i]
        return None

    def _load_from_raw(self):
        fp = AIPOLIT_SEJM_ELECTION_RAW_DATA_GENERAL_RESULTS_FP
        logging.info("Load raw data from the file: %s", fp)
        raw_data = read_csv(fp, delimiter=';', quotechar='"')

        first_entry = raw_data[0]

        for entry in raw_data:
            parsed_entry = OrderedDict()
            for k, v in entry.items():
                if k not in self.TRANSLATE_RAW_COLUMNS:
                    raise Exception(f"Unknown column name found in file {fp} column {k}")

                parsed_key = self.TRANSLATE_RAW_COLUMNS.get(k, None)
                if parsed_key is None:
                    continue
                if parsed_key == '':
                    continue
                if parsed_key in self.INTEGER_COLUMNS:
                    if v == '-':
                        return None
                    v = int(v)
                parsed_entry[parsed_key] = v

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
