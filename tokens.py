from parsers import *
from context import *
from typing import *
from find import *
import sys


class Line:
    re = None

    def __init__(self, string):
        pass

    def eval(self, context, pos, code):  # this code is to find matching ENDIF or something like that.
        new_pos = pos + 1

        return new_pos
        # return value is new pos(line no.). all other functions like printing, changing value...
        # etc is processed as side effect.


class BlankLine(Line):
    re = r'^[ \t\n]*$'


class EquLine(Line):
    re = r'^[^=]+[ \t]*=[ \t]*[^=\n\t ]+'

    def __init__(self, string):
        super().__init__(string)
        self.a, self.b = string.split('=')
        self.a = self.a.strip()
        self.b = self.b.strip()

    def eval(self, context: Context, pos, code):
        set_global_var(self.a, self.b, context)

        return super().eval(context, pos, code)


class InstLine(Line):
    re = None

    def __init__(self, string):
        super().__init__(string)
        self.Inst = regex.split('[ \t]+', string.strip())[0].strip()
        try:
            self.arg = string.strip()[len(self.Inst):].strip()
        except IndexError:
            self.arg = None

    def eval(self, context: Context, pos, code):
        return super().eval(context, pos, code)


class PrintLine(InstLine):
    re = r'[ \t]*PRINT .+'

    def __init__(self, string):
        super().__init__(string)

    def eval(self, context: Context, pos, code):
        print(str_eval(self.arg, context))

        return super().eval(context, pos, code)


class EndifLine(InstLine):
    re = r'[ \t]*ENDIF'


class ElseLine(InstLine):
    re = r'[ \t]*ELSE'

    def eval(self, context: Context, pos, code):
        pos = find(EndifLine.re, code, pos)
        return pos


class IfLine(InstLine):
    re = r'[ \t]*IF .+'

    def __init__(self, string):
        super().__init__(string)

    def eval(self, context: Context, pos, code):
        if exp_eval(self.arg, context):
            pos += 1
        else:
            pos = min(find(EndifLine.re, code, pos), find(ElseLine.re, code, pos))
            # find else or endif and skip it (to not skip the inside of else. else will skip to endif if executed)

        return pos


class SifLine(InstLine):
    re = r'[ \t]*SIF'

    def __init__(self, string):
        super().__init__(string)

    def eval(self, context, pos, code):
        if exp_eval(self.arg, context):
            pos += 1
        else:
            pos += 2

        return pos


class CallLine(InstLine):
    re = r'[ \t]*CALL'

    def __init__(self, string: str):
        super().__init__(string)
        self.farg = self.arg[len(self.arg.split(' ')[0])+1:]
        args = [i.strip() for i in self.farg.split(',')]
        self.arg = self.arg.split(' ')[0:1] + args

    def eval(self, context: Context, pos, code):
        new_pos = find_func('@' + self.arg[0], code)  # find from top of the file

        arg_list = [literal_eval(i, context) for i in self.arg[1:]]

        context.push_stack(pos)
        for i, arg in enumerate(FuncLine(code[new_pos]).arg):
            set_global_var_by_value(arg, arg_list[i][0], context)

        return new_pos


class ReturnLine(InstLine):
    re = r'RETURN'

    def eval(self, context, pos, code):
        new_pos = context.get_stack_elem().return_pos + 1
        return_var, is_str = literal_eval(self.arg, context)
        context.pop_stack()
        set_global_var_by_value('RESULT', return_var, context)
        return new_pos


class RestartLine(InstLine):
    re = r'RESTART'

    def eval(self, context: Context, pos, code):
        new_pos = find_func(FuncLine.re, code, pos, True)
        return new_pos


class FuncLine(Line):
    re = r'^@'

    def __init__(self, string: str):
        super().__init__(string)
        self.name = string[1:].split(' ')[0]
        try:
            self.arg = [i.strip() for i in string[len(self.name) + 2:].split(',')]
        except IndexError:
            self.arg = []

    def eval(self, context, pos, code):
        print('function should not be normally called.')
        sys.exit(1)


lines = [
    BlankLine,
    EquLine,
    PrintLine,
    IfLine,
    EndifLine,
    ElseLine,
    SifLine,
    CallLine,
    FuncLine,
    ReturnLine,
    RestartLine
]
