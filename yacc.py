import ply.yacc as yacc
from lex import tokens
from lex import reserved
from instructions import *
from pprint import pprint


precedence = (
    ('left', 'merge'),
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
    ('nonassoc', 'UMINUS'),
    ('left', 'ID'),
    ('left', 'COLON')
)


def p_insts(p):
    '''insts : inst %prec merge
             | insts inst %prec merge'''
    if len(p) == 2:
        p[0] = ('INSTS', p[1])
    else:
        p[0] = p[1] + (p[2],)


def p_PRINT(p):
    '''inst : PRINT STRING
            | PRINT expr
            | PRINT empty'''
    p[0] = ('PRINT', p[2])


def p_CALL(p):
    'inst : CALL ID COMMA args'
    p[0] = ('CALL', p[2], p[4])


def p_assign(p):
    'inst : ID SUBSIT expr'
    p[0] = ('ASSIGN', p[0], p[3])


def p_WHILE(p):
    '''inst : WHILE expr insts WEND'''
    p[0] = ('WHILE', p[2], p[3])


def p_FOR(p):
    '''inst : FOR ID COMMA expr COMMA expr empty empty insts NEXT
            | FOR ID COMMA expr COMMA expr COMMA expr insts NEXT'''
    p[0] = ('FOR', p[2], p[4], p[6], p[8] if p[8] else 1, p[9])


def p_DOLOOP(p):
    'inst : DO insts LOOP expr'
    p[0] = ('DO', p[4], p[2])


def p_IF(p):
    '''inst : IF expr insts elseif_blocks ELSE insts ENDIF
            | IF expr insts empty ELSE insts ENDIF
            | IF expr insts elseif_blocks empty empty ENDIF
            | IF expr insts empty empty empty ENDIF'''
    p[0] = ('IF', p[2], p[3], p[4], p[6])


def p_elseif_blocks(p):
    '''elseif_blocks : elseif_block %prec merge
                     | elseif_blocks elseif_block %prec merge'''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = p[1] + p[2]


def p_elseif_block(p):
    'elseif_block : ELSEIF expr insts'
    p[0] = ('ELSEIF', p[2], p[3])


def p_SELECTCASE(p):
    '''inst : SELECTCASE expr case_blocks CASEELSE insts ENDSELECT
            | SELECTCASE expr case_blocks empty empty ENDSELECT'''
    p[0] = ('SELECTCASE', p[2], p[3], p[5])


def p_case_blocks(p):
    '''case_blocks : case_block %prec merge
                   | case_blocks case_block %prec merge'''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = p[1] + p[2]


def p_case_block(p):
    'case_block : CASE expr insts'
    p[0] = ('CASE', p[2], p[3])


def p_STRING(p):
    'STRING : CHAR'
    p[0] = p[1]


def p_char(p):
    '''STRING : STRING CHAR'''
    if type(p[1]) == str:
        p[0] = p[1] + p[2]
    elif type(p[1][-1]) == str:
        p[0] = p[1][:-1] + ((p[1][-1] + p[2]),)  # if possible, connect strings to improve readability
    else:
        p[0] = ('STRCAT', p[1], p[2])


def p_STRFORMAT(p):
    '''STRING : STRING LBRACE expr RBRACE
              | STRING MOD expr MOD
              | STRING SLASHAT expr QUESTION expr SHARP expr SLASHAT'''
    if p[2] == r'\@':
        p[3] = ('TERNARY', p[3], p[5], p[7])

    p[0] = ('STRCAT', p[1], p[3])


def p_args(p):
    '''args : expr COMMA expr'''
    p[0] = ('ARGS', p[1], p[3])


def p_extend_args(p):
    'args : args COMMA expr'
    p[0] = p[1] + (p[3],)


def p_index(p):
    '''expr : expr COLON expr'''
    p[0] = ('INDEX', p[1], p[3])


def p_int_binop(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr EQUALS expr
            | expr NEQUALS expr
            | expr LESS expr
            | expr LESSEQ expr
            | expr GREATER expr
            | expr GREATEQ expr
            | expr LSHIFT expr
            | expr RSHIFT expr
            | expr AND expr
            | expr NAND expr
            | expr OR expr
            | expr NOR expr
            | expr XOR expr
            | expr BAND expr
            | expr BOR expr
            | expr BXOR expr
            | expr MOD expr'''

    p[0] = (p[2], p[1], p[3])


def p_not(p):
    '''expr : NOT expr
            | BNOT expr'''
    p[0] = (p[1], p[2])


def p_uminus(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = ('UMINUS', p[2])


def p_ternary(p):
    '''expr : expr QUESTION expr SHARP expr
            | expr QUESTION STRING SHARP STRING
            | expr QUESTION expr SHARP STRING
            | expr QUESTION STRING SHARP expr'''
    p[0] = ('TERNARY', p[1], p[3], p[5])


def p_expr2NUM(p):
    'expr : NUMBER'
    p[0] = p[1]


def p_expr2ID(p):
    'expr : ID'
    p[0] = ('ID', p[1])


def p_parens(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]


def p_empty(p):
    'empty : '
    pass


def p_error(p):
    if p:
        print("Syntax error in input!", p)
    else:
        print('end of file')
        return


parser = yacc.yacc()


def parse(filename):
    with open(filename, 'r') as f:
        result = parser.parse(f.read(-1))

    return result


if __name__ == '__main__':
    pprint(parse('test.erb'))
