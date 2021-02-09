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
        b, var_type = literal_eval(self.b, context)
        try:
            context.set_var(self.a, b)
        except ValueError:
            context.add_var(self.a, b, var_type)

        return super().eval(context, pos, code)


class IncreaseLine(Line):
    re = r'[A-Za-z]* ?(\+\+|--)'

    def __init__(self, string: str):
        super(IncreaseLine, self).__init__(string)

        if '+' in string:
            self.var = string.split('++')
            self.add_value = 1
        else:
            self.var = string.split('--')
            self.add_value = -1

        self.var = self.var[0] or self.var[1]
        self.var = self.var.strip()

    def eval(self, context, pos, code):
        context.set_var(self.var, context.get_var(self.var) + self.add_value)
        return pos + 1


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


class PrintLine(InstLine): # todo
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
        self.arg = self.arg.split(',')[0:1] + args

    def eval(self, context: Context, pos, code):
        new_pos = find_func('@' + self.arg[0], code)  # find from top of the file

        arg_list = [literal_eval(i, context) for i in self.arg[1:]]

        context.push_stack(pos)
        context.add_var('ARG', IntArray(0, (1000, )), VarType.INT_ARY, True)
        context.add_var('ARGS', StrArray("", (100, )), VarType.STR_ARY, True)

        for i, arg in enumerate(FuncLine(get_line(code, new_pos - 1)).arg):
            try:
                context.add_var(arg, arg_list[i][0], arg_list[i][1])
            except ValueError:
                context.set_var(arg, arg_list[i][0])

        return new_pos


class ReturnLine(InstLine):
    re = r'[ \t]*RETURN'

    def eval(self, context, pos, code):
        new_pos = context.get_stack_elem().return_pos + 1
        return_var, _ = literal_eval(self.arg, context)
        context.pop_stack(return_var)
        return new_pos


class RestartLine(InstLine):
    re = r'[ \t]*RESTART'

    def eval(self, context: Context, pos, code):
        new_pos = find_func(FuncLine.re, code, pos, True)
        return new_pos


class GotoLine(InstLine):
    re = r'GOTO'
    flag = 'GOTO'

    def eval(self, context: Context, pos, code):
        new_pos = find_func(r'\$' + self.arg, code)
        context.flags[self.flag] = True
        return new_pos


class ForLine(InstLine):
    re = r'FOR'
    start_name = 'FOR_START'
    end_name = 'FOR_END'
    step_name = 'FOR_STEP'

    def __init__(self, string: str):
        super(ForLine, self).__init__(string)

        self.args = [i.strip() for i in self.arg.split(',')]
        self.index_var = self.args[0]
        if len(self.args) > 4:
            raise ValueError('Too many arguments!')

        self.start = ConstArg()
        self.end = ConstArg()
        self.step = ConstArg()

    def eval(self, context: Context, pos, code):
        try:
            ConstArg.remove(context, self.start_name, pos)
        except KeyError:
            pass
        try:
            ConstArg.remove(context, self.end_name, pos)
        except KeyError:
            pass
        try:
            ConstArg.remove(context, self.step_name, pos)
        except KeyError:
            pass

        self.start.init(context, self.start_name, pos, exp_eval(self.args[1], context))
        self.end.init(context, self.end_name, pos, exp_eval(self.args[2], context))
        if len(self.args) == 4:
            self.step.init(context, self.step_name, pos, exp_eval(self.args[3], context))

        context.flags[GotoLine.flag] = False
        context.auto_add_var(self.index_var, self.start.get(context), VarType.INT_SCALA)

        return pos + 1


