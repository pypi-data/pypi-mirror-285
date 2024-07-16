import os


def find_files(
    filename: str,
    base_dir: str = "./",
    case_sensitive: bool = False,
    find_all: bool = True,
    skip_text: str = None,
):
    """find all files that match file name
    Args:
        skip_text (str, optional): if have this string in file_path name or folder, it will skip that file. Defaults to None.
    """
    filename_lower = filename.lower() if not case_sensitive else None
    skip_text_lower = (
        skip_text.lower() if skip_text and not case_sensitive else skip_text
    )

    for root, _, files in os.walk(base_dir):
        root_to_check = root if case_sensitive else root.lower()
        if skip_text and (
            (case_sensitive and skip_text in root)
            or (not case_sensitive and skip_text_lower in root_to_check)
        ):
            continue

        for file in files:
            file_to_check = file if case_sensitive else file.lower()
            if (case_sensitive and file == filename) or (
                not case_sensitive and file_to_check == filename_lower
            ):
                if skip_text and (
                    (case_sensitive and skip_text in file)
                    or (not case_sensitive and skip_text_lower in file_to_check)
                ):
                    continue
                full_path = os.path.join(root, file)
                yield full_path
                if not find_all:
                    return


def count_files(
    filename: str,
    base_dir: str = "./",
    case_sensitive: bool = True,
    skip_text: str = None,
) -> int:

    count = 0

    filename_lower = filename.lower() if not case_sensitive else None
    skip_text_lower = (
        skip_text.lower() if skip_text and not case_sensitive else skip_text
    )

    for root, _, files in os.walk(base_dir):
        root_to_check = root if case_sensitive else root.lower()
        if skip_text and (
            (case_sensitive and skip_text in root)
            or (not case_sensitive and skip_text_lower in root_to_check)
        ):
            continue

        for file in files:
            file_to_check = file if case_sensitive else file.lower()
            if (case_sensitive and file == filename) or (
                not case_sensitive and file_to_check == filename_lower
            ):
                if skip_text and (
                    (case_sensitive and skip_text in file)
                    or (not case_sensitive and skip_text_lower in file_to_check)
                ):
                    continue
                count += 1

    return count


def find_first_file(filename, base_dir="./", case_sensitive=False):
    filename_lower = filename.lower() if not case_sensitive else None
    for root, _, files in os.walk(base_dir):
        for file in files:
            if (case_sensitive and file == filename) or (
                not case_sensitive and file.lower() == filename_lower
            ):
                full_path = os.path.join(root, file)
                return full_path
    return None


def find_first_file_contain_id(
    filename: str, folder_id: str, case_sensitive: bool = False
) -> str:
    file_list = find_files(filename)
    if not case_sensitive:
        folder_id = folder_id.lower()
    for file in file_list:
        if not case_sensitive:
            file_lower = file.lower()
            if folder_id in file_lower:
                return file
        else:
            if folder_id in file:
                return file
    return None


def main():
    for file in find_files("test_class.py"):
        print(file)

    print(find_first_file_contain_id("test_class.py", "py_output_compare"))
    print(find_first_file("test_class.py"))


if __name__ == "__main__":
    main()
