"""Module for global variables"""

# Path to the solution script that test will be run on
testing_script_path = ""


def set_testing_script_path(testing_script_path_: str) -> None:
    """Set the testing script path global variable"""
    global testing_script_path
    testing_script_path = testing_script_path_


def get_testing_script_path() -> str:
    """Return the testing script path global variable"""
    return testing_script_path
