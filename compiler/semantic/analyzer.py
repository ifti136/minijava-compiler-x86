# compiler/semantic/analyzer.py
from ..ast_nodes.nodes import *
from .symbol_table import SymbolTable

# NOTE: It's good practice to use your own custom error from utils,
# but using a local one is fine for this project's scope.
class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []
        self.current_class = None
        self.current_method = None
        self.INT = IntType()
        self.BOOL = BooleanType()

    def error(self, msg):
        self.errors.append(f"Error in class '{self.current_class}', method '{self.current_method}': {msg}")

    def analyze(self, program: ProgramNode):
        # Pass 1: Register all class names first to allow forward references
        self._register_main(program.main)
        for cls in program.classes:
            self._register_class(cls)
        
        if self.errors: return self.errors

        # Pass 2: Process members (fields and method signatures)
        for cls in program.classes:
            self.current_class = self.symtab.lookup_class(cls.name)
            self._process_class_members(cls)
            
        if self.errors: return self.errors
            
        # Pass 3: Check method bodies and main statement
        if isinstance(program.main, MainClassNode):
            self.current_class = self.symtab.lookup_class(program.main.name)
            self.current_method = self.current_class['methods']['main']
            
            # FIX: Properly check the main method's body like a regular method.
            main_locals = {}
            for var_decl in program.main.var_decls:
                if var_decl.name in main_locals:
                    self.error(f"Variable '{var_decl.name}' is already defined in main.")
                else:
                    main_locals[var_decl.name] = var_decl.type
            
            for stmt in program.main.statements:
                self._check_statement(stmt, main_locals)
                
        for cls_node in program.classes:
            self.current_class = self.symtab.lookup_class(cls_node.name)
            for method_node in cls_node.method_decls:
                self.current_method = self.current_class['methods'][method_node.name]
                self._check_method_body(method_node)

        return self.errors

    def _register_main(self, main: MainClassNode):
        if not isinstance(main, MainClassNode):
            self.error('No MainClass found')
            return
        main_info = {
            'name': main.name,
            'fields': {},
            'methods': {
                'main': {
                    'name': 'main',
                    'params': [('String[]', main.argname)],
                    'rtype': 'void' # Special type for main's return
                }
            }
        }
        try:
            self.symtab.add_class(main.name, main_info)
        except Exception as e:
            self.error(str(e))

    def _register_class(self, cls: ClassDeclNode):
        if self.symtab.lookup_class(cls.name):
            self.error(f'Duplicate class {cls.name}')
            return
        class_info = {'name': cls.name, 'fields': {}, 'methods': {}}
        self.symtab.add_class(cls.name, class_info)

    def _process_class_members(self, cls: ClassDeclNode):
        class_info = self.current_class
        # Fields
        for v in cls.var_decls:
            if v.name in class_info['fields']:
                self.error(f'Duplicate field {v.name}')
            else:
                class_info['fields'][v.name] = v.type
        # Methods
        for m in cls.method_decls:
            if m.name in class_info['methods']:
                self.error(f'Duplicate method {m.name}')
                continue
            
            param_info = []
            param_names = set()
            for p_type, p_name in m.params:
                if p_name in param_names:
                    self.error(f"Duplicate parameter name '{p_name}' in method '{m.name}'")
                param_names.add(p_name)
                param_info.append((p_type, p_name))
            
            class_info['methods'][m.name] = {
                'name': m.name,
                'params': param_info,
                'rtype': m.rtype,
                'node': m 
            }

    # FIX: Added function to process method bodies correctly
    def _check_method_body(self, method_node: MethodDeclNode):
        local_vars = {}
        # Add parameters to local scope
        for p_type, p_name in method_node.params:
            local_vars[p_name] = p_type
            
        # Add local declarations to scope, checking for duplicates
        for var_decl in method_node.var_decls:
            if var_decl.name in local_vars:
                self.error(f"Variable '{var_decl.name}' is already defined in this scope.")
            else:
                local_vars[var_decl.name] = var_decl.type

        # Check all statements in the method
        for stmt in method_node.statements:
            self._check_statement(stmt, local_vars)
            
        # Check return expression type
        return_expr_type = self._check_expression(method_node.return_expr, local_vars)
        if not self._types_compatible(method_node.rtype, return_expr_type):
            self.error(f"Return type mismatch. Expected {method_node.rtype} but got {return_expr_type}")
    
    def _lookup_variable_type(self, name, local_vars):
        # Look in local scope first
        if name in local_vars:
            return local_vars[name]
        # Then look in class fields
        if self.current_class and name in self.current_class['fields']:
            return self.current_class['fields'][name]
        return None

    def _check_statement(self, stmt, local_vars):
        if isinstance(stmt, BlockNode):
            # Create a new scope for the block to handle nested variable declarations if needed
            # For MiniJava, scopes are usually per-method, so we pass a copy
            block_locals = local_vars.copy()
            for s in stmt.statements:
                self._check_statement(s, block_locals)
        elif isinstance(stmt, IfNode):
            cond_type = self._check_expression(stmt.cond, local_vars)
            if not self._is_boolean_type(cond_type):
                self.error('Condition of if must be boolean')
            self._check_statement(stmt.then_stmt, local_vars.copy())
            self._check_statement(stmt.else_stmt, local_vars.copy())
        elif isinstance(stmt, WhileNode):
            cond_type = self._check_expression(stmt.cond, local_vars)
            if not self._is_boolean_type(cond_type):
                self.error('Condition of while must be boolean')
            self._check_statement(stmt.body, local_vars.copy())
        elif isinstance(stmt, PrintNode):
            expr_type = self._check_expression(stmt.expr, local_vars)
            if not self._is_int_type(expr_type):
                self.error('System.out.println expects an int expression')
        elif isinstance(stmt, AssignNode):
            expr_type = self._check_expression(stmt.expr, local_vars)
            var_type = self._lookup_variable_type(stmt.name, local_vars)
            if var_type is None:
                self.error(f'Undeclared variable {stmt.name} for assignment')
            elif not self._types_compatible(var_type, expr_type):
                self.error(f'Type mismatch in assignment to {stmt.name}: expected {var_type}, got {expr_type}')
        elif isinstance(stmt, ArrayAssignNode):
            # FIX: Correctly check array assignment types
            var_type = self._lookup_variable_type(stmt.name, local_vars)
            if var_type is None:
                self.error(f'Undeclared array {stmt.name}')
            elif not isinstance(var_type, ArrayType):
                self.error(f'Variable {stmt.name} is not an array')
            else:
                index_type = self._check_expression(stmt.index, local_vars)
                if not self._is_int_type(index_type):
                    self.error('Array index must be an integer')
                
                expr_type = self._check_expression(stmt.expr, local_vars)
                # Compare expression type to the array's base type
                array_base_type = IntType() if var_type.base == 'int' else None # Assuming only int arrays
                if not self._types_compatible(array_base_type, expr_type):
                    self.error(f'Type mismatch in array assignment to {stmt.name}: expected {array_base_type} but got {expr_type}')

    def _check_expression(self, expr, local_vars):
        if expr is None: return None
        if isinstance(expr, IntLiteralNode): return self.INT
        if isinstance(expr, BoolLiteralNode): return self.BOOL
        if isinstance(expr, VarNode):
            var_type = self._lookup_variable_type(expr.name, local_vars)
            if var_type is None:
                self.error(f'Undeclared variable {expr.name}')
                return None
            return var_type
        if isinstance(expr, BinaryOpNode):
            left_t = self._check_expression(expr.left, local_vars)
            right_t = self._check_expression(expr.right, local_vars)
            op = expr.op
            if op in ['+', '-', '*', '/']:
                if self._is_int_type(left_t) and self._is_int_type(right_t): return self.INT
                self.error(f'Arithmetic operator "{op}" requires int operands')
            elif op == '<':
                if self._is_int_type(left_t) and self._is_int_type(right_t): return self.BOOL
                self.error('"<" requires int operands')
            elif op in ['&&', '||']:
                if self._is_boolean_type(left_t) and self._is_boolean_type(right_t): return self.BOOL
                self.error(f'Logical operator "{op}" requires boolean operands')
            return None
        if isinstance(expr, UnaryOpNode):
            if expr.op == '!':
                t = self._check_expression(expr.expr, local_vars)
                if self._is_boolean_type(t): return self.BOOL
                self.error('! operator expects a boolean operand')
            return None
        if isinstance(expr, ArrayAccessNode):
            arr_t = self._lookup_variable_type(expr.name, local_vars)
            if not isinstance(arr_t, ArrayType):
                self.error(f'{expr.name} is not an array')
                return None
            idx_t = self._check_expression(expr.index, local_vars)
            if not self._is_int_type(idx_t):
                self.error('Array index must be int')
            return IntType() # MiniJava only has int arrays
        if isinstance(expr, ArrayLengthNode):
            arr_t = self._lookup_variable_type(expr.name, local_vars)
            if not isinstance(arr_t, ArrayType):
                self.error(f'{expr.name} is not an array for length')
            return self.INT
        if isinstance(expr, MethodCallNode):
            # FIX: Correctly check method calls based on object type
            obj_type = self._check_expression(expr.obj, local_vars)
            if not isinstance(obj_type, ClassType):
                self.error(f"Variable '{expr.obj.name}' is not a class instance.")
                return None
            
            class_info = self.symtab.lookup_class(obj_type.name)
            if not class_info:
                self.error(f"Class '{obj_type.name}' not found.")
                return None
            
            method_info = class_info['methods'].get(expr.method)
            if not method_info:
                self.error(f"Method '{expr.method}' not found in class '{class_info['name']}'.")
                return None
            
            # Check arity
            expected_args = len(method_info['params'])
            actual_args = len(expr.args)
            if expected_args != actual_args:
                self.error(f"Method '{expr.method}' expects {expected_args} arguments, but got {actual_args}.")
                return None # Stop checking this call
            
            # Check argument types
            for i, arg_expr in enumerate(expr.args):
                arg_type = self._check_expression(arg_expr, local_vars)
                param_type = method_info['params'][i][0]
                if not self._types_compatible(param_type, arg_type):
                    self.error(f"Type mismatch for argument {i+1} of method '{expr.method}'. Expected {param_type} but got {arg_type}.")

            return method_info['rtype']
        return None

    def _is_int_type(self, t): return isinstance(t, IntType)
    def _is_boolean_type(self, t): return isinstance(t, BooleanType)

    def _types_compatible(self, dest_t, src_t):
        if dest_t is None or src_t is None: return False
        if isinstance(dest_t, ArrayType) and isinstance(src_t, ArrayType):
            return dest_t.base == src_t.base
        # Allow assigning subclass to superclass (not implemented here, but this is where it would go)
        if isinstance(dest_t, ClassType) and isinstance(src_t, ClassType):
             return dest_t.name == src_t.name
        return type(dest_t) == type(src_t)