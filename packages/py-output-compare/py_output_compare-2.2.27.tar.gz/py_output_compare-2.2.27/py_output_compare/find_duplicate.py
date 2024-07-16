import hashlib
import os
import re
from collections import defaultdict


def normalize_content(content, to_lowercase=False):
    normalized = re.sub(r"\s+", "", content)
    return normalized.lower() if to_lowercase else normalized


def hash_file(filepath, do_normalize=False, to_lowercase=False):
    hasher = hashlib.sha256()
    with open(filepath, "rb") as file:
        content = file.read()
        if do_normalize or to_lowercase:
            content = normalize_content(
                content.decode("utf-8", errors="ignore"), to_lowercase
            ).encode("utf-8")
        hasher.update(content)
    return hasher.hexdigest()


def find_duplicate_files(
    folder_path="./",
    ignore_list=["TestRunner", "nattapong"],
    include_list=[],
    do_normalize=False,
    to_lowercase=False,
):
    file_hashes = defaultdict(list)
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if any(ignore in file_path for ignore in ignore_list):
                    continue
                if include_list and not any(
                    include in file_path for include in include_list
                ):
                    continue
                file_hash = hash_file(file_path, do_normalize, to_lowercase)
                file_hashes[file_hash].append(file_path)
    return {hash: paths for hash, paths in file_hashes.items() if len(paths) > 1}


def get_duplicate_text(
    folder_path: str = "./",
    ignore_list: list[str] = ["TestRunner", "nattapong"],
    include_list: list[str] = None,
    do_normalize: bool = False,
    to_lowercase: bool = False,
) -> str:
    final_list = []
    duplicates = find_duplicate_files(
        folder_path, ignore_list, include_list or [], do_normalize, to_lowercase
    )
    if duplicates:
        for duplicate_group in duplicates.values():
            final_list.append("_" * 90)
            for file_path in duplicate_group:
                final_list.append(f"{file_path}")
            final_list.append("_" * 90)
        return "\n".join(final_list)
    else:
        return "No"


def main():
    exclude_list = ["TestRunner", "nattapong"]
    include_list = []
    folder_path = "./"
    do_normalize = True
    to_lowercase = True
    duplicate_word = get_duplicate_text(
        folder_path, exclude_list, include_list, do_normalize, to_lowercase
    )
    print(duplicate_word)


if __name__ == "__main__":
    main()
