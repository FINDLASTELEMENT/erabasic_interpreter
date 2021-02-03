import regex
from typing import *

class Context:
    def __init__(self):
        self.functions: Dict[str, int] = {} # function name: line no.
        self.globalValuables: Dict[str, Union[str, int]] = {} # valuable name: value
        self.labels: Dict[str, Union[str, int]] = {} # label name: label no.

    def setFunc(self, name, pos):
        self.functions[name] = pos

    def setValue(self, name, value):
        self.globalValuables[name] = value

    def setLbl(self, name, pos):
        self.labels[name] = pos

    def getValue(self, name):
        result = None

        if name in self.globalValuables.keys():
            return self.globalValuables[name]
        
        if name in self.functions.keys():
            pass
        
        print(name, self)
        raise NameError

    def __repr__(self):
        return f'{self.globalValuables} {self.functions} {self.labels}'

def expEval(string: str, context):
    string = regex.split(r'(\+|-|\*|/|==|!=)', string)
    for i in range(len(string)//2+1)[::2]:
        stripped = string[i].strip()
        if not regex.match(regex.compile(r'([1-9])'), stripped):
            string[i] = str(context.getValue(stripped))
    
    string = ''.join(string)        

    return int(eval(string))

def strEval(string, context):
    result = ""
    expr = ""

    inExpr = False
    exprRe = r'(\{|\}|%)'
    for i in string:
        if regex.match(exprRe, i):
            if inExpr:
                inExpr = False
                result += str(expEval(expr, context))
                expr = ""

            else:
                inExpr = True
        else:
            if inExpr:
                expr += i
            else:
                result += i

    return result

def idEval(string, context): # valuable, function, array... etc
    pass

def codeeval(code: str):
    pos = 0
    context = Context()
    code = code.split('\n')
    while pos < len(code):
        line = code[pos].split(';')[0]
        for linetype in lines:
            matched = False
            if regex.match(regex.compile(linetype.re, regex.MULTILINE), line):
                #print(line, linetype, pos)
                pos = linetype(line).eval(context, pos, code)
                matched = True
                break
        if not matched:
            print(line, 'unexpected line type')

    print(context)
        


def find(re, code, pos):
    result = int(pos)
    while not regex.match(regex.compile(re, regex.MULTILINE), code[result]):
        result += 1
    #result += 1
    return result

# line types

class Line:
    re = None

    def __init__(self, string):
        pass

    def eval(self, context, pos, code): # code is to find matching ENDIF or somthing like that.
        newpos = pos + 1

        return newpos # return value is new pos(line no.). all other functions like printing, changing value... etc is processed as side effect.

class BlankLine(Line):
    re = r'^[ \t\n]*$'

class EquLine(Line):
    re = r'^[^=]+[ \t]*=[ \t]*[^=\n\t ]+'

    def __init__(self, string):
        self.a, self.b = string.split('=')
        self.a = self.a.strip()
        self.b = self.b.strip()

    def eval(self, context: Context, pos, code):
        context.setValue(self.a, expEval(self.b, context))

        return super().eval(context, pos, code)


class InstLine(Line):
    re = None

    def __init__(self, string):
        self.Inst = regex.split('[ \t]+', string.strip())[0].strip()
        try:
            self.arg = string.strip()[len(self.Inst):].strip()
        except:
            self.arg = None

    def eval(self, context: Context, pos, code):
        return super().eval(context, pos, code)


class PrintLine(InstLine):
    re = r'[ \t]*PRINT .+'

    def __init__(self, string):
        super().__init__(string)

    def eval(self, context: Context, pos, code):
        print(strEval(self.arg, context))

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
        if expEval(self.arg, context):
            pos += 1
        else:
            pos = min(find(EndifLine.re, code, pos), find(ElseLine.re, code, pos)) + 1 # find else or endif and skip it (to not skip the inside of else. else will skip to endif if executed)

        return pos

class SifLine(InstLine):
    re = r'[ \t]*SIF'

    def __init__(self, string):
        super().__init__(string)

    def eval(self, context, pos, code):
        if expEval(self.arg, context):
            pos += 1
        else:
            pos += 2

        return pos


lines = [
    BlankLine,
    EquLine,
    PrintLine,
    IfLine,
    EndifLine,
    ElseLine,
    SifLine
]

if __name__ == '__main__':
    with open('test.erb', 'r') as f:
        codeeval(f.read(-1))
