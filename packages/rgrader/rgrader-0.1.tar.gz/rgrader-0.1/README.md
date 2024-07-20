# HOW TO USE GRADER

rgrader is a new generation modern superior !NO ALTERNATIVE! grading tool for programming assignments.

There are TWO(as of now) main ways to use it: either with txt file, or through unittests.

Assure that pip is installed on your machine.
To install, do this inside your shell:

```shell
pip install rgrader
```

To run:

```shell
grade -t [path_to_tests] -s [path_to_solution.py]
```

Unittest files look like this:

```python
import unittest
from rgrader import add_points, run_solution


class TestName(unittest.TestCase):
    """
    Comment for your test
    """

    @add_points(4)  # how much this test will cost in terms of points
    @run_solution(["6", "throttle", "31", "190", "-30"])  # expected input
    def test_test1(self, output):  # each test method must be in form test_<name>
        """
        test's description
        """
        self.assertEqual(output, "37", "test message")

    @add_points(4)
    @run_solution(["5", "break", "11", "10", "-3"])
    def test_test2(self, output):
        """
        test's description
        """
        self.assertEqual(output, "37", "test message")

```

If you want to create tests with a simple text file create a file with .tests extension. Such files must conform to the
following conventions:

```text
# test_<name> <optional points for it>
<optional test message>
INPUT
<inputs per line>
OUTPUT
<output per line>
# test_second 10
fix your code!
INPUT
2
3
OUTPUT
2+3=5
# test_third_example 
INPUT
123
1
OUTPUT
123+1=124
```