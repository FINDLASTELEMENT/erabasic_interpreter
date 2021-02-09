from ply import lex
import ply.yacc as yacc

# this is almost copy of https://riptutorial.com/python/example/31583/the--hello--world---of-ply---a-simple-calculator

tokens = (
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'EQUALS',
    'NEQUALS',
    'LESSEQ',
    'GREATEQ',
    'LSHIFT',
    'RSHIFT',
    'NAND',
    'NOR',
    'NOT',
    'BNOT',
    'MOD',
    'LESS',
    'GREATER',
    'AND',
    'OR',
    'BAND',
    'BOR',
    'XOR',
    'BXOR',
    'STRING',
    'QUESTION',
    'SHARP',
    'RPAREN',
    'LPAREN',
    'NUMBER',
)

t_ignore = ' \t'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'=='
t_NEQUALS = r'!='
t_LESSEQ = r'<='
t_GREATEQ = r'>='
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_NAND = r'!&'
t_NOR = r'!\|'
t_NOT = r'!'
t_BNOT = r'~'
t_MOD = r'%'
t_LESS = r'<'
t_GREATER = r'>'
t_AND = r'&&'
t_OR = r'\|\|'
t_BAND = r'&'
t_BOR = r'\|'
t_XOR = '\^\^'
t_BXOR = '\^'
t_STRING = r'"[^"]*"'
t_QUESTION = r'\?'
t_SHARP = r'\#'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_error(t):
    print("invalid token", t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

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


def p_add(p):
    '''expr : expr PLUS expr
            | STRING PLUS STRING'''
    p[0] = p[1] + p[3]


def p_minus(p):
    'expr : expr MINUS expr'
    p[0] = p[1] - p[3]


def p_mult_div(p):
    '''expr : expr TIMES expr
            | expr DIVIDE expr
            | STRING TIMES expr'''
    if p[2] == '*':
        p[0] = p[1] * p[3]
    else:
        if p[3] == 0:
            print("Can't divide by 0")
            raise ZeroDivisionError('integer division by 0')
        p[0] = p[1] / p[3]


def p_equals(p):
    'expr : expr EQUALS expr'
    p[0] = int(p[1] == p[3])


def p_nequals(p):
    'expr : expr NEQUALS expr'
    p[0] = int(p[1] != p[3])


def p_cmp(p):
    '''expr : expr LESS expr
            | expr LESSEQ expr
            | expr GREATER expr
            | expr GREATEQ expr'''
    if p[2] == '<':
        p[0] = p[1] < p[3]
    elif p[2] == '<=':
        p[0] = p[1] <= p[3]
    elif p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '>=':
        p[0] = p[1] >= p[3]

    p[0] = int(p[0])


def p_shift(p):
    '''expr : expr LSHIFT expr
            | expr RSHIFT expr'''
    if p[2] == '<<':
        p[0] = p[1] << p[3]
    else:
        p[0] = p[1] >> p[3]


def p_and(p):
    '''expr : expr AND expr
            | expr NAND expr'''
    if p[2] == '&&':
        p[0] = p[1] and p[3]
    else:
        p[0] = not (p[1] and p[3])
    p[0] = int(p[0])


def p_or(p):
    '''expr : expr OR expr
            | expr NOR expr'''
    if p[2] == '||':
        p[0] = p[1] or p[3]
    else:
        p[0] = not (p[1] or p[3])
    p[0] = int(p[0])


def p_xor(p):
    'expr : expr XOR expr'
    p[0] = int(bool(p[1]) ^ bool(p[3]))


def p_bitwise(p):
    '''expr : expr BAND expr
            | expr BOR expr
            | expr BXOR expr'''
    if p[2] == '&':
        p[0] = p[1] & p[2]
    elif p[2] == '|':
        p[0] = p[1] | p[2]
    else:
        p[0] = p[1] ^ p[2]


def p_not(p):
    '''expr : NOT expr
            | BNOT expr'''
    if p[1] == '!':
        p[0] = int(not p[2])
    else:
        p[0] = ~p[2]


def p_mod(p):
    'expr : expr MOD expr'
    if p[2] == 0:
        print("Can't divide by 0")
        raise ZeroDivisionError('integer division by 0')
    p[0] = p[1] % p[2]


def p_ternary(p):
    '''expr : expr QUESTION expr SHARP expr
            | expr QUESTION STRING SHARP STRING
            | expr QUESTION expr SHARP STRING
            | expr QUESTION STRING SHARP expr'''
    if p[1]:
        p[0] = p[3]
    else:
        p[0] = p[5]


def p_expr2NUM(p):
    'expr : NUMBER'
    p[0] = p[1]


def p_parens(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]


def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()


def eval_exp(string):
    return parser.parse(string)


if __name__ == '__main__':
    parser = yacc.yacc()

    res = parser.parse("4*3 - 5 + 0? 15 # 5")
    print(res)
