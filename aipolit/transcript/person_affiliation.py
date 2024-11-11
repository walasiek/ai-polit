import os
import json
import logging
from typing import Optional
from datetime import date
from aipolit.utils.date import text_to_date, date_to_text
from collections import OrderedDict


def create_name_from_f_s_name(f_name: str, s_name: str) -> str:
    return f"{f_name} {s_name}"


class Person:
    UNK_ENTRY = "TODO"

    def __init__(self, f_name: str, s_name: str, is_active: bool):
        self.f_name = f_name
        self.s_name = s_name
        self.name = create_name_from_f_s_name(f_name, s_name)
        self.is_active = is_active
        self.deactivate_reason = None
        self.active_to = None
        self.all_clubs = []

    def check_is_active(self, when: Optional[str] = None) -> bool:
        if self.is_active:
            return True
        else:
            if when is not None:
                when = text_to_date(when)
            else:
                when = date.today()

            if when < self.active_to:
                return True
            else:
                return False

    def get_club(self, when: Optional[str] = None) -> Optional[str]:
        if not self.check_is_active(when=when):
            return None

        if when is not None:
            when = text_to_date(when)
        else:
            when = date.today()

        for club in self.all_clubs:
            if 'to_date' in club and 'from_date' in club:
                if club['from_date'] <= when < club['to_date']:
                    return club['club_name']
            elif 'to_date' in club:
                if when < club['to_date']:
                    return club['club_name']
            elif 'from_date' in club:
                if when >= club['from_date']:
                    return club['club_name']
            else:
                return club['club_name']

        return None

    def to_dict(self) -> OrderedDict:
        dict_data = OrderedDict()
        dict_data["f_name"] = self.f_name
        dict_data['s_name'] = self.s_name

        clubs = []
        for club in self.all_clubs:
            club_entry = OrderedDict()
            club_entry["club_name"] = club["club_name"]
            if "from_date" in club:
                if club["from_date"] is not None:
                    club_entry['from_date'] = self.date_to_text_with_unk(club["from_date"])
            if "to_date" in club:
                if club["to_date"] is not None:
                    club_entry['to_date'] = self.date_to_text_with_unk(club["to_date"])
            clubs.append(club_entry)

        dict_data['clubs'] = clubs

        dict_data['active'] = self.is_active
        if not self.is_active:
            dict_data['active_to'] = self.date_to_text_with_unk(self.active_to)
            dict_data['deactivate_reason'] = self.deactivate_reason

        return dict_data

    @classmethod
    def date_to_text_with_unk(cls, d) -> Optional[str]:
        if d is None:
            return None
        elif isinstance(d, str) and d.startswith(cls.UNK_ENTRY):
            return d
        else:
            return date_to_text(d)

    def sort_clubs(self):
        """
        Clubs should be sorted in ascending order, last one is current
        """
        if len(self.all_clubs) < 2:
            return

        def get_for_sort_func(e):
            k1 = self.date_to_text_with_unk(e.get('from_date', None))
            k2 = self.date_to_text_with_unk(e.get('to_date', None))

            if k1 is None:
                k1 = '1000-01-01'
            if k2 is None:
                k2 = '3000-01-01'

            return (k1, k2)

        sorted_clubs = [c for c in sorted(self.all_clubs, key=get_for_sort_func)]
        self.all_clubs = sorted_clubs

    @classmethod
    def text_to_date_with_unk(cls, txt: str):
        if txt is None:
            return None
        elif txt.startswith(cls.UNK_ENTRY):
            return txt
        else:
            return text_to_date(txt)

    @classmethod
    def from_json_entry(cls, json_entry):
        new_person = Person(
            f_name=json_entry['f_name'],
            s_name=json_entry['s_name'],
            is_active=json_entry['active'],
        )

        for club in json_entry['clubs']:
            for k in ['from_date', 'to_date']:
                if k in club:
                    club[k] = cls.text_to_date_with_unk(club[k])
            new_person.all_clubs.append(club)

        if not new_person.is_active:
            new_person.deactivate_reason = json_entry['deactivate_reason']
            new_person.active_to = cls.text_to_date_with_unk(json_entry['active_to'])

        new_person.sort_clubs()
        return new_person


class PersonAffiliation:
    """
    This class tries to assign given person to particular politcal party / side.
    It is based on the hardcoded list of names which is stored in resources directory AFFILIATION_DATA_DIR

    Remark: the affiliation uses only first name and second name, so it has its drawbacks like:
    - persons with the same name and surname are not distinguished
    - persons who change their surname (e.g women after marriage) are treated as different individuals (maybe I will fix it in the future :) )
    """

    AFFILIATION_DATA_DIR="political-affiliation"

    def __init__(self, fixed_filepath: Optional[str] = None):
        self.person_data = []
        self.name_to_entry = dict()
        self.input_data_filepath = None
        self._load_data(fixed_filepath)

    def count(self, only_active: Optional[bool] = False) -> int:
        if only_active:
            result = 0
            for e in self.person_data:
                if e.check_is_active():
                    result += 1
            return result
        else:
            return len(self.person_data)

    def get_person_by_name(self, name: str) -> Optional[Person]:
        return self.name_to_entry.get(name, None)

    def get_person_by_f_name_and_s_name(self, f_name: str, s_name: str) -> Optional[Person]:
        name = create_name_from_f_s_name(f_name, s_name)
        return self.name_to_entry.get(name, None)

    def add_person(self, new_person: Person):
        if new_person.name in self.name_to_entry:
            logging.info("DUPLICATE name found in PersonAffiliation datafile: %s (will not be added)", new_person.name)

        self.name_to_entry[new_person.name] = new_person
        self.person_data.append(new_person)

    def dump_to_json_file(self, filepath: str):
        data = []
        for person in sorted(self.person_data, key=lambda p: p.name):
            data.append(person.to_dict())

        with open(filepath, "w", encoding ='utf8') as f:
            json.dump({
                "poslowie": data,
            }, f, indent=4, ensure_ascii = False)

        return

    def _load_data(self, fixed_filepath: Optional[str] = None):
        fp = None
        if fixed_filepath is not None:
            fp = fixed_filepath
        else:
            fp = os.path.join("resources", self.AFFILIATION_DATA_DIR, "sejm.json")

        self.input_data_filepath = os.path.abspath(fp)
        data = None
        with open(fp, "r") as f:
            data = json.load(f)

        for entry in data['poslowie']:
            new_person = Person.from_json_entry(entry)
            self.add_person(new_person)
