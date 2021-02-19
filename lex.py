from ply import lex
import regex as re

reserved = {
    'FOR': 'FOR',
    'NEXT': 'NEXT',
    'WHILE': 'WHILE',
    'WEND': 'WEND',
    'DO': 'DO',
    'LOOP': 'LOOP',
    'REPEAT': 'REPEAT',
    'REND': 'REND',
    'IF': 'IF',
    'SIF': 'SIF',
    'ELSEIF': 'ELSEIF',
    'ELSE': 'ELSE',
    'ENDIF': 'ENDIF',
    'SELECTCASE': 'SELECTCASE',
    'CASE': 'CASE',
    'CASEELSE': 'CASEELSE',
    'ENDSELECT': 'ENDSELECT',
    'FUNCTION': 'FUNCTION',
    'FUNCTIONS': 'FUNCTIONS',
    'LOCALSIZE': 'LOCALSIZE',
    'LOCALSSIZE': 'LOCALSSIZE',
    'DIM': 'DIM',
    'DIMS': 'DIMS',
    'DYNAMIC': 'DYNAMIC',
    'CONST': 'CONST',
    'REF': 'REF',
    'ONLY': 'ONLY',
    'PRI': 'PRI',
    'LATER': 'LATER',
    'SINGLE': 'SINGLE',
}

tokens = (
    'INCREASE',
    'DECREASE',
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
    'SUBSIT',
    'QUOTE',
    'QUESTION',
    'SHARP',
    'RPAREN',
    'LPAREN',
    'NUMBER',
    'NEWLINE',
    'COMMA',
    'LBRACE',  # 중괄호
    'RBRACE',
    'PERCENT',
    'SLASHAT',  # \@
    'CHAR',
    'COLON',
    'PRINT',
    'DOLLAR',
    'SKIPSTART',
    'SKIPEND',
    'ID',
    'WTSPC',
    'COMMENT',
    'AT',
    'WHITESPACE'
)
tokens += tuple(reserved.values())

states = (
    ('string', 'exclusive'),
    ('fstring', 'exclusive'),
    ('lstring', 'exclusive'),
    ('expr', 'inclusive'),
    ('strexpr', 'inclusive'),
    ('ternary', 'inclusive'),
    ('strternary', 'exclusive'),
    ('strvarasign', 'inclusive'),
    ('dims', 'inclusive'),
    ('SKIP', 'exclusive')
)

t_ignore = '( |\t|\ufeff)'

t_INCREASE = r'\+\+'
t_DECREASE = r'--'
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
t_INITIAL_MOD = r'%'
t_LESS = r'<'
t_GREATER = r'>'
t_AND = r'&&'
t_OR = r'\|\|'
t_BAND = r'&'
t_BOR = r'\|'
t_XOR = '\^\^'
t_BXOR = '\^'
t_SUBSIT = r'='
t_SHARP = r'\#'
t_strternary_SHARP = r'\#'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_string_lstring_fstring_CHAR = r'(\\.|.)'
t_strternary_CHAR = r'(\\[^\#]|[^\#])'
t_COLON = r':'
t_COMMA = r','
t_AT = r'@'


def t_strvarasign_SUBSIT(t):
    r'='
    t.lexer.push_state('string')
    return t


def t_COMMENT(t):
    r';.*'
    pass

def t_lstring_COMMENT(t):
    r';.*'
    pass


def opt_parse(string, option_regexes):
    result = []
    for o in option_regexes:
        r = re.findall(o, string)
        if r:
            result.append(r[0])

    return result


def t_PRINT(t):
    r'PRINT[^\s]*[ \t]*'

    splitted = re.split(r'[ \t]+', t.value, maxsplit=1)
    inst = splitted[0]
    string = ''
    if len(splitted) != 1:
        string = splitted[1]

    option = inst[5:]

    opts = opt_parse(option, (
        r'(V|S|FORMS|FORM)',
        r'(K|D)',
        r'(L|W)'
    ))

    if 'FORM' in opts:  # todo
        t.lexer.push_state('fstring')
    elif 'FORMS' not in opts:
        t.lexer.push_state('lstring')
    else:
        t.lexer.push_state('INITIAL')
    # FORMS is for displaying string variable.

    return t


def t_SKIP_NEWLINE(t):
    r'\n+'
    pass


def t_ANY_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.begin('INITIAL')


def t_DOLLAR(t):
    r'\$'
    return t


def t_string_fstring_strternary_LBRACE(t):
    r'\{'
    t.lexer.push_state('expr')
    return t


def t_expr_RBRACE(t):
    r'\}'
    t.lexer.pop_state()
    return t


def t_string_fstring_strternary_PERCENT(t):
    r'%'
    t.lexer.push_state('strexpr')
    return t


def t_strexpr_PERCENT(t):
    r'%'
    t.lexer.pop_state()
    return t


def t_QUOTE(t):
    r'"'
    t.lexer.push_state('string')


def t_string_QUOTE(t):
    r'"'
    t.lexer.pop_state()


def t_strternary_SLASHAT(t):
    r'\\@'
    t.lexer.pop_state()
    return t


def t_string_fstring_SLASHAT(t):
    r'\\@'
    t.lexer.push_state('strternary')
    t.lexer.push_state('INITIAL')
    return t


def t_QUESTION(t):
    r'\?'
    t.lexer.pop_state()
    return t


def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_SKIPSTART(t):
    r'\[SKIPSTART\]'
    t.lexer.push_state('SKIP')


def t_SKIP_SKIPEND(t):
    r'\[SKIPEND\]'
    t.lexer.pop_state()


def t_SKIP_throw(t):
    r'.'
    pass


def t_ANY_error(t):
    if t.value[0]:
        print("invalid token while lexing", t.value[0], 'at', t.lineno)
    else:
        print('end of file')
    t.lexer.skip(1)


def t_ID(t):
    r'[\w]+'
    global var_type_table
    if t.value in reserved.keys():
        t.type = reserved[t.value]
        if t.value == 'DIMS':
            t.lexer.push_state('dims')
    elif t.value in var_type_table.keys() and var_type_table[t.value] == STRING:
        if re.match(r'^[^!<>=]*=[^!<>=]*$', t.lexer.lexdata[t.lexer.lexpos:].split("\n")[0]):  # this code will
            # lookahead the code until it finds \n, and checks whether it is an assignment
            # to decide the type of following expression without other traits.
            t.lexer.push_state('strvarasign')
    return t


lexer = lex.lex(reflags=re.UNICODE)


STRING = str
INT = int
var_type_table = {'MASTERNAME': STRING, 'CSTR': STRING}


if __name__ == '__main__':
    with open('test.erb', 'r') as f:
        lexer.input(f.read(-1))

        while True:
            tok = lexer.token()
            if not tok:
                break
            print(tok)

