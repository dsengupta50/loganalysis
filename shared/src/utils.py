import json
import os

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

def save_json(filename, dict):
    st = json.dumps(dict)
    tfile = open(filename)
    tfile.writelines(st)
    tfile.close()