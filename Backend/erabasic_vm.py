from instructions import *
import pickle
import sys
import make_testcode
from random_access_list import *


if __name__ == "__main__":
    filename = 'testcode'
    with open(f'{filename}.era', 'rb') as f:
        code = list(f.read(-1))
    with open(f'{filename}.addr', 'rb') as f:
        jmptable = pickle.load(f)

    ic = 0
    stack = []
    sstack = []
    var = RandomList()
    svar = RandomList()
    stackp = []
    sstackp = []

    while ic is not None:
        stack, sstack, var, svar, code, jmptable, stackp, sstackp, ic = \
            instructions[code[ic]].run(stack, sstack, var, svar, code, jmptable, [], [], ic)

    print(stack, sstack)
