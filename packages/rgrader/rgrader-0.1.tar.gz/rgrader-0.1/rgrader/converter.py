import unittest

from .decorators import add_points, run_solution


class WrongStructure(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)


def func_generator(inputs: list[str], exp_output: str, points: str, test_msg: str):
    try:
        @add_points(float(points))
        @run_solution(inputs)
        def testing_func(self, output: list[str]):
            self.assertEqual(output, exp_output, test_msg)

        return testing_func
    except ValueError as e:
        print(e, "'points' must be a number with floating point")


def txt_to_func(test_file: str) -> dict:
    with open(test_file, "r", encoding="utf-8") as file:

        func_dict = {}
        file = file.read()

        # handle wrong test file structure
        input_lines = file.count("INPUT")
        output_lines = file.count("OUTPUT")
        cases_num = file.count("# test_")

        if input_lines != output_lines or output_lines != cases_num or input_lines != cases_num:
            raise WrongStructure(
                "Each test case should look like:\n# test_<name> <points>\n\
<optional test comment>\nINPUT\n<input per line>\nOUTPUT\n<output per line>")

        test_cases = filter(lambda x: bool(x), file.split("# "))

        for test in test_cases:
            test = test.strip().split("\n")

            if len(test) < 3:
                raise WrongStructure("Not enough elements in test case")

            if " " in test[0]:
                name, points = test[0].split(" ")
            else:
                name, points = test[0], 0

            if test[1] != "INPUT" and test[2] != "INPUT":
                raise WrongStructure(
                    f"INPUT goes right after test's name. It should look like:\n# {name} {points}\nINPUT")

            test_msg = ""
            if test[2] == "INPUT":
                test_msg = test[1]

            inputs_start = test.index("INPUT")

            if "OUTPUT" not in test:
                raise WrongStructure(f"No OUTPUT for {name}.")

            output_start = test.index("OUTPUT")

            if output_start - inputs_start == 1:
                raise WrongStructure(f"No inputs are given for {name}.")

            if len(test) - 1 == output_start:
                raise WrongStructure(f"No outputs are given for {name}.")

            inputs = test[inputs_start + 1:output_start]
            outputs = "\n".join(test[output_start + 1:])

            func_dict[name] = func_generator(inputs, outputs, points, test_msg)

        return func_dict


def create_unittest(test_file: str) -> type:
    return type("tests", (unittest.TestCase,), txt_to_func(test_file))