class NextLine(InstLine):
    re = r'NEXT'
    matching_line = ForLine

    def __init__(self, string):
        super(NextLine, self).__init__(string)
        self.end = ConstArg()
        self.step = ConstArg()

    @staticmethod
    def update_index(index: int, end: int, step: int):
        if index >= end - 1 or index + step >= end - 1:
            return None
        else:
            return index + step

    def eval(self, context: Context, pos, code):
        if not context.flags[GotoLine.flag]:
            new_pos = find(self.matching_line.re, code, pos, reverse=True)
            for_pos = new_pos - 1
            for_line = self.matching_line(get_line(code, for_pos))
            args = for_line.args
            index_var = for_line.index_var

            self.end.init(context, ForLine.end_name, for_pos, exp_eval(args[1], context))
            if len(args) == 4:
                self.step.init(context, ForLine.step_name, for_pos, exp_eval(args[2], context))
            else:
                self.step.init(context, ForLine.step_name, for_pos, 1)

            current = context.get_var(index_var)
            next_index = self.update_index(current, self.end.get(context), self.step.get(context))

            if next_index:
                context.set_var(self.matching_line(get_line(code, new_pos-1)).index_var, next_index)
            else:
                return pos + 1

            return new_pos
        else:
            return pos + 1


class RepeatLine(ForLine):
    re = r'REPEAT'

    def __init__(self, string):
        super(RepeatLine, self).__init__(string)
        self.args = ['COUNT', '1', self.arg]
        self.index_var = 'COUNT'

    def eval(self, context: Context, pos, code):
        return super().eval(context, pos, code)


class RendLine(NextLine):  # todo: remove code duplication
    re = r'REND'
    matching_line = RepeatLine

    @staticmethod
    def update_index(index: int, end: int, step: int):
        if index > end or index + step > end:
            return None
        else:
            return index + step

    def eval(self, context: Context, pos, code):
        if not context.flags[GotoLine.flag]:
            new_pos = find(self.matching_line.re, code, pos, reverse=True)
            repeat_pos = new_pos - 1
            repeat_line = self.matching_line(get_line(code, repeat_pos))
            args = repeat_line.args
            index_var = repeat_line.index_var

            self.end.init(context, ForLine.end_name, repeat_pos, exp_eval(args[1], context))
            if len(args) == 4:
                self.step.init(context, ForLine.step_name, repeat_pos, exp_eval(args[2], context))
            else:
                self.step.init(context, ForLine.step_name, repeat_pos, 1)

            current = context.get_var(index_var)
            next_index = self.update_index(current, self.end.get(context), self.step.get(context))

            if next_index:
                context.set_var(self.matching_line(get_line(code, new_pos-1)).index_var, next_index)
            else:
                return pos + 1

            return new_pos
        else:
            return pos + 1


class WhileLine(InstLine):
    re = r'WHILE'

    def eval(self, context: Context, pos, code):
        if exp_eval(self.arg, context):
            return pos + 1
        else:
            return find(WendLine.re, code, pos)


class WendLine(InstLine):
    re = r'WEND'

    def eval(self, context: Context, pos, code):
        return find(WhileLine.re, code, pos, True) - 1


# all matching instruction class should be in same index
loop_start = [
    RepeatLine,
    ForLine,
    WhileLine
]

loop_end = [
    RendLine,
    NextLine,
    WendLine
]


class ContinueLine(InstLine):
    re = r'CONTINUE'

    def eval(self, context: Context, pos, code):
        return find_func(f'({"|".join([i.re for i in loop_end])})', code, pos) - 1  # must execute REPEAT instruction


class BreakLine(InstLine):
    re = r'BREAK'

    def eval(self, context: Context, pos, code):
        maximum = find_func(f'({"|".join([e.re for e in loop_end])})', code, pos)

        return maximum


class FuncLine(Line):
    re = r'^@'

    def __init__(self, string: str):
        super().__init__(string)
        self.name = string[1:].split(',')[0]
        try:
            self.arg = [i.strip() for i in string[len(self.name) + 2:].split(',')]
        except IndexError:
            self.arg = []

    def eval(self, context, pos, code):
        context.pop_stack()
        context.push_stack(-1)
        return pos + 1


class LabelLine(Line):
    re = r'\$'


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
    RestartLine,
    GotoLine,
    RepeatLine,
    RendLine,
    ContinueLine,
    BreakLine,
    LabelLine,
    ForLine,
    NextLine,
    WhileLine,
    WendLine,
    IncreaseLine
]
