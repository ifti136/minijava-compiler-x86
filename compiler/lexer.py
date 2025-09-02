# compiler/lexer.py
import ply.lex as lex

# Reserved keywords
reserved = {
    'class': 'CLASS',
    'public': 'PUBLIC',
    'static': 'STATIC',
    'void': 'VOID',
    'main': 'MAIN',
    'String': 'STRING',
    'int': 'INT',
    'boolean': 'BOOLEAN',
    'if': 'IF',
    'else': 'ELSE',
    'while': 'WHILE',
    'return': 'RETURN',
    'System': 'SYSTEM',
    'out': 'OUT',
    'println': 'PRINTLN',
    'true': 'TRUE',
    'false': 'FALSE',
}

# All tokens
tokens = [
    'ID', 'NUMBER',
    'LBRACE', 'RBRACE',
    'LPAREN', 'RPAREN',
    'LBRACK', 'RBRACK',
    'SEMICOLON',
    'ASSIGN',
    'DOT',
    'PLUS', 'MINUS', 'TIMES',
    'LT', 'NOT',
] + list(reserved.values())

# Regex rules
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACK    = r'\['
t_RBRACK    = r'\]'
t_SEMICOLON = r';'
t_ASSIGN    = r'='
t_DOT       = r'\.'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_LT        = r'<'
t_NOT       = r'!'

# Identifiers and keywords
def t_ID(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Numbers
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Comments
def t_COMMENT(t):
    r'//.*'
    pass

# Newlines
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore whitespace
t_ignore = ' \t\r'

# Errors
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(**kwargs)

if __name__ == "__main__":
    lexer = build_lexer()
    data = '''
    class Test {
      public static void main(String[] args) {
        int a;
        a = 5;
        System.out.println(a);
      }
    }
    '''
    lexer.input(data)
    for tok in lexer:
        print(tok)
