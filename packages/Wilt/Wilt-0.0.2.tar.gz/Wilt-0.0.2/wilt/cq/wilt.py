import fileinput
import re
from functools import reduce
from typing import Literal, TextIO


_leading_ws = re.compile(r'^(\s+)\w')

def wilt(fp, *, indent=4) -> float:
    """
    Calculate WILT metric.

    It stands for Whitespace Integrated over Lines of Text, and it's
    measured in indentations.
    """

    return reduce(lambda r, l: r + sum(len(ws) for ws in _leading_ws.findall(l)), fp, 0) / indent


def run_cmd(files: Literal['-'] | list[str], indent: int, output_file: TextIO, **kwargs):
    with fileinput.input(files) as fp:
        output_file.write('{}\n'.format(wilt(fp, indent=indent)))
