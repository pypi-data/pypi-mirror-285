from typing import List, Literal, Union, Any, Tuple,Dict

def filter_dict(myDict:Dict,select_key):
    # should be in my lib
    ans = {key: value for key, value in myDict.items() if key in select_key}
    return ans

def reorder_dict(input_dict, new_order):
    from collections import OrderedDict
    return OrderedDict((key, input_dict[key]) for key in new_order)


def filter_dict(myDict,select_key):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 02_Conjugation\Conju_PT.py"
    # should be in my lib
    ans = {key: value for key, value in myDict.items() if key in select_key}
    return ans


def reorder_dict(input_dict, new_order):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 02_Conjugation\Conju_PT.py"
    from collections import OrderedDict
    return OrderedDict((key, input_dict[key]) for key in new_order)