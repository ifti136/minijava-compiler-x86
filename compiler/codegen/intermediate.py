# compiler/codegen/intermediate.py
from ..ast_nodes.visitor import Visitor
from ..ast_nodes.nodes import *

class IRBuilder:
    def __init__(self):
        self.instructions = []
        self._temp_count = 0
        self._label_count = 0
    def add(self, op, a=None, b=None, r=None):
        self.instructions.append((op, a, b, r))
    def new_temp(self):
        self._temp_count += 1
        return f"t{self._temp_count}"
    def new_label(self, prefix='L'):
        self._label_count += 1
        return f"{prefix}{self._label_count}"
    def get_ir(self):
        return self.instructions

class IRGenerator(Visitor):
    def __init__(self):
        self.builder = IRBuilder()

    def visit_ProgramNode(self, node: ProgramNode):
        self.visit(node.main)
        for cls in node.classes:
            self.visit(cls)
        return self.builder.get_ir()

    def visit_MainClassNode(self, node: MainClassNode):
        self.builder.add('begin_main', None, None, None)
        # NOTE: do NOT emit a 'label main' — x86 backend already emits 'main:'
        for stmt in getattr(node, 'statements', []):
            self.visit(stmt)
        self.builder.add('end_main', None, None, None)

    def visit_ClassDeclNode(self, node: ClassDeclNode):
        for m in getattr(node, 'method_decls', []):
            self.visit(m)

    def visit_MethodDeclNode(self, node: MethodDeclNode):
        lbl = f"{node.name}"
        self.builder.add('label', lbl, None, None)
        for stmt in getattr(node, 'statements', []):
            self.visit(stmt)
        if node.return_expr:
            val = self.visit(node.return_expr)
            if isinstance(val, int):
                t = self.builder.new_temp()
                self.builder.add('=', val, None, t)
                val = t
            self.builder.add('return', val, None, None)

    # --- Statements ---
    def visit_BlockNode(self, node: BlockNode):
        for s in getattr(node, 'statements', []):
            self.visit(s)

    def visit_IfNode(self, node: IfNode):
        cond = self.visit(node.cond)
        if isinstance(cond, int):
            t = self.builder.new_temp()
            self.builder.add('=', cond, None, t)
            cond = t
        L_else = self.builder.new_label('ELSE')
        L_end = self.builder.new_label('END_IF')
        self.builder.add('if_false', cond, L_else, None)
        self.visit(node.then_stmt)
        self.builder.add('goto', L_end, None, None)
        self.builder.add('label', L_else, None, None)
        self.visit(node.else_stmt)
        self.builder.add('label', L_end, None, None)

    def visit_WhileNode(self, node: WhileNode):
        L_start = self.builder.new_label('LOOP')
        L_end = self.builder.new_label('ENDL')
        self.builder.add('label', L_start, None, None)
        cond = self.visit(node.cond)
        if isinstance(cond, int):
            t = self.builder.new_temp()
            self.builder.add('=', cond, None, t)
            cond = t
        self.builder.add('if_false', cond, L_end, None)
        self.visit(node.body)
        self.builder.add('goto', L_start, None, None)
        self.builder.add('label', L_end, None, None)

    def visit_PrintNode(self, node: PrintNode):
        v = self.visit(node.expr)
        if isinstance(v, int):
            t = self.builder.new_temp()
            self.builder.add('=', v, None, t)
            v = t
        self.builder.add('print', v, None, None)

    def visit_AssignNode(self, node: AssignNode):
        rhs = self.visit(node.expr)
        self.builder.add('=', rhs, None, node.name)

    # --- Expressions ---
    def visit_IntLiteralNode(self, node: IntLiteralNode):
        return node.value
    def visit_BoolLiteralNode(self, node: BoolLiteralNode):
        return 1 if node.value else 0
    def visit_VarNode(self, node: VarNode):
        return node.name
    def visit_BinaryOpNode(self, node: BinaryOpNode):
        left = self.visit(node.left)
        right = self.visit(node.right)
        dest = self.builder.new_temp()
        if node.op in ['+', '-', '*', '<']:
            self.builder.add(node.op, left, right, dest)
            return dest
        raise NotImplementedError(f"Operator {node.op} not implemented in IR")
    def visit_UnaryOpNode(self, node: UnaryOpNode):
        raise NotImplementedError("Unary '!' not implemented in IR")
