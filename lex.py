from ply import lex

reserved = {
    'FOR': 'FOR',
    'NEXT': 'NEXT',
    'WHILE': 'WHILE',
    'WEND': 'WEND',
    'DO': 'LOOP',
    'IF': 'IF',
    'SIF': 'SIF',
    'ELSEIF': 'ELSEIF',
    'ELSE': 'ELSE',
    'GOTO': 'GOTO'
}

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
    'SLASHAT',  # \@
    'CHAR',
    'COLON',
    'PRINT',
    'DOLLAR',
    'LABEL',
    'ID',
    'WTSPC',
    'COMMENT',
    'AT'
)
tokens += tuple(reserved.values())

states = (
    ('string', 'exclusive'),
    ('expr', 'inclusive'),
    ('strexpr', 'inclusive'),
    ('ternary', 'inclusive'),
    ('label', 'exclusive'),
    ('print', 'exclusive')
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
t_SUBSIT = r'='
t_QUESTION = r'\?'
t_SHARP = r'\#'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_string_CHAR = r'(\\.|.)'
t_COLON = r':'
t_COMMA = r','
t_AT = r'@'
t_label_LABEL = '[A-Za-z]+'


def t_COMMENT(t):
    r';.*'
    pass


def t_PRINT(t):
    r'PRINT(|V|S|FORM|FORMS)(|K|D)(|L|W)'
    t.lexer.push_state('print')
    return t


def t_print_WTSPC(t):
    r'[ \t]+'
    t.lexer.push_state('string')


def t_string_NEWLINE(t):
    r'\n'
    t_NEWLINE(t)
    t.lexer.begin('INITIAL')


def t_DOLLAR(t):
    r'\$'
    t.lexer.push_state('label')
    return t


def t_label_NEWLINE(t):
    r'\n+'
    t_NEWLINE(t)
    t.lexer.pop_state()


def t_string_LBRACE(t):
    r'\{'
    t.lexer.push_state('expr')
    return t


def t_expr_RBRACE(t):
    r'\}'
    t.lexer.pop_state()
    return t


def t_string_MOD(t):
    r'%'
    t.lexer.push_state('strexpr')
    return t


def t_strexpr_MOD(t):
    r'%'
    t.lexer.pop_state()
    return t


def t_QUOTE(t):
    r'"'
    t.lexer.push_state('string')


def t_string_QUOTE(t):
    r'"'
    t.lexer.pop_state()


def t_ternary_SLASHAT(t):
    r'\\@'
    t.lexer.pop_state()
    return t


def t_string_SLASHAT(t):
    r'\\@'
    t.lexer.push_state('ternary')
    return t


def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_ANY_error(t):
    print("invalid token while lexing", t.value[0])
    t.lexer.skip(1)


def t_label_error(t):
    print("invalid label token", t.value[0])
    t.lexer.skip(1)


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_ID(t):
    r'[a-zA-Z_]+'
    t.type = reserved.get(t.value, 'ID')
    return t


lexer = lex.lex()

if __name__ == '__main__':
    with open('test.erb', 'r') as f:
        lexer.input(f.read(-1))

        while True:
            tok = lexer.token()
            if not tok:
                break
            print(tok)

