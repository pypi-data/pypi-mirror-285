from py_output_compare.compare_file import (
    get_compare_output_by_path,
    get_score_by_path,
)
from py_output_compare.find_file import (
    find_files,
    find_first_file_contain_id,
    find_first_file,
    count_files,
)
from py_output_compare.test_case import TestCase
from py_output_compare.find_duplicate import get_duplicate_text


class Problem:

    def __init__(
        self,
        problem_name: str,
        input_cases: list[TestCase] = [TestCase("")],
        need_to_contain_words: list[str] = [],
        do_normalize_input: bool = False,
        timeout_setting: float = 6,
        teacher_name: str = "manee-2024",
    ):
        self.problem_name = problem_name
        self.input_cases = input_cases
        self.need_to_contain_words = need_to_contain_words
        self.do_normalize_input = do_normalize_input
        self.teacher_name = teacher_name
        self.timeout_setting = timeout_setting

    def get_max_score(self) -> int:
        return len(self.input_cases) + len(self.need_to_contain_words)

    def get_teacher_path(self) -> str:
        return find_first_file_contain_id(self.problem_name, self.teacher_name)

    def get_score_all(self) -> str:
        teacher_file_path = self.get_teacher_path()
        all_student = find_files(self.problem_name)
        result = []

        max_score = self.get_max_score()
        number_of_student = 0
        student_score_sum = 0

        print(f"start evaluate {self.problem_name}...")

        for student_file_path in all_student:
            score_num, score_emoji = get_score_by_path(
                student_file_path,
                teacher_file_path,
                self.input_cases,
                self.need_to_contain_words,
                self.do_normalize_input,
                self.timeout_setting,
            )

            number_of_student += 1
            student_score_sum += score_num

            this_student_score = f"{score_num} {score_emoji} {student_file_path}"
            result.append(this_student_score)
        problem_score_max = max_score * number_of_student

        score_summary = (
            f"{number_of_student} students submit file\n"
            f"score_summary: [{student_score_sum:<4}]-({problem_score_max:<4}) [get]-(max)\n"
            f"average_score: [{(student_score_sum/number_of_student):<4.2f}]-({max_score:<4}) [get]-(max)"
        )

        result.append("-" * 80)
        result.append(score_summary)

        return "\n".join(result)

    def get_score_by_path_all(self, student_path_list: list[str]) -> str:
        teacher_file_path = self.get_teacher_path()
        result = []
        for student_file_path in student_path_list:
            score_num, score_emoji = get_score_by_path(
                student_file_path,
                teacher_file_path,
                self.input_cases,
                self.need_to_contain_words,
                self.do_normalize_input,
                self.timeout_setting,
            )

            final_score_output = f"{score_num} {score_emoji} {student_file_path}"
            result.append(final_score_output)
        return "\n".join(result)

    def get_score_by_path(self, student_path: str) -> str:
        teacher_file_path = self.get_teacher_path()
        score_num, score_emoji = get_score_by_path(
            student_path,
            teacher_file_path,
            self.input_cases,
            self.need_to_contain_words,
            self.do_normalize_input,
            self.timeout_setting,
        )

        final_score_output = f"{score_num} {score_emoji} {student_path}"
        return final_score_output

    def get_score_fast(self, student_path: str, teacher_path: str) -> str:
        score_num, score_emoji = get_score_by_path(
            student_path,
            teacher_path,
            self.input_cases,
            self.need_to_contain_words,
            self.do_normalize_input,
            self.timeout_setting,
        )

        final_score_output = f"{score_num} {score_emoji} {student_path}"
        return final_score_output

    def get_output_by_path(self, student_path: str) -> str:
        teacher_file_path = self.get_teacher_path()
        result = get_compare_output_by_path(
            student_path,
            teacher_file_path,
            self.input_cases,
            self.need_to_contain_words,
            self.do_normalize_input,
            self.timeout_setting,
        )
        return result

    def get_output_id(self, student_id: str) -> str:
        student_file_path = find_first_file_contain_id(self.problem_name, student_id)
        teacher_file_path = self.get_teacher_path()
        result = get_compare_output_by_path(
            student_file_path,
            teacher_file_path,
            self.input_cases,
            self.need_to_contain_words,
            self.do_normalize_input,
            self.timeout_setting,
        )
        return result

    def get_output_from_upload_file(self, upload_file_name="to_evaluate.py") -> str:
        student_file_path = find_first_file(upload_file_name)
        teacher_file_path = self.get_teacher_path()
        result = get_compare_output_by_path(
            student_file_path,
            teacher_file_path,
            self.input_cases,
            self.need_to_contain_words,
            self.do_normalize_input,
            self.timeout_setting,
            score_web_format=True,
        )
        return result

    def get_score_id(self, student_id: str) -> str:
        teacher_file_path = self.get_teacher_path()
        student_file_path = find_first_file_contain_id(self.problem_name, student_id)

        score_num, score_emoji = get_score_by_path(
            student_file_path,
            teacher_file_path,
            self.input_cases,
            self.need_to_contain_words,
            self.do_normalize_input,
            self.timeout_setting,
        )

        final_score_output = f"{score_num} {score_emoji} {student_file_path}"
        return final_score_output

    def get_submit_count(self) -> int:
        return count_files(self.problem_name)

    def get_duplicate_file(
        self,
        folder_path="./",
        ignore_list=["TestRunner", "nattapong"],
        do_normalize=True,
        to_lowercase=True,
    ) -> None:

        return get_duplicate_text(
            folder_path, ignore_list, [self.problem_name], do_normalize, to_lowercase
        )

    def get_exact_duplicate(
        self,
        folder_path="./",
        ignore_list=["TestRunner", "nattapong"],
    ) -> None:

        return get_duplicate_text(
            folder_path,
            ignore_list,
            [self.problem_name],
            do_normalize=False,
            to_lowercase=False,
        )

    def get_duplicate_report(self) -> str:
        result = []
        result.append("-" * 90)
        result.append(f"📄 [ {self.problem_name} ]")
        result.append("-" * 90)

        duplicate_list = self.get_duplicate_file()
        exact_duplicate_list = self.get_exact_duplicate()

        if duplicate_list != "No":
            result.append(f"🌕{self.problem_name}🌕 normalize")
            result.append(duplicate_list)
            result.append("")
        if exact_duplicate_list != "No":
            result.append(f"🔴{self.problem_name}🔴 exact")
            result.append(exact_duplicate_list)
            result.append("")
        return "\n".join(result)
