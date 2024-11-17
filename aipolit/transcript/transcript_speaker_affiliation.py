import re
from typing import Optional
from datetime import date
from aipolit.transcript.person_affiliation import PersonAffiliation
from aipolit.utils.date import date_to_text


class TranscriptSpeakerAffiliation:
    """
    Assigns party to given transcript speaker.
    """
    def __init__(self, person_affiliation: PersonAffiliation):
        self.person_affiliation = person_affiliation

        self.all_names_regex = None
        self.all_names_with_potential_2nd_name_regex = None
        self.all_names_only_one_f_name_regex = None

        self.name_cut_to_only_f_name_to_original_names = dict()

        self._create_all_names_regex()

    def assign_affiliation(
            self,
            speaker_name: str,
            when: Optional[date] = None,
            when_txt: Optional[str] = None) -> Optional[str]:
        """
        Tries to assign club affiliation from PersonAffiliation
        for given speaker name during defined date.

        Returns None if not possible to assign person to a club (e.g. unknown person)
        """

        assert when is not None or when_txt is not None, "one of when or when_txt should be defined"
        assert not (when is not None and when_txt is not None), "both 'when' and 'when_txt' should not be defined at the same time (impl error)"

        # 1. regex match - last string of the speaker name (case insensitive, regex from right to left matching)
        matched_name = self.normalize_name(speaker_name)
        if matched_name is None:
            return None

        # 2. get club during 'when' for person matched
        person = self.person_affiliation.get_person_by_name(matched_name)
        if person is None:
            return None

        if when is not None:
            when_txt = date_to_text(when)

        return person.get_club(when_txt)

    def normalize_name(self, speaker_name: str) -> Optional[str]:
        """
        Tries to normalize name using database of persons in affilaitions.
        Returns name as it appears in affiliations data (if found)
        or None if cant find such person in our data.
        """
        match = self.all_names_regex.search(speaker_name)
        if not match:
            # 2nd try - maybe transcript omits 2nd name?
            match_without_2nd_name = self.all_names_only_one_f_name_regex.search(speaker_name)
            if match_without_2nd_name:
                matched_name_without_2nd = match_without_2nd_name.group(1)

                original_name = self.name_cut_to_only_f_name_to_original_names.get(matched_name_without_2nd, None)
                return original_name

            # 3rd try - maybe DB which we are using doesn't contain 2nd name?
            match_with_additional_2nd_name = self.all_names_with_potential_2nd_name_regex.search(speaker_name)
            if match_with_additional_2nd_name:
                matched_name = match_with_additional_2nd_name.group(1)
                name_tokens = re.split(r"\s+", matched_name)
                db_name = f"{name_tokens[0]} {name_tokens[-1]}"
                return db_name

            return None

        matched_name = match.group(1)
        return matched_name


    def _create_all_names_regex(self):
        regex_chunks = []
        regex_chunks_only_one_f_name = []
        regex_chunks_with_potential_2nd_name = []

        for name in sorted(self.person_affiliation.name_to_entry.keys(), key=lambda n: -len(n)):
            regex_chunks.append(name)

            name_tokens = re.split(r"\s+", name)
            if len(name_tokens) > 2:
                name_reduced_to_1_name = f"{name_tokens[0]} {name_tokens[-1]}"
                name_reduced_to_1_name_regex = f"{name_tokens[0]} +{name_tokens[-1]}"
                regex_chunks_only_one_f_name.append(name_reduced_to_1_name_regex)
                self.name_cut_to_only_f_name_to_original_names[name_reduced_to_1_name] = name
            elif len(name_tokens) == 2:
                # need to add version where potential 2nd name is added (but it is not present in DB)
                regex_chunks_with_potential_2nd_name.append(f"{name_tokens[0]}\\s+[^ ]+\\s+{name_tokens[-1]}")

        self.all_names_regex = re.compile(r"\b(" + "|".join(regex_chunks) + ")$", re.IGNORECASE)

        self.all_names_with_potential_2nd_name_regex = re.compile(r"\b(" + "|".join(regex_chunks_with_potential_2nd_name) + ")$", re.IGNORECASE)
        self.all_names_only_one_f_name_regex = re.compile(r"\b(" + "|".join(regex_chunks_only_one_f_name) + ")$", re.IGNORECASE)
