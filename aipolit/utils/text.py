import re
import csv
from collections import OrderedDict
import random
import emoji


NONE_STRING = 'N/A'
TRUE_STRING = "T"
FALSE_STRING = "F"


def none_to_string(value):
    if value is None:
        return NONE_STRING
    else:
        return value


def string_to_none(value):
    if value == NONE_STRING:
        return None
    else:
        return value


def bool_to_string(value):
    if value is None:
        return NONE_STRING
    elif value == True:
        return TRUE_STRING
    else:
        return FALSE_STRING


def string_to_bool(value):
    if value == NONE_STRING:
        return None
    elif value == TRUE_STRING:
        return True
    elif value == FALSE_STRING:
        return False
    else:
        return None


def save_list_as_tsv(fp, data_list, header):
    """
    Saves given data_list as TSV file.
    Assumes that data_list is list of list (each row is equal length as header)
    """
    with open(fp, "w") as f:
        f.write("\t".join(header))
        f.write("\n")
        for entry in data_list:
            assert len(entry) == len(header)
            entry_str = [str(x) for x in entry]
            f.write("\t".join(entry_str))
            f.write("\n")


def save_dict_as_tsv(fp, data_dict):
    """
    Saves given data_dict as TSV headerless file.
    """
    with open(fp, "w") as f:
        for key, value in data_dict.items():
            if value is None:
                value = ''
            f.write(f"{key}\t{value}\n")


def load_dict_from_tsv(fp):
    """
    Loads data_dict from TSV headerless file.
    Assumes this is two column TSV: key<tab>value
    Returns: OrderedDict
    """
    result = OrderedDict()

    with open(fp, "r") as f:
        for line in f:
            line = line.rstrip()
            tokens = line.split('\t')
            key = tokens[0]
            if len(tokens) >= 2:
                value = tokens[1]
            else:
                value = ''
            result[key] = value
    return result


def read_tsv(fp, header=None):
    result = []
    with open(fp, "r") as f:
        for line in f:
            line = line.rstrip()
            tokens = line.split("\t")
            if not header:
                header = tokens
            else:
                entry = OrderedDict()
                for i, key in enumerate(header):
                    value = ""
                    if i < len(tokens):
                        value = tokens[i]
                    if value == NONE_STRING:
                        value = None
                    entry[key] = value
                result.append(entry)
    return result

def save_tsv(fp, data, header):
    """
    Saves data to TSV file assuming that 'data' is list of dicts with keys from 'header'
    """
    with open(fp, "w") as f:
        f.write("\t".join(header))
        f.write("\n")

        for e in data:
            row = []
            for key in header:
                val = e.get(key, '')
                val = str(val)
                row.append(val)
            f.write("\t".join(row))
            f.write("\n")


def save_txt_list(fp, data):
    with open(fp, "w") as f:
        for line in data:
            f.write(line)
            f.write("\n")


def read_txt_list(fp):
    result = []
    result_set = set()
    with open(fp, "r") as f:
        for line in f:
            line = line.rstrip()
            line = re.sub(r"\s+", " ", line)
            line = re.sub(r"^\s+", " ", line)
            line = re.sub(r"\s+$", " ", line)
            if re.match(r"^\s*#.*$", line):
                continue
            if re.match(r"^\s*$", line):
                continue
            if line not in result_set:
                result_set.add(line)
                result.append(line)
    return result


def emojize_case_insensitive(text, language='alias'):
    """
    Tries to emojize text trying also case insensitve forms.
    """

    tokens = re.split(r"(:[a-zA-Z0-9_-]+:)", text)
    result = []
    for token in tokens:
        if len(token) <= 0:
            continue
        if token[0] == ":":
            if re.match(r"^:[a-zA-Z0-9_-]+:$", token):
                emojized = emoji.emojize(token, language=language)
                if emojized != token:
                    result.append(emojized)
                    continue
                else:
                    new_token = ":" + token[1].upper() + token[2:]
                    emojized = emoji.emojize(new_token, language=language)
                    if emojized != new_token:
                        result.append(emojized)
                        continue
                    else:
                        new_token = ":" + token[1:].upper()
                        emojized = emoji.emojize(new_token, language=language)
                        if emojized != new_token:
                            result.append(emojized)
                            continue

        # could not emojize, probably not emoji
        result.append(token)

    return "".join(result)


def read_csv(fp, delimiter=';', quotechar='"'):
    """
    Returns list of rows.
    Each row is Ordered dict: key -> value
    Assumes that first row is a header.
    """
    data = []
    with open(fp, "r") as f:
        reader = csv.reader(f, delimiter=';', quotechar='"')
        firstrow = None
        for row in reader:
            if not firstrow:
                firstrow = row
            else:
                entry = OrderedDict()
                for i, key in enumerate(firstrow):
                    val = None
                    if i < len(row):
                        val = row[i]
                    entry[key] = val
                data.append(entry)
    return data
