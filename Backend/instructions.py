import sys, inspect
from random_access_list import *


encoding = 'utf-8'


def toint(x):
    if type(x) == int:
        return x
    else:
        return x.__int__()


def string(x):
    encoded = list(bytearray(bytes(x, encoding)))
    return [len(encoded), ] + encoded


class NOP:
    @classmethod
    def __int__(cls):
        return instructions.index(cls)

    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class HALT(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, None


class PUSH(NOP):
    @staticmethod
    def run(stack: list, sstack: list, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(code[ic+1])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class POP(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class PUSHS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        length = code[ic+1]
        sstack.append(bytes(code[ic+2:ic+2+length]).decode(encoding))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + length + 2


def binoper(stack, func):
    a = stack.pop()
    b = stack.pop()
    stack.append(func(a, b))


class POPS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class ADD(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x + y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class SUB(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x - y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class MUL(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x * y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class DIV(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x / y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class AND(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: int(x and y))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class OR(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: int(x or y))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class XOR(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: int(bool(x) != bool(y)))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class BAND(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x & y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class BOR(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x | y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class BXOR(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x ^ y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class LSHFT(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x << y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class RSHFT(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x >> y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


def uoper(stack, func):
    x = stack.pop()
    stack.append(func(x))


class NOT(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        uoper(stack, lambda x: int(not x))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class BNOT(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        uoper(stack, lambda x: ~x)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1
    

class CMP(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: (x - y)//abs(x - y))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class SEQ(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(sstack, lambda x, y: int(x == y))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class CATS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(sstack, lambda x, y: x + y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class MULS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        a = sstack.pop()
        b = stack.pop()

        stack.append(a * b)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class JMP(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        addr = stack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, addr


class JEQ(NOP):
    matches = [0]

    @classmethod
    def run(cls, stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        addr = stack.pop()
        condition = stack.pop()
        if condition in cls.matches:
            return stack, sstack, var, svar, code, jmptable, addr
        else:
            return stack, sstack, var, svar, code, jmptable, ic + 1


class JNE(JEQ):
    matches = [-1, 1]


class JGT(JEQ):
    matches = [1, ]


class JLE(JEQ):
    matches = [-1, ]


class ADDR(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        addr = jmptable.get(sstack.pop())
        if addr:
            stack.push(addr)
            return stack, sstack, var, svar, code, jmptable, stackp, sstackp, addr
        else:
            stack.push(-1)
            return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class ST(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        var[code[ic+1]] = stack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LD(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(var[code[ic+1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class STS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        svar[code[ic + 1]] = sstack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LDS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.append(var[code[ic + 1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class STRI(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        i = stack.pop()
        s = sstack.pop()
        sstack.append(s[i])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class LEN(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(len(sstack.pop()))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class PRT(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        s = sstack.pop()
        print(s)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class INP(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.append(input())
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class PUSHLOC(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stackp.append(stack.len() - 1)


class PUSHLOCS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstackp.append(sstack.len() - 1)


class POPLOC(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stackp.pop()


class POPLOCS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstackp.pop()


class STLOC(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        var[stackp[-1] + code[ic + 1]] = stack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LDLOC(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(var[stackp[-1] + code[ic + 1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class STLOCS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        svar[sstackp[-1] + code[ic + 1]] = sstack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LDLOCS(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.append(svar[sstackp[-1] + code[ic + 1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class GETADDR(NOP):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(ic)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


instructions = []

for name, obj in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(obj):
        instructions.append(obj)
