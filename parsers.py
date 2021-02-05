import regex
from typing import *
from context import *
import sys


def parse_var(string, context: Context):
    stack = context.get_stack_elem()
    if string in stack.int_var.keys():
        return stack.int_var[string]
    elif string in stack.str_var.keys():
        return '"' + stack.str_var[string] + '"'
    elif string in context.global_elem.int_var.keys():
        return context.global_elem.int_var[string]
    elif string in context.global_elem.str_var.keys():
        return '"' + context.global_elem.str_var[string] + '"'

    print(context)
    print(f"NameError: invalid valuable name {string}.")
    assert False


def set_var(var_name, value, target_stack_elem, is_str: bool, index: Iterable[int]=None):
    # todo: after adding array and local arrays (LOCAL, LOCALS, ARG, ARGS) this should change
    if is_str and not index:
        target_stack_elem.str_var[var_name] = value
    elif not index:
        target_stack_elem.int_var[var_name] = value
    elif is_str and index:
        target_stack_elem.str_ary[var_name].set_elem(value, index)
    elif not is_str and index:
        target_stack_elem.int_ary[var_name].set_elem(value, index)


def set_var_by_value(var_name, value, target_stack_elem: StackElem):
    # todo: same as upper
    set_var(var_name, value, target_stack_elem, type(value) == str)


def set_global_var_by_value(var_name, value, context):
    # todo: this should be deleted
    set_var_by_value(var_name, value, context.get_global_elem())


def eval_and_set_var(var_name, value_str, target_stack_elem: StackElem, context):
    _value, is_str = literal_eval(value_str, context)

    set_var(var_name, _value, target_stack_elem, is_str)


def set_global_var(var_name, value_str: str, context):
    # todo: this too
    eval_and_set_var(var_name, value_str, context.get_global_elem(), context)


def exp_eval(string: str, context: Context):
    string = regex.split(r'(\+|-|\*|/|==|!=)', string)
    for i in range(len(string) // 2 + 1)[::2]:
        stripped = string[i].strip()
        if not regex.match(regex.compile(r'([1-9])'), stripped):
            string[i] = str(parse_var(stripped, context))

    string = ''.join(string)

    return eval(string)
    # todo


def literal_eval(string: str, context: Context):
    if string[0] == '"' and string[-1] == '"':
        return str_eval(string[1:-1], context), True

    else:
        return exp_eval(string, context), False


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


def array_eval(string: str, context: Context):
    s = string.strip()
    args = s.split(':')

