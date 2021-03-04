import sys
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


class Inst:
    @classmethod
    def __int__(cls):
        return instructions.index(cls)

    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class HALT(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, None


class NOP(Inst):
    pass


class PUSH(Inst):
    @staticmethod
    def run(stack: list, sstack: list, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(code[ic+1])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class POP(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class PUSHS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        length = code[ic+1]
        sstack.append(bytes(code[ic+2:ic+2+length]).decode(encoding))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + length + 2


def binoper(stack, func):
    a = stack.pop()
    b = stack.pop()
    stack.append(func(a, b))


class POPS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class ADD(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x + y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class SUB(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x - y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class MUL(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x * y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class DIV(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: x / y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1
    

class CMP(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(stack, lambda x, y: (x - y)//abs(x - y))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class SEQ(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(sstack, lambda x, y: int(x == y))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class CATS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        binoper(sstack, lambda x, y: x + y)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class MULS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        a = sstack.pop()
        b = stack.pop()

        stack.append(a * b)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class JMP(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, code[ic+1]


class JEQ(Inst):
    matches = [0]

    @classmethod
    def run(cls, stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        condition = stack.pop()
        if condition in cls.matches:
            return stack, sstack, var, svar, code, jmptable, code[ic + 1]
        else:
            return stack, sstack, var, svar, code, jmptable, ic + 1


class JNE(JEQ):
    matches = [-1, 1]


class JGT(JEQ):
    matches = [1, ]


class JLE(JEQ):
    matches = [-1, ]


class DJMP(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        addr = jmptable.get(stack.pop())
        if addr:
            return stack, sstack, var, svar, code, jmptable, stackp, sstackp, addr
        else:
            return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class ST(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        var[code[ic+1]] = stack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LD(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(var[code[ic+1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class STS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        svar[code[ic + 1]] = sstack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LDS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.append(var[code[ic + 1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class ITOS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        x = stack.pop()
        sstack.append(str(x))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class STRI(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        i = stack.pop()
        s = sstack.pop()
        sstack.append(s[i])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class STOI(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(int(sstack.pop()))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class LEN(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(len(sstack.pop()))
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class PRT(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        s = sstack.pop()
        print(s)
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class INP(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.append(input())
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 1


class PUSHLOC(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stackp.append(stack.len() - 1)


class PUSHLOCS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstackp.append(sstack.len() - 1)


class POPLOC(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stackp.pop()


class POPLOCS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstackp.pop()


class STLOC(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        var[stackp[-1] + code[ic + 1]] = stack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LDLOC(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        stack.append(var[stackp[-1] + code[ic + 1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class STLOCS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        svar[sstackp[-1] + code[ic + 1]] = sstack.pop()
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


class LDLOCS(Inst):
    @staticmethod
    def run(stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic):
        sstack.append(svar[sstackp[-1] + code[ic + 1]])
        return stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic + 2


instructions = Inst.__subclasses__()
