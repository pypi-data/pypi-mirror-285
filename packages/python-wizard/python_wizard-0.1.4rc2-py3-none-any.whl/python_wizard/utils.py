# v02 => import print_time

def is_convertible_to_num(s):
    if isinstance(s,(int,float)):
        return True
    try:
        int(s)
        return True
    except ValueError:
        try:
            float(s)
            return True
        except ValueError:
            return False


def print_time(duration):
    # tested
    hours = duration // 3600
    minutes = (duration % 3600) / 60
    minutes_str = "{:.2f}".format(minutes)
    seconds = duration % 60
    seconds_str = "{:.2f}".format(seconds)
    if hours < 1:
        if minutes > 1:
            # only minutes
            print(f"{minutes_str} minutes", end="\n")
        else:
            # only seconds
            print(f"{seconds_str} seconds", end="\n")
    else:
        # hours with minutes
        print(f"{hours} hour", end=" ")
        print(f"{minutes_str} minutes", end="\n")

def package_version(package_name):
    # medium tested
    """
    
    Return the version of a Python package as a tuple of integers.
    
    Parameters
    ----------
    package_name : str
        The name of the Python package for which you want to retrieve the version.
    
    Returns
    -------
    package_version_tuple : tuple of ints
        The version of the package as a tuple of integers. If the package is not found,
        the tuple will be (0, 0, 0).
    
    Notes
    -----
    The function uses the `importlib_metadata` module to retrieve the package version
    from the package metadata. If the package is not found, it returns a tuple of (0, 0, 0).
    
    Examples
    --------
    >>> package_version('pandas')
    (1, 4, 3)
    
    >>> package_version('non_existent_package')
    (0, 0, 0)
    """
    import importlib_metadata
    try:
        package_version = importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        # Handle the case where the package is not found
        package_version = "package is not found"
        return "package is not found"
    
    package_version_tuple = tuple(map(int, package_version.split('.')))
    return package_version_tuple

def flatten(list_of_lists):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 08_VocabList\VocatList_func01.py"
    """Flatten a 2D list to 1D"""
    return [item for sublist in list_of_lists for item in sublist]


def filter_dict(myDict,select_key):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 02_Conjugation\Conju_PT.py"
    # should be in my lib
    ans = {key: value for key, value in myDict.items() if key in select_key}
    return ans


def reorder_dict(input_dict, new_order):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 02_Conjugation\Conju_PT.py"
    from collections import OrderedDict
    return OrderedDict((key, input_dict[key]) for key in new_order)