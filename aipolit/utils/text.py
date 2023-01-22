import re
from collections import OrderedDict
import random


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