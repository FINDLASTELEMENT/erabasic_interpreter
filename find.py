import regex


block_start = [
    r'[ \t]*IF',
]

block_end = [
    r'[ \t]*ENDIF',
]

elses = [
    r'[ \t]*ELSE',
    r'[ \t]*ELSEIF'
]


class FindError(Exception):
    pass


def find_func(re, code, pos=0, reverse=False):
    for i in range(len(code))[pos::(-2*reverse+1)]:
        if regex.match(re, code[i]):
            return i + 1

    raise FindError('Cannot find that function')


def find(re, code, pos, reverse=False):
    """
    this function will give you the searched position + 1 (past that instruction)
    """
    block_height = 0

    for r in elses:
        if regex.match(r, code[pos]):
            block_height = 1
            break

    direction = -2*reverse + 1

    for i in range(len(code))[pos::direction]:
        if regex.match(re, code[i]) and block_height == 1:
            return i + 1

        for s in block_start:
            if regex.match(s, code[i]):
                block_height += 1
                break

        for e in block_end:
            if regex.match(e, code[i]):
                block_height -= 1
                break

    raise FindError('Cannot find matching token')
