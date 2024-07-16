from problem import Problem


class Topic:
    """topic is class that contain many exercise, use to evaluate all lab at once"""

    def __init__(self, topic_name: str, exercises: list[Problem]):
        self.topic_name = topic_name
        self.exercises = exercises

    def get_score_all_exercise(self) -> str:
        final_result = []
        for exercise in self.exercises:
            final_result.append(exercise.problem_name)
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
