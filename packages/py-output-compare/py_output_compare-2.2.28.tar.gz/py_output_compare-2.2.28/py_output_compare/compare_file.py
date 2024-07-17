from py_output_compare.test_case import TestCase
from py_output_compare.highlight import highlight_diff
from py_output_compare.normalize_file_output import normalize_output
from py_output_compare.find_file import find_first_file
from py_output_compare.get_file_run_output import get_run_output_by_path


def get_compare_output_by_search_file_name(
    filename_1,
    filename_2,
    user_input_list=[TestCase("")],
    need_to_contain_words=[],
    do_normalize_output=False,
    timeout=6,
):
    filepath_1 = find_first_file(filename_1)
    filepath_2 = find_first_file(filename_2)
    return get_compare_output_by_path(
        filepath_1,
        filepath_2,
        user_input_list,
        need_to_contain_words,
        do_normalize_output,
        timeout,
    )


def get_compare_output_by_path(
    file_path_1,
    file_path_2,
    user_input_list=[TestCase("")],
    need_to_contain_words=[],
    do_normalize_output=False,
    timeout=6,
    score_web_format=False,
):
    result = []
    score = []
    score_num = 0

    for user_input in user_input_list:
        file_output_1 = get_run_output_by_path(
            file_path_1, user_input.case_input, timeout
        )
        file_output_2 = get_run_output_by_path(
            file_path_2, user_input.case_input, timeout
        )

        if do_normalize_output:
            file_output_1 = normalize_output(file_output_1)
            file_output_2 = normalize_output(file_output_2)

        if file_output_2 == file_output_1:
            result.append(f"✅: {user_input.case_name} pass!")
            score.append("🟢")
            score_num += 1

        else:
            result.append("~" * 80)
            result.append(f"❌: {user_input.case_name} fail!")
            score.append("🔴")
            result.append(highlight_diff(file_output_2, file_output_1))

    if len(need_to_contain_words) > 0:
        for word in need_to_contain_words:
            if find_word_in_file(file_path_1, word):
                score.append("🟢")
                score_num += 1
                result.append(get_find_word_in_file_result(file_path_1, word))
            else:
                score.append("🔴")
                result.append(get_find_word_in_file_result(file_path_1, word))

    final_score = "".join(score)

    max_score = len(user_input_list) + len(need_to_contain_words)

    if score_web_format:
        result.append(f"score: {final_score}({score_num}/{max_score})")
    else:
        result.append(f"{final_score} {score_num} {file_path_1}")
    final_compare_result = "\n".join(result)
    return final_compare_result


def get_score_by_path(
    student_path,
    teacher_path,
    user_input_list=[TestCase("")],
    need_to_contain_words=[],
    do_normalize_output=False,
    timeout=6,
):
    score_num = 0
    score = []

    for user_input in user_input_list:
        file_output_student = get_run_output_by_path(
            student_path, user_input.case_input, timeout
        )
        file_output_teacher = get_run_output_by_path(
            teacher_path, user_input.case_input, timeout
        )

    if do_normalize_output:
        file_output_student = normalize_output(file_output_student)
        file_output_teacher = normalize_output(file_output_teacher)

    if file_output_teacher == file_output_student:
        score.append("🟢")
        score_num += 1
    else:
        score.append("🔴")

    if len(need_to_contain_words) > 0:
        for word in need_to_contain_words:
            if find_word_in_file(student_path, word):
                score.append("🟢")
                score_num += 1
            else:
                score.append("🔴")

    final_emoji_score = "".join(score)
    return score_num, final_emoji_score


def get_score_by_search_file_name(
    student_file_name,
    teacher_file_name,
    user_input_list=[TestCase("")],
    need_to_contain_words=[],
    do_normalize_output=False,
    timeout=6,
):
    student_path = find_first_file(student_file_name)
    teacher_path = find_first_file(teacher_file_name)
    return get_score_by_path(
        student_path,
        teacher_path,
        user_input_list,
        need_to_contain_words,
        do_normalize_output,
        timeout,
    )


def find_word_in_file(filename, word):
    try:
        with open(filename, "r") as file:
            content = file.read()
            if word in content:
                return True
            else:
                return False
    except TypeError:
        print(f"Error: File '{filename}' is none")
        return False

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return False
    except IOError:
        print(f"Error: Unable to read file '{filename}'.")
        return False


def get_find_word_in_file_result(file_path, word):
    if find_word_in_file(file_path, word):
        return f'✅: file contain"{word}"'
    else:
        return f'❌: file not contain "{word}"'


def main():
    student_file = find_first_file("bad.py")
    student_file_good = find_first_file("good.py")
    teacher_file = find_first_file("teacher_file.py")

    case1_input = [8.2, 1.8]
    case_input_int = [8.2, 999, 9334]

    test_cases = [
        TestCase(case1_input),
        TestCase(case_input_int),
    ]

    print(student_file)
    print(student_file_good)
    print(teacher_file)

    fail_student = get_compare_output_by_path(student_file, teacher_file, test_cases)
    pass_student = get_compare_output_by_path(
        student_file_good, teacher_file, test_cases
    )
    no_test_input = get_compare_output_by_path(student_file_good, teacher_file)

    print(fail_student)
    print(pass_student)
    print(no_test_input)

    print(get_score_by_search_file_name("good.py", "good.py"))
    print(get_score_by_search_file_name("good.py", "bad.py"))


if __name__ == "__main__":

    main()
