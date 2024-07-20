"""Main grader module"""
import argparse

from .classroom.commands import run_no_args_argparse, get_course, choose_course_work
from .classroom.commands import setup_grade_submissions, grade_submissions
from .test_runner import run_tests_setup_argparse, run_tests

ACTIONS = {
    'run-tests': (run_tests_setup_argparse, run_tests),
    'get-courses': (run_no_args_argparse, get_course),
    'submissions': (setup_grade_submissions, grade_submissions),
    'get-assignments': (run_no_args_argparse, choose_course_work)
}


def grade():
    """
    Run tests for solution script with specified test file and show grade
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("action", help="Action to perform", choices=ACTIONS)

    for setup_function, _ in ACTIONS.values():
        setup_function(argument_parser)

    args = argument_parser.parse_args()
    action = args.action

    if action not in ACTIONS:
        print(f"There is no such action `{action}`. Available actions are: {', '.join(ACTIONS.keys())}")

    ACTIONS[action][1](args)
