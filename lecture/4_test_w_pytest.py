"""
- Tests get added to the test module, they then get organized by code type. 
- Test is carried out once to ensure code behaves as expected within the test.
- Code gets organized in a separate folder as a series of modules.
"""
import pytest


def test_always_passes():
    assert True
    
def test_always_fails():
    assert False



# Monkeypatch
def user_input():
    return input("Cats or Dogs?")

def test_uppercase():
    assert "I love python".upper() == "I LOVE PYTHON"

def test_reversed():
    assert list(reversed[1,2,3,4]) == [4,3,2,1]

def test_input(monkeypatch):
    # monkeypatch the "input" function,
    # so that it returns "Cats"
    # This simulates the user entering "Cats"
    # in the terminal
    monkeypatch.setattr('builtin.input',
                        lambda _: "Cats")
    assert user_input().lower() == 'cats'

# Fixtures with pytest
@pytest.fixture # the function with this tag is purely to run the test functions, not necessarily for actual application logic

def format_data_for_display(course_data):
    return formatted_display

def format_data_for_csv_export(course_data):
    # Implement Me!
    return formatted_display

@pytest.fixture
def example_course_data():
    return [
        {
            "id": 206,
            "name": "Intro to Python",
            "instructor": "Joe",
            "room_number": 132
        },
        {
            "id": 256,
            "name": "Modern Software Concepts in Python",
            "instructor": "Liv",
            "room_number": 133
        }
    ]

def test_format_data_for_display(example_course_data):
    assert format_data_for_display(example_course_data) == [
        "206: Intro to Python",
        "256: Modern Software Concepts in Python"
    ]

def test_format_data_for_csv_export(example_course_data):
    assert format_data_for_csv_export(example_course_data) == [
    
    id, name, instructor, room_number
    206, Intro to Python, Joe, 132
    256, Modern Software Concepts in Python, Liv, 133
    
    ]


