from instructions import *
import pickle


def flatten(x):
    result = []
    for i in x:
        if hasattr(i, "__iter__"):
            result += flatten(i)
        else:
            result.append(i)

    return result


testcode = flatten([
    INP,
    LEN,
    ITOS,
    PRT,
    JMP, 0,
    HALT
])


testcode = bytearray([toint(i) for i in testcode])
with open("testcode.era", 'wb') as f:
    f.write(testcode)

with open("testcode.addr", 'wb') as af:
    pickle.dump({}, af)
