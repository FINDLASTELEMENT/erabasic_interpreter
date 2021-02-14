import ply.yacc as yacc
from lex import tokens
from lex import reserved
from instructions import *


precedence = (
    ('left', 'NEWLINE'),
    ('left', 'FOR'),
    ('nonassoc', 'PRINT', 'GOTO', 'BREAK', 'CONTINUE', 'CALL'),
    ('left', 'CHAR'),
    ('left', 'COMMA'),
    ('left', 'QUESTION', 'SHARP'),
    ('left', 'AND', 'NAND', 'OR', 'NOR', 'XOR'),
    ('left', 'BAND', 'BOR', 'BXOR'),
    ('left', 'EQUALS', 'NEQUALS'),
    ('left', 'LESS', 'GREATER', 'LESSEQ', 'GREATEQ'),
    ('left', 'LSHIFT', 'RSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('nonassoc', 'BNOT', 'NOT'),
    ('left', 'ID'),
    ('left', 'COLON')
)


def p_PRINT(p):
    'inst : PRINT STRING'
    p[0] = ('PRINT', p[2])


def p_REPEAT(p):
    'inst : REPEAT expr NEWLINE inst REND'
    p[0] = ('REPEAT', p[2], p[4])


def p_block(p):
    '''inst : inst NEWLINE inst'''
    if type(p[1][0]) == tuple:
        p[0] = p[1] + (p[3],)
    else:
        p[0] = (p[1], p[3])


def p_end(p):
    '''inst : inst NEWLINE'''
    p[0] = p[1]


def p_STRING(p):
    'STRING : CHAR'
    p[0] = p[1]


def p_char(p):
    '''STRING : STRING CHAR'''
    p[0] = p[1] + p[2]


def p_STRFORMAT(p):
    '''STRING : STRING LBRACE expr RBRACE
              | STRING MOD expr MOD
              | STRING SLASHAT expr QUESTION expr SHARP expr SLASHAT'''
    if p[2] == r'\@':
        p[3] = Operator(ternary, (p[3], p[5], p[7]))

    p[0] = String(p[1], p[3])


def p_args(p):
    '''args : expr COMMA expr
            | args COMMA expr'''
    p[0] = ('ARGS', p[1], p[3])


def p_index(p):
    '''expr : expr COLON expr'''
    p[0] = ('INDEX', p[1], p[3])


def p_add(p):
    '''expr : expr PLUS expr
            | STRING PLUS STRING'''
    p[0] = ('ADD', p[1], p[3])


def p_minus(p):
    'expr : expr MINUS expr'
    p[0] = ('MINUS', p[1], p[3])


def p_mult_div(p):
    '''expr : expr TIMES expr
            | expr DIVIDE expr
            | STRING TIMES expr'''
    p[0] = (p[2], p[1], p[3])


def p_equals(p):
    'expr : expr EQUALS expr'
    pass


def p_nequals(p):
    'expr : expr NEQUALS expr'
    pass


def p_cmp(p):
    '''expr : expr LESS expr
            | expr LESSEQ expr
            | expr GREATER expr
            | expr GREATEQ expr'''
    if p[2] == '<':
        pass
    elif p[2] == '<=':
        pass
    elif p[2] == '>':
        pass
    elif p[2] == '>=':
        pass

    pass


def p_shift(p):
    '''expr : expr LSHIFT expr
            | expr RSHIFT expr'''
    if p[2] == '<<':
        pass
    else:
        pass


def p_and(p):
    '''expr : expr AND expr
            | expr NAND expr'''
    if p[2] == '&&':
        pass
    else:
        pass
    pass


def p_or(p):
    '''expr : expr OR expr
            | expr NOR expr'''
    if p[2] == '||':
        pass
    else:
        pass
    pass


def p_xor(p):
    'expr : expr XOR expr'
    pass


def p_bitwise(p):
    '''expr : expr BAND expr
            | expr BOR expr
            | expr BXOR expr'''
    if p[2] == '&':
        pass
    elif p[2] == '|':
        pass
    else:
        pass


def p_not(p):
    '''expr : NOT expr
            | BNOT expr'''
    if p[1] == '!':
        pass
    else:
        pass


def p_mod(p):
    'expr : expr MOD expr'
    pass


def p_ternary(p):
    '''expr : expr QUESTION expr SHARP expr
            | expr QUESTION STRING SHARP STRING
            | expr QUESTION expr SHARP STRING
            | expr QUESTION STRING SHARP expr'''
    pass


def p_expr2NUM(p):
    'expr : NUMBER'
    p[0] = p[1]


def p_expr2ID(p):
    'expr : ID'
    p[0] = ('ID', p[1])


def p_parens(p):
    'expr : LPAREN expr RPAREN'
    pass


def p_error(p):
    print("Syntax error in input!", p)


parser = yacc.yacc()


if __name__ == '__main__':
    with open('test.erb', 'r') as f:
        result = parser.parse(f.read(-1))

    print(result)
