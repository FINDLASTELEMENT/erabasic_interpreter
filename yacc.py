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
    ('left', 'PERCENT'),
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
            | PRINT empty'''
    p[0] = (p.slice[1].value, p[2])


def p_assign_left(p):
    '''asleft : var BINOPER SUBSIT
              | var empty SUBSIT'''
    p[0] = (p[1], p[2], p[3])


def p_assign(p):
    '''inst : asleft expr 
            | asleft empty 
            | asleft MOD expr MOD  %prec PERCENT'''
    if len(p) == 3:
        p[0] = ('ASSIGN',) + p[1] + (p[2],)
    else:
        p[0] = ('ASSIGN',) + p[1] + (p[3],)


def p_crease_front(p):
    '''inst : INCREASE var 
            | DECREASE var '''
    p[0] = (p[1], p[2])


def p_crease_rear(p):
    '''inst : var INCREASE 
            | var DECREASE '''
    p[0] = (p[2], p[1])


def p_WHILE(p):
    '''inst : WHILE expr  insts WEND '''
    p[0] = ('WHILE', p[2], p[3])


def p_FORHEAD(p):
    '''FORHEAD : FOR ID
               | FOR array'''
    p[0] = (p[1], p[2])


def p_FOR(p):
    '''inst : FORHEAD COMMA expr COMMA expr empty empty  insts NEXT
            | FORHEAD ID COMMA expr COMMA expr COMMA expr  insts NEXT '''
    p[0] = ('FOR', p[2], p[4], p[6], p[8] if p[8] else 1, p[9])


def p_DOLOOP(p):
    'inst : DO insts LOOP expr'
    p[0] = ('DO', p[4], p[2])


def p_REPEAT(p):
    'inst : REPEAT expr insts REND'
    p[0] = ('REPEAT', p[2], p[3])


def p_IF(p):
    '''inst : IFBODY elseif_blocks ENDIF
            | IFBODY empty ENDIF'''
    p[0] = ('IF', p[1], p[2])


def p_IFBODY(p):
    '''IFBODY : IF expr insts
              | IF expr empty'''
    p[0] = (p[2], p[3])


def p_ELSEBLOCK(p):
    '''elseif_block : ELSE insts
                 | ELSE empty'''
    p[0] = p[2]


def p_elseif_blocks(p):
    '''elseif_blocks : elseif_block %prec merge
                     | elseif_blocks elseif_block %prec merge'''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = p[1] + p[2]


def p_elseif_block(p):
    '''elseif_block : ELSEIF expr insts
                    | ELSEIF expr empty'''
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


def p_SIF(p):
    'inst : SIF expr inst'
    p[0] = ('SIF', p[2], p[3])


def p_func_def(p):
    '''inst : AT ID COMMA fargs FUNCATTRIBS
            | AT ID empty empty FUNCATTRIBS
            | AT ID COMMA fargs empty
            | AT ID empty empty empty'''
    p[0] = ('FUNCDEF', p[2], p[4])


def p_INSTCALL(p):
    '''inst : ID args
            | ID empty'''
    p[0] = ('INST', p.slice[1].value, p[2])


def p_inline_call(p):
    '''expr : ID LPAREN args RPAREN
            | ID LPAREN arg RPAREN'''
    p[0] = ('CALL', p[1], p[3])


def p_LABEL(p):
    'inst : DOLLAR ID'
    p[0] = ('LABEL', p[2])


def p_STRING(p):
    '''STRING : CHAR %prec merge
              | FORMAT'''
    p[0] = (p[1],)


def p_char(p):
    '''STRING : STRING CHAR %prec merge
              | STRING FORMAT %prec merge'''
    p[0] = p[1] + (p[2],)


def p_STRFORMAT(p):
    '''FORMAT : LBRACE expr RBRACE
              | PERCENT expr PERCENT
              | SLASHAT STRTERNARY SLASHAT'''
    p[0] = (p[2],)


def p_STRTERNARY(p):
    'STRTERNARY : expr QUESTION STRING SHARP STRING'
    p[0] = ('TERNARY', p[1], p[3], p[5])


def p_arg(p):
    '''arg : expr'''
    p[0] = p[1]


def p_args(p):
    '''args : arg
            | args COMMA arg'''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = p[1] + (p[3],)


def p_farg(p):
    '''farg : ID'''
    p[0] = p[1]


def p_fargs(p):
    '''fargs : farg %prec merge
             | fargs COMMA ID %prec merge'''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = p[1] + (p[3],)


def p_function_attrib(p):
    '''FUNCATTRIB : SHARP ONLY
                  | SHARP FUNCTION
                  | SHARP FUNCTIONS
                  | SHARP PRI
                  | SHARP LATER
                  | SHARP SINGLE'''
    p[0] = p[2]


def p_function_attribs(p):
    '''FUNCATTRIBS : FUNCATTRIB
                   | FUNCATTRIBS FUNCATTRIBS'''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = p[1] + (p[2],)


def p_index(p):
    '''array : ID COLON expr
             | array COLON expr'''
    p[0] = ('INDEX', p[1], p[3])


def p_str_binop(p):
    '''STRING : STRING PLUS STRING
              | STRING TIMES expr'''
    p[0] = (p[2], p[1], p[3])


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
    '''expr : expr QUESTION expr SHARP expr'''
    p[0] = ('ITERNARY', p[1], p[3], p[5])


def p_expr(p):
    '''expr : NUMBER
             | ID
             | array
             | STRING'''
    p[0] = p[1]


def p_var(p):
    '''var : ID
           | array'''
    p[0] = p[1]


def p_binoper(p):
    '''BINOPER : PLUS
            | MINUS
            | TIMES
            | DIVIDE
            | EQUALS
            | NEQUALS
            | LESS
            | LESSEQ
            | GREATER
            | GREATEQ
            | LSHIFT
            | RSHIFT
            | AND
            | NAND
            | OR
            | NOR
            | XOR
            | BAND
            | BOR
            | BXOR
            | MOD '''
    p[0] = p[1]


def p_parens(p):
    'expr : LPAREN expr RPAREN'
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]


def p_str_parens(p):
    'expr : LPAREN STRING RPAREN'
    p[0] = p[2]


def p_quoted_emptystring(p):
    'STRING : QUOTE QUOTE'
    p[0] = None


def p_quoted(p):
    '''STRING : QUOTE STRING QUOTE'''
    p[0] = p[2]


def p_empty(p):
    'empty : '
    pass


def p_error(p):
    global errorcount
    if p or __debug__:
        print("Syntax error in input!", p, parser.token())
        exit()
    else:
        print('end of file while parsing')
        return


parser = yacc.yacc()


def parse(filename):
    with open(filename, 'r') as f:
        result = parser.parse(f.read(-1))

    return result


if __name__ == '__main__':
    pprint(parse('test2.erb'))
