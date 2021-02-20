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

fstr_start = (
    'GOTOFORM',
    'TRYGOTOFORM'
)

arged_fstr_start = (
    'JUMPFORM',
    'TRYJUMPFORM',
    'CALLFORM',
    'TRYCALLFORM'
)

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
    'ASSIGN',
    'QUOTE',
    'QUESTION',
    'SHARP',
    'RPAREN',
    'LPAREN',
    'NUMBER',
    'NEWLINE',
    'DIMEND',
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
    ('SKIP', 'exclusive'),
    ('argedfstr', 'exclusive'),
    ('dim', 'inclusive')
)

t_ignore = ' \t\ufeff'

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
t_argedfstr_CHAR = r'[^ ]'
t_strternary_CHAR = r'(\\[^\#]|[^\#])'
t_COLON = r':'
t_COMMA = r','
t_AT = r'@'


def t_argedfstr_WHITESPACE(t):
    r'[ ]'
    t.lexer.pop_state()


def t_strvarasign_SUBSIT(t):
    r'='
    t.lexer.push_state('string')
    return t


def t_dim_SUBSIT(t):
    r'='
    t.type = 'ASSIGN'
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
    t.lexer.lineno += len(t.value)
    pass


def t_dim_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'DIMEND'
    return t


def t_ANY_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.begin('INITIAL')


def t_DOLLAR(t):
    r'\$'
    return t


def t_string_fstring_argedfstr_strternary_LBRACE(t):
    r'\{'
    t.lexer.push_state('expr')
    return t


def t_expr_RBRACE(t):
    r'\}'
    t.lexer.pop_state()
    return t


def t_string_fstring_argedfstr_strternary_PERCENT(t):
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
    return t


def t_string_QUOTE(t):
    r'"'
    t.lexer.pop_state()
    return t


def t_strternary_SLASHAT(t):
    r'\\@'
    t.lexer.pop_state()
    return t


def t_string_fstring_argedfstr_SLASHAT(t):
    r'\\@'
    t.lexer.push_state('strternary')
    t.lexer.push_state('INITIAL')
    return t


def t_QUESTION(t):
    r'\?'
    t.lexer.pop_state()
    return t


def t_NUMBER(t):
    r'((0b|0x)[0-9]+|[0-9]+(e|p)[0-9]+)'  # 0x0000, 0b0000, 00e0000, 00p0000
    if 'x' in t.value:
        t.value = int(t.value, 16)
    elif 'b' in t.value:
        t.value = int(t.value, 2)

    elif 'e' in t.value or 'p' in t.value:
        if 'e' in t.value:
            base = 10
            a, b = t.value.split('e')
        else:
            base = 2
            a, b = t.value.split('p')

        t.value = int(a) * base ** int(b)

    else:
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
            parts = t.lexer.lexdata[t.lexer.lexpos:].split("\n")[0].split(' ')

            for p in parts:
                if p not in ('DYNAMIC', 'REF', 'CONST') and p:  # find variable name
                    var_type_table[p] = STRING  # and register that to the dictionary
                    break

        if t.value in ('DIM', 'DIMS'):
            t.lexer.push_state('dim')

    elif t.value in var_type_table.keys() and var_type_table[t.value] == STRING:
        if re.match(r'^[^!<>=]*=[^!<>=]*$', t.lexer.lexdata[t.lexer.lexpos:].split("\n")[0]) and \
                '#' not in t.lexer.lexdata[:t.lexer.lexpos].split('\n')[-1]:  # this code will
            # lookahead the code until it finds \n, and checks whether it is an assignment
            # to decide the type of following expression without other traits.
            # (and also exclude line starting with #)
            t.lexer.push_state('strvarasign')

    elif t.value in fstr_start:
        t.lexer.push_state('fstring')

    elif t.value in arged_fstr_start:
        t.lexer.push_state('argedfstr')
        t.lexer.push_state('argedfstr')  # this will make the lexer ignore whitespace once,
        # and if it meets next space, then it exits state.

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

