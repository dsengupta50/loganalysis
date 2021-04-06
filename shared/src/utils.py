import json
import os
import re

# these will get turned into <*> during preprocessing phase
star_able_regex      = [
    r'[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12}', # UUIDs
    r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)', # IP
    r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$' # Numbers
]

def std_starrify_message(message):
    return starrify_message(message, star_able_regex)

def starrify_message(message, star_regex):
    msg = message
    for regex in star_regex:
        msg = re.sub(regex, '*', msg)

    return msg


def merge_dicts_with_arrays(dict1, dict2):
    merged = {}
    keys = dict1.keys() | dict2.keys()
    for key in keys:
        val = []
        if key in dict1:
          val = val + dict1[key]
        if key in dict2:
            val = val + dict2[key]
        merged[key] = val
    
    return merged

def save_json(filename, d):
    tfile = open(filename, 'w')
    st = json.dumps(d)
    tfile.writelines(st)
    tfile.close()