import regex
from typing import *
from context import *
import sys


oper_re = r'(\+|-|\*|/|==|!=|<=|>=|<|>)'


def remove_comments(line:str):
    result = ""
    in_expr = False
    for char in line:
        if char == '"':
            in_expr = not in_expr

        if not char == ";":
            result += char
        elif not in_expr:
            break

    return result


def remove_whitespace(line: str):
    index = 0
    while regex.match(r'[ \t]', line[index:]):
        index += 1

    return line[index:]


def get_line(code, line: int) -> str:
    return remove_whitespace(remove_comments(code[line]))


def exp_eval(string: str, context: Context):
    string = regex.split(oper_re, string)
    for i in range(0, len(string), 2):
        stripped = string[i].strip()
        try:
            value = context.get_var(stripped)
        except ValueError:
            value = stripped
        else:
            if type(value) == str:
                string[i] = '"""' + value + '"""'
            else:
                string[i] = str(value)

    string = ''.join(string)

    return eval(string)
    # todo


def literal_eval(string: str, context: Context):
    if string[0] == '"' and string[-1] == '"':
        return str_eval(string[1:-1], context), VarType.STR_SCALA
    else:
        result = exp_eval(string, context)
        if type(result) == str:
            result_type = VarType.STR_SCALA
        else:
            result_type = VarType.INT_SCALA
            result = int(result)
        return result, result_type


def str_eval(string, context):
    result = ""
    expr = ""

    in_expr = False
    expr_re = r'(\{|\}|%)'
    for i in string:
        if regex.match(expr_re, i):
            if in_expr:
                in_expr = False
                result += str(literal_eval(expr, context)[0])
                expr = ""

            else:
                in_expr = True
        else:
            if in_expr:
                expr += i
            else:
                result += i
    # todo : add \@ support
    return result


if __name__ == '__main__':
    c = Context()
    c.add_var("a", 1, VarType.INT_SCALA)
