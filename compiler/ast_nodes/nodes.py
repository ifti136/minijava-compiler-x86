from dataclasses import dataclass
from typing import List, Any

# FIX: Removed the duplicate ASTNode definition. This is the single source of truth.
class ASTNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children is not None else []

    def __repr__(self):
        return self.name

# NOTE: Removed @dataclass from nodes with custom __init__ to avoid redundancy.
# The custom __init__ is kept to build the 'children' list for visualization.

class ProgramNode(ASTNode):
    def __init__(self, main, classes):
        super().__init__('Program', [main] + classes)
        self.main = main
        self.classes = classes

class MainClassNode(ASTNode):
    def __init__(self, name, argname, body):
        super().__init__(f'MainClass:{name}', body)
        self.name = name
        self.argname = argname
        
        self.var_decls = [item for item in body if isinstance(item, VarDeclNode)]
        self.statements = [item for item in body if not isinstance(item, VarDeclNode)]

class ClassDeclNode(ASTNode):
    def __init__(self, name, var_decls, method_decls):
        children = (var_decls or []) + (method_decls or [])
        super().__init__(f'Class:{name}', children)
        self.name = name
        self.var_decls = var_decls or []
        self.method_decls = method_decls or []

class VarDeclNode(ASTNode):
    def __init__(self, type_, name):
        super().__init__(f'Var:{name}', [type_])
        self.type = type_
        self.name = name

class MethodDeclNode(ASTNode):
    # FIX: Updated constructor to take a single 'body' list.
    def __init__(self, name, rtype, params, body, return_expr):
        children = [rtype]
        children.extend(params or [])
        children.extend(body or [])
        if return_expr:
            children.append(return_expr)
            
        super().__init__(f'Method:{name}', children)
        self.name = name
        self.rtype = rtype
        self.params = params or []
        self.return_expr = return_expr
        
        # FIX: The node separates the body internally.
        self.var_decls = [item for item in body if isinstance(item, VarDeclNode)]
        self.statements = [item for item in body if not isinstance(item, VarDeclNode)]
        
# Types
class IntType(ASTNode):
    def __init__(self):
        super().__init__('int', [])

class BooleanType(ASTNode):
    def __init__(self):
        super().__init__('boolean', [])

class ArrayType(ASTNode):
    def __init__(self, base='int'):
        super().__init__(f'{base}[]', [])
        self.base = base

class ClassType(ASTNode):
    def __init__(self, name):
        super().__init__(f'class:{name}', [])
        self.name = name

# Statements
class BlockNode(ASTNode):
    def __init__(self, statements):
        super().__init__('Block', statements or [])
        self.statements = statements or []

class IfNode(ASTNode):
    def __init__(self, cond, then_stmt, else_stmt):
        super().__init__('If', [cond, then_stmt, else_stmt])
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

class WhileNode(ASTNode):
    def __init__(self, cond, body):
        super().__init__('While', [cond, body])
        self.cond = cond
        self.body = body

class PrintNode(ASTNode):
    def __init__(self, expr):
        super().__init__('Print', [expr])
        self.expr = expr

class AssignNode(ASTNode):
    def __init__(self, name, expr):
        super().__init__(f'Assign:{name}', [expr])
        self.name = name
        self.expr = expr

class ArrayAssignNode(ASTNode):
    def __init__(self, name, index, expr):
        super().__init__(f'ArrayAssign:{name}', [index, expr])
        self.name = name
        self.index = index
        self.expr = expr

# Expressions
class BinaryOpNode(ASTNode):
    def __init__(self, op, left, right):
        super().__init__(f'BinOp:{op}', [left, right])
        self.op = op
        self.left = left
        self.right = right

class UnaryOpNode(ASTNode):
    def __init__(self, op, expr):
        super().__init__(f'UnOp:{op}', [expr])
        self.op = op
        self.expr = expr

class IntLiteralNode(ASTNode):
    def __init__(self, value):
        super().__init__(f'Int:{value}', [])
        self.value = value

class BoolLiteralNode(ASTNode):
    def __init__(self, value):
        super().__init__(f'Bool:{value}', [])
        self.value = value

class VarNode(ASTNode):
    def __init__(self, name):
        super().__init__(f'Var:{name}', [])
        self.name = name

class ArrayAccessNode(ASTNode):
    def __init__(self, name, index):
        super().__init__(f'ArrayAccess:{name}', [index])
        self.name = name
        self.index = index

class ArrayLengthNode(ASTNode):
    def __init__(self, name):
        super().__init__(f'Len:{name}', [])
        self.name = name

class MethodCallNode(ASTNode):
    def __init__(self, obj, method, args):
        super().__init__(f'MCall:{obj}.{method}', args or [])
        self.obj = obj
        self.method = method
        self.args = args or []