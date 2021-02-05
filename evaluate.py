import regex
from typing import *
from collections.abc import Iterable
from tokens import *


def evaluate_code(code: str):
    pos = 0
    context = Context()

    code = code.split('\n')
    while pos < len(code):
        matched = False
        line = remove_comments(code[pos])

        for line_type in lines:
            if regex.match(regex.compile(line_type.re, regex.MULTILINE), line):
                pos = line_type(line).eval(context, pos, code)
                matched = True
                break

        if not matched:
            raise SyntaxError('Unexpected line type')

    print(context)


if __name__ == '__main__':
    with open('test.erb', 'r') as f:
        evaluate_code(f.read(-1))
