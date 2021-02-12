import ply.yacc as yacc
from lex import tokens
from instructions import *


precedence = (
    ('left', 'QUESTION', 'SHARP'),
    ('left', 'AND', 'NAND', 'OR', 'NOR', 'XOR'),
    ('left', 'BAND', 'BOR', 'BXOR'),
    ('left', 'EQUALS', 'NEQUALS'),
    ('left', 'LESS', 'GREATER', 'LESSEQ', 'GREATEQ'),
    ('left', 'LSHIFT', 'RSHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('nonassoc', 'BNOT', 'NOT')
)


def p_repeat(p):
    'inst : REPEAT expr block REND'
    pass


def p_for(p):
    '''inst : FOR ID COMMA expr COMMA expr block NEXT
            | FOR ID COMMA expr COMMA expr COMMA expr block NEXT'''
    pass


def p_call(p):
    '''inst : CALL ID
            | CALL ID COMMA args'''
    pass


def p_while(p):
    '''inst : WHILE expr block WEND'''
    pass


def p_break(p):
    'inst : BREAK'
    pass


def p_continue(p):
    'inst : CONTINUE'
    pass


def p_print(p):
    'inst : PRINT string'
    p[0] = Print(p[2])


def p_dim(p):
    '''inst : SHARP DIM ID
            | SHARP DIMS ID
            | SHARP DIM CONST ID
            | SHARP DIMS CONST ID
            | SHARP DIM REF ID
            | SHARP DIMS REF ID
            | SHARP DIM CONST REF ID
            | SHARP DIMS CONST REF ID
            | SHARP DIM REF CONST ID
            | SHARP DIMS REF CONST ID'''
    pass


def p_subsit(p):
    '''inst : ID SUBSIT expr'''
    pass


def p_label(p):
    '''lbl : DOLLAR ID'''
    pass


def p_func(p):
    '''function : AT ID COMMA args'''
    pass


def p_crease(p):
    '''inst : INCREASE ID
            | ID INCREASE
            | DECREASE ID
            | ID DECREASE'''
    pass


def p_ID2expr(p):
    'expr : ID'
    pass


def p_char(p):
    '''STRING : CHAR CHAR
              | STRING CHAR'''
    if type(p[1]) == String:
        p[0] = String(p[1], Literal(p[2]))
    else:
        p[0] = String(Literal(p[1]), Literal(p[2]))


def p_STRFORMAT(p):
    '''STRING : STRING LBRACE expr RBRACE
              | STRING PERCENT expr PERCENT
              | STRING SLASHAT expr QUESTION expr SHARP expr SLASHAT'''
    if p[2] == r'\@':
        p[3] = Operator(ternary, (p[3], p[5], p[7]))

    p[0] = String(p[1], p[3])


def p_args(p):
    '''args : expr COMMA expr
            | args COMMA expr'''


def p_index(p):
    '''expr : expr COLON expr'''
    pass


def p_block(p):
    '''block : inst inst
             | block inst'''
    pass


def p_add(p):
    '''expr : expr PLUS expr
            | STRING PLUS STRING'''
    pass


def p_minus(p):
    'expr : expr MINUS expr'
    pass


def p_mult_div(p):
    '''expr : expr TIMES expr
            | expr DIVIDE expr
            | STRING TIMES expr'''
    if p[2] == '*':
        pass
    else:
        pass


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
    pass


def p_parens(p):
    'expr : LPAREN expr RPAREN'
    pass


def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()


if __name__ == '__main__':
    with open('test.erb', 'r') as f:
        result = parser.parse(f.read(-1))

    print(result)
