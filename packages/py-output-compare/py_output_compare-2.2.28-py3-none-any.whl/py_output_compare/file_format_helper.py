import re
from pathlib import Path


def remove_prefix_from_test(filename):
    """my test lab in formate of 1_1_lab_name
    Returns:
        _type_: file name with no 1_1_ like only lab_name
    """
    return re.sub(r"^\d+_\d+_", "", filename)


def get_problem_name_from_test_name(file_path_by_name):
    """Extract the lab name from the file name and include the file extension.
    Args:
        file_path_by_name (str): File path or filename to process.
    Returns:
        str: Lab name extracted from the filename with the file extension.
    """
    full_test_name = Path(file_path_by_name).resolve().stem  # _1_1_adder.py
    final_name = remove_prefix_from_test(full_test_name)
    file_extension = Path(file_path_by_name).suffix  # .py
    return f"{final_name}{file_extension}"
