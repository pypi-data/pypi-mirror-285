from typing import List, Literal, Union, Any, Tuple,Dict
import inspect

def swap_key_value(dictt:Dict[Any,Any]):
    # to import
    out_dict = dict()
    for key, value in dictt.items():
        out_dict[value] = key
    return out_dict

def filter_dict(myDict:Dict,select_key):
    # should be in my lib
    ans = {key: value for key, value in myDict.items() if key in select_key}
    return ans

def filter_dict(myDict,select_key):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 02_Conjugation\Conju_PT.py"
    # should be in my lib
    ans = {key: value for key, value in myDict.items() if key in select_key}
    return ans


def reorder_dict(input_dict, new_order):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 02_Conjugation\Conju_PT.py"
    from collections import OrderedDict
    return OrderedDict((key, input_dict[key]) for key in new_order)


def combine_2dicts(dict1: dict, dict2: dict):
    """
    Combines two dictionaries into a new dictionary.
    If keys are the same, the value from dict2 will overwrite the value from dict1.
    """
    out_dict = dict1.copy()
    out_dict.update(dict2)
    return out_dict

def combine_dicts(*dict_list: list[dict]):
    """
    Combines two dictionaries into a new dictionary.
    If keys are the same, the value from dict2 will overwrite the value from dict1.
    """
    out_dict = dict_list[0].copy()
    for i, curr_dict in enumerate(dict_list):
        if i > 0:
            out_dict.update(curr_dict)
        
    return out_dict

__all__ = [name for name, obj in globals().items() 
           if inspect.isfunction(obj) and not name.startswith('_')]