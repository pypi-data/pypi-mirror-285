"""Util functions"""
from subprocess import run

def capture_io(script_name: str, inputs: list) -> str:
    """
    :param script_name:  name of the script to be tested
    :param inputs: list of inputs, one element per line
    :return: returns script output for the test case
    """
    inputs = "\n".join(inputs)
    p = run(
        f"python {script_name}",
        shell=True,
        input=inputs,
        text=True,
        capture_output=True,
    )

    return p.stdout.strip()
