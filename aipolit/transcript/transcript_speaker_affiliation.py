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
        self.all_names_regex = self._create_all_names_regex()

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
        match = self.all_names_regex.search(speaker_name)
        if not match:
            return None

        matched_name = match.group(1)

        # 2. get club during 'when' for person matched
        person = self.person_affiliation.get_person_by_name(matched_name)
        if person is None:
            return None

        if when is not None:
            when_txt = date_to_text(when)

        return person.get_club(when_txt)

    def _create_all_names_regex(self):
        regex_chunks = []

        for name in sorted(self.person_affiliation.name_to_entry.keys(), key=lambda n: -len(n)):
            regex_chunks.append(name)

        regex = re.compile(r"\b(" + "|".join(regex_chunks) + ")$", re.IGNORECASE)
        return regex
