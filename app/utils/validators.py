from typing import List


class Validator:

    @staticmethod
    def validate_text(text: str) -> bool:
        return bool(text and text.strip())

    @staticmethod
    def validate_skill_list(skills: List[str]) -> bool:
        return isinstance(skills, list) and len(skills) > 0

    @staticmethod
    def validate_cgpa(cgpa: float) -> bool:
        return 0 <= cgpa <= 10