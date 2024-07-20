"""Main grader module"""
import os
import inspect
import argparse
from typing import Type
from unittest import TextTestRunner, TestSuite, TestResult, TestLoader, makeSuite

from globals import set_testing_script_path


class GraderTestRunner(TextTestRunner):
    """Test runner that counts points for each successful test case."""

    def run(self, test_suite: TestSuite) -> TestResult:
        """Run tests and count total grade"""

        test_case = test_suite._tests[0]._tests[0].__class__
        result = super().run(test_suite)

        self.show_points(test_case, result)

        return result

    def show_points(self, test_case: Type, result: TestResult) -> None:
        """
        Count and print gained points
        Args:
            test_case: class of testcase, we must pass it because, after running tests
            it is very hard to find TestCase class
            result: Test result of the TestCase

        """

        all_methods = [method
                       for name, method in inspect.getmembers(test_case)
                       if name.startswith("test_")]

        failed_methods_names = [method._testMethodName for method, _ in result.failures]
        succeeded_methods = [method for method in all_methods if method.__name__ not in failed_methods_names]

        total_points = sum(getattr(method, "points_increment") for method in all_methods)
        gained_points = sum(getattr(method, "points_increment") for method in succeeded_methods)

        self.stream.writeln(f"Grade: {gained_points}/{total_points}")


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


def grade():
    """
    Run tests for solution script with specified test file and show grade
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-t", "--tests", help="Path to the test script")
    argument_parser.add_argument("-s", "--solution", help="Path to the solution")

    args = argument_parser.parse_args()

    test_file_path = args.tests
    solution_file_path = args.solution

    set_testing_script_path(solution_file_path)

    suite = load_tests(test_file_path)

    runner = GraderTestRunner()

    runner.run(suite)
