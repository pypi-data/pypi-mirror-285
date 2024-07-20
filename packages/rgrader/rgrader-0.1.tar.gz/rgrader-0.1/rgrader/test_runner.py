import argparse
import inspect
import os
import sys
import unittest
from io import BufferedIOBase
from typing import Type
from unittest import TextTestRunner, TestSuite, TestLoader

from six import StringIO

from .globals import set_testing_script_path, get_testing_script_path


class GraderTestResult(unittest.TextTestResult):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.total_points = None
        self.gained_points = None


class GraderTestRunner(TextTestRunner):
    """Test runner that counts points for each successful test case."""

    def run(self, test_suite: TestSuite) -> GraderTestResult:
        """Run tests and count total grade"""

        test_cases = self._discover_test_cases(test_suite)

        self.stream.writeln(f"=== Running tests for: {get_testing_script_path()} ===")

        result = super().run(test_suite)

        self.show_points(test_cases, result)

        return result

    def show_points(self, test_cases: list[Type], result: GraderTestResult) -> None:
        """
        Count and print gained points
        Args:
            test_case: class of testcase, we must pass it because, after running tests
            it is very hard to find TestCase class
            result: Test result of the TestCase
        """

        all_methods = [method
                       for test_case in test_cases
                       for name, method in inspect.getmembers(test_case)
                       if name.startswith("test_")]


        failed_methods_names = [method._testMethodName for method, _ in result.failures]
        succeeded_methods = [method for method in all_methods if method.__name__ not in failed_methods_names]

        total_points = sum(getattr(method, "points_increment") for method in all_methods)
        gained_points = sum(getattr(method, "points_increment") for method in succeeded_methods)

        self.stream.writeln(f"Grade: {gained_points}/{total_points}")

        result.total_points = total_points
        result.gained_points = gained_points

    @staticmethod
    def _discover_test_cases(test_suite: TestSuite) -> set:
        """Get all TestCase classes from a TestSuite
        Args:

            test_suite: suite where to search for TestCase classes
        """
        discovered_test_cases = set()

        nodes_to_discover = [test_suite]
        while nodes_to_discover:
            node = nodes_to_discover.pop()

            for test in node._tests:
                if isinstance(test, TestSuite):
                    nodes_to_discover.append(test)
                else:
                    discovered_test_cases.add(test.__class__)

        return discovered_test_cases


def load_tests(test_file_path: str) -> TestSuite:
    """Load test suite from file by path

    Args:
        test_file_path: path to the test script

    """
    directory_path = os.path.dirname(test_file_path)
    test_file_name = os.path.basename(test_file_path)

    loader = TestLoader().discover(start_dir=directory_path, top_level_dir=directory_path,
                                   pattern=test_file_name)
    return loader


def run_tests_setup_argparse(argument_parser: argparse.ArgumentParser) -> None:
    """Add necessary arguments to argparse"""
    argument_parser.add_argument("-t", "--tests", help="Path to the test script")
    argument_parser.add_argument("-s", "--solution", help="Path to the solution")


def run_tests_for(script_path: str, test_script_path: str) -> GraderTestResult:
    """
    Run tests for given script with test_script_path
    :param script_path:
    :param test_script_path:
    :return:
    """

    set_testing_script_path(script_path)
    suite = load_tests(test_script_path)
    stream = StringIO()
    runner = GraderTestRunner(stream)

    result = runner.run(suite)

    return result


def run_tests(args: argparse.Namespace) -> None:
    """Perform run tests action"""

    test_file_path = args.tests
    solution_file_path = args.solution

    run_tests_for(script_path=solution_file_path, test_script_path=test_file_path)
