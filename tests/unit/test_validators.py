from app.utils.validators import Validator


def test_validate_text():
    assert Validator.validate_text("hello") is True


def test_validate_skill_list():
    assert Validator.validate_skill_list(["Python"]) is True


def test_validate_cgpa():
    assert Validator.validate_cgpa(8.5) is True