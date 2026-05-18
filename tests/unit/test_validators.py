from app.utils.validators import Validator


def test_validate_text():
    assert Validator.validate_text("hello") is True


def test_validator():

    assert validate_cgpa(8.5) == True