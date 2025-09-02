# compiler/ast/visitor.py
class Visitor:
    def visit(self, node):
        if node is None:
            return None
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # default: traverse children and return None
        res = None
        if hasattr(node, 'children'):
            for c in getattr(node, 'children') or []:
                if c is None:
                    continue
                if isinstance(c, list):
                    for x in c:
                        self.visit(x)
                else:
                    self.visit(c)
        return res
