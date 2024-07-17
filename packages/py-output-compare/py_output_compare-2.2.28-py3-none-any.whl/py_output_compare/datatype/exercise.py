from py_output_compare.datatype.problem import Problem


class Exercise:
    """topic is class that contain many exercise, use to evaluate all lab at once"""

    def __init__(self, exercise_name: str, problems: list[Problem]):
        self.exercise_name = exercise_name
        self.problems = problems

    def get_score_all_exercise(self) -> str:
        final_result = []
        for exercise in self.exercises:
            final_result.append(exercise.lab_name)
            final_result.append(exercise.get_score_all())
            final_result.append("=" * 80)
        return "\n".join(final_result)

    def get_score_id(self, student_id: str) -> str:
        final_result = []
        for exercise in self.exercises:
            final_result.append(exercise.get_score_id(student_id))
        return "\n".join(final_result)

    def get_output_id(self, student_id: str) -> str:
        final_result = []
        for exercise in self.exercises:
            final_result.append(exercise.get_output_id(student_id))
        return "\n".join(final_result)
