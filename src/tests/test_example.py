import pytest

class Student:
    def __init__(self, first_name, last_name, major, years) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def student1():
    return Student("Ali", "Valiyev", "Olim", 3)


def test_student(student1):
    assert student1.first_name == "Ali"
    assert student1.last_name == "Valiyev"
    assert student1.major == "Olim"
    assert student1.years == 3
