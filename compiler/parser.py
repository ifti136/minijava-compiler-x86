# compiler/parser.py
import ply.yacc as yacc
import sys
from compiler.lexer import tokens
from compiler.ast_nodes.nodes import (
    ProgramNode, MainClassNode, ClassDeclNode, VarDeclNode, BlockNode,
    AssignNode, PrintNode, IfNode, WhileNode,
    IntLiteralNode, BoolLiteralNode, VarNode, BinaryOpNode, UnaryOpNode,
    IntType, BooleanType
)

# -----------------------
# Grammar
# -----------------------

def p_program(p):
    '''program : main_class class_decl_list'''
    p[0] = ProgramNode(p[1], p[2])

def p_class_decl_list(p):
    '''class_decl_list : class_decl_list class_decl
                       | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_class_decl(p):
    '''class_decl : CLASS ID LBRACE RBRACE'''
    # Minimal class support (no fields/methods yet)
    p[0] = ClassDeclNode(p[2], [], [])

def p_main_class(p):
    '''main_class : PUBLIC CLASS ID LBRACE PUBLIC STATIC VOID MAIN LPAREN STRING LBRACK RBRACK ID RPAREN LBRACE decl_or_statement_list RBRACE RBRACE'''
    # Build MainClassNode with a single body list that contains decls + statements
    class_name = p[3]
    arg_name = p[13]
    body = p[16]  # list of VarDeclNode and statements
    p[0] = MainClassNode(class_name, arg_name, body)

def p_decl_or_statement_list(p):
    '''decl_or_statement_list : decl_or_statement_list decl_or_statement
                              | decl_or_statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_decl_or_statement(p):
    '''decl_or_statement : var_decl
                         | statement'''
    p[0] = p[1]

def p_var_decl(p):
    '''var_decl : INT ID SEMICOLON
                | BOOLEAN ID SEMICOLON'''
    if p[1] == 'int':
        vtype = IntType()
    else:
        vtype = BooleanType()
    p[0] = VarDeclNode(vtype, p[2])

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement_block(p):
    '''statement : LBRACE statement_list RBRACE'''
    p[0] = BlockNode(p[2])

def p_statement_assign(p):
    '''statement : ID ASSIGN expression SEMICOLON'''
    p[0] = AssignNode(p[1], p[3])

def p_statement_print(p):
    '''statement : SYSTEM DOT OUT DOT PRINTLN LPAREN expression RPAREN SEMICOLON'''
    p[0] = PrintNode(p[7])

def p_statement_if(p):
    '''statement : IF LPAREN expression RPAREN statement ELSE statement'''
    p[0] = IfNode(p[3], p[5], p[7])

def p_statement_while(p):
    '''statement : WHILE LPAREN expression RPAREN statement'''
    p[0] = WhileNode(p[3], p[5])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression LT expression'''
    p[0] = BinaryOpNode(p[2], p[1], p[3])

def p_expression_unary(p):
    '''expression : NOT expression'''
    p[0] = UnaryOpNode(p[1], p[2])

def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]

def p_expression_int(p):
    '''expression : NUMBER'''
    p[0] = IntLiteralNode(p[1])

def p_expression_bool(p):
    '''expression : TRUE
                  | FALSE'''
    # The token values are 'true'/'false' as strings from the lexer
    p[0] = BoolLiteralNode(p[1] == 'true')

def p_expression_var(p):
    '''expression : ID'''
    p[0] = VarNode(p[1])

def p_empty(p):
    'empty :'
    p[0] = []

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

def build_parser():
    # Build with this module's grammar; lexer is built by caller.
    parser = yacc.yacc(module=sys.modules[__name__], start='program')
    # Return a fresh lexer too to keep the main driver’s routine intact
    from compiler.lexer import build_lexer
    return parser, build_lexer()

if __name__ == "__main__":
    from compiler.lexer import build_lexer
    data = '''
    public class Test3_Arith {
        public static void main(String[] args) {
            int a; int b; int c;
            a = 2; b = 3;
            c = a * a + b * b;
            System.out.println(c);
        }
    }
    '''
    parser, lexer = build_parser()
    ast = parser.parse(data, lexer=lexer)
    print(ast)
