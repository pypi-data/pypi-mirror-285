# from typing import List, Literal, Union, Any, Tuple
from typing import *
import inspect
# from inspect_py import Scalar_BuiltIn

Scalar_BuiltIn = Union[int, float, str, bool, complex]
def swap_item(input_list: List[Scalar_BuiltIn], 
              item1: Scalar_BuiltIn, 
              item2: Scalar_BuiltIn, 
              inplace: bool = False) -> Union[List[Scalar_BuiltIn], None]:
    """
    Swap the positions of two items in a list.

    Args:
    input_list (List[Scalar_BuiltIn]): The input list.
    item1 (Scalar_BuiltIn): First item to swap.
    item2 (Scalar_BuiltIn): Second item to swap.
    inplace (bool): If True, modify the list in-place. If False, return a new list.

    Returns:
    Union[List[Scalar_BuiltIn], None]: Modified list if inplace is False, None otherwise.

    Raises:
    ValueError: If either item1 or item2 is not in the list.
    """
    if not inplace:
        input_list = input_list.copy()

    try:
        index1 = input_list.index(item1)
        index2 = input_list.index(item2)
    except ValueError as e:
        raise ValueError(f"One or both items not found in the list: {e}")

    input_list[index1], input_list[index2] = input_list[index2], input_list[index1]

    if not inplace:
        return input_list
        
def to_back_of(input_list: List[Scalar_BuiltIn], 
               item_ref: Scalar_BuiltIn, 
               items_to_move: Union[Scalar_BuiltIn, List[Scalar_BuiltIn]], 
               inplace: bool = False) -> Union[List[Scalar_BuiltIn], None]:
    # High tested

    if not inplace:
        input_list = input_list.copy()
    
    # Find the index of the reference item
    try:
        ref_index = input_list.index(item_ref)
    except ValueError:
        raise ValueError(f"Reference item '{item_ref}' not found in the list")
    
    if not is_unique(input_list):
        dup_items = get_duplicates(input_list)
        raise Exception(f"List is not unique, {dup_items} are duplicated")

    # Ensure items_to_move is a list
    if not isinstance(items_to_move, list):
        items_to_move = [items_to_move]

    # Collect items to move and their indices
    to_move = []
    has_error = False
    for item in items_to_move:
        try:
            index = input_list.index(item)
            if index <= ref_index:
                ref_index -= 1
            to_move.append(input_list.pop(index))
        except ValueError:
            print(f"Warning: Item '{item}' not found in the list")
            has_error = True

    if has_error:
        raise ValueError(f"Some elements in items_to_move aren't in the input_list")
    
    # Insert collected items after the reference index
    # Fixed by Claude 3.5
    for i, item in enumerate(to_move):
        input_list.insert(ref_index + 1 + i, item)
    
    if not inplace:
        return input_list


def to_front_of(input_list:List[Scalar_BuiltIn], 
                item_ref: Scalar_BuiltIn, 
                items_to_move:Union[Scalar_BuiltIn,List[Scalar_BuiltIn]], 
                inplace:bool=False) -> Union[List[Any], None]:
    # High tested

    if not inplace:
        input_list = input_list.copy()
    
    # Find the index of the reference item
    try:
        ref_index = input_list.index(item_ref)
    except ValueError:
        raise ValueError(f"Reference item '{item_ref}' not found in the list")
    
    if not is_unique(input_list):
        dup_items = get_duplicates(input_list)
        raise Exception(f"List is not unique, {dup_items} are duplicated")

    # Collect items to move and their indices
    to_move = []
    has_error = False
    for item in items_to_move:
        try:
            index = input_list.index(item)
            if index < ref_index:
                ref_index -= 1
            to_move.append(input_list.pop(index))
        except ValueError:
            print(f"Warning: Item '{item}' not found in the list")
            has_error = True

    if has_error:
        raise ValueError(f"Some elements in items_to_move aren't in the input_list")
    
    # Insert collected items at the reference index
    for item in reversed(to_move):
        input_list.insert(ref_index, item)
    
    if not inplace:
        return input_list

def is_unique(input_list:List[Any]) -> bool:
    """ 
    check if a list is unique(with no duplicates)
    """
    return len(input_list) == len(set(input_list))

def get_duplicates(input_list:List[Any]) -> List[Any] :
    """
    return duplicates items in list
    """
    return [item for item in set(input_list) if input_list.count(item) > 1]

def flatten(list_of_lists:List[List[Any]]):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 08_VocabList\VocatList_func01.py"
    """Flatten a 2D list to 1D"""
    return [item for sublist in list_of_lists for item in sublist]

def filter_text(input_list:List[str],start_with = "",end_with ="", contain = "", case_sensitive:bool=False) -> List[str]:
    """
    filter a list using text string
    currently only support 1 element of start_with, end_with, contain

    """
    # this is from print_col 
    # !!! TODO start_with, end_with, contain is list
    # add 2 logic options

    
    if start_with != "":
        if case_sensitive:
            out_list = [x for x in input_list if x.startswith(start_with) ]
        else:
            out_list = [x for x in input_list if x.lower().startswith(start_with.lower()) ]
        
    
    if end_with != "":
        if case_sensitive:
            out_list = [x for x in input_list if x.endswith(end_with) ]
        else:
            out_list = [x for x in input_list if x.lower().endswith(end_with.lower()) ]
    
    if contain != "":
        if case_sensitive:
            out_list = [x for x in input_list if contain in x]
        else:
            out_list = [x for x in input_list if contain.lower() in x.lower()]
    
    return out_list


def is_list_of_tuple(input: Any) -> bool:
    """
    Check if the input is a list of tuples.

    Parameters
    ----------
    input : Any
        The object to be checked.

    Returns
    -------
    bool
        True if the input is a non-empty list where all elements are tuples,
        False otherwise.

    Examples
    --------
    >>> is_list_of_tuple([(1, 2), (3, 4)])
    True
    >>> is_list_of_tuple([1, 2, 3])
    False
    >>> is_list_of_tuple("not a list")
    False
    >>> is_list_of_tuple([])
    False
    """
    if not isinstance(input, list) or not input:
        return False
    return all(isinstance(item, tuple) for item in input)

def contain_all_items(my_list:List[Any], items_to_check:List[Any]) -> bool:
    # TOADD_01 when items_to_check is single str
    """
    Check if a list contains all items from another list.

    Args:
        my_list (list): The list to check.
        items_to_check (list): The list of items to check for.

    Returns:
        bool: True if my_list contains all items from items_to_check, False otherwise.
    """
    return all(item in my_list for item in items_to_check)

def contain_any_items(my_list, items_to_check) -> bool:
    """
    Check if a list contains all items from another list.

    Args:
        my_list (list): The list to check.
        items_to_check (list): The list of items to check for.

    Returns:
        bool: True if my_list contains all items from items_to_check, False otherwise.
    """
    return any(item in my_list for item in items_to_check)

__all__ = [name for name, obj in globals().items() 
           if inspect.isfunction(obj) and not name.startswith('_')]