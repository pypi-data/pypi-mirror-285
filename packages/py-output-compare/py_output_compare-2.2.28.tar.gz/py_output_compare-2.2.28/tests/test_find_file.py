import os
from py_output_compare import find_files, find_first_file, find_first_file_contain_id


def print_path():
    print(find_first_file_contain_id("find_test.txt", "test"))


def test_find_files_all_files():
    filename = "find_test.txt"
    base_dir = r"tests\test_lab_script"
    case_sensitive = True
    find_all = True
    expected_files = [
        os.path.join(base_dir, filename),
    ]

    assert (
        list(find_files(filename, base_dir, case_sensitive, find_all)) == expected_files
    )


def test_find_files_single_file():
    filename = "find_test.txt"
    base_dir = r"tests\test_lab_script"
    case_sensitive = True
    find_all = False
    expected_file = os.path.join(base_dir, filename)
    assert (
        next(find_files(filename, base_dir, case_sensitive, find_all)) == expected_file
    )


def test_find_first_file():
    filename = "find_test.txt"
    base_dir = r"tests\test_lab_script"
    case_sensitive = True
    expected_file = os.path.join(base_dir, filename)
    assert find_first_file(filename, base_dir, case_sensitive) == expected_file


def test_find_first_file_not_found():
    filename = "not_found.txt"
    base_dir = "./"
    case_sensitive = True
    assert find_first_file(filename, base_dir, case_sensitive) is None


def test_find_first_file_contain_id():
    filename = "find_test.txt"
    folder_id = "tests"
    expected_file = os.path.join("./", r"tests\test_lab_script", filename)
    assert find_first_file_contain_id(filename, folder_id) == expected_file


def test_find_first_file_contain_id_not_found():
    filename = "find_test.txt"
    folder_id = "not_found"
    assert find_first_file_contain_id(filename, folder_id) is None
