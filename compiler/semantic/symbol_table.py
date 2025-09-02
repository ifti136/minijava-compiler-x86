class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}      # for variables, methods etc.
        self.classes = {}      # top-level classes only
        self.parent = parent

    # Insert symbol (variable, method, etc.)
    def insert(self, name, info):
        if name in self.symbols:
            raise Exception(f"Duplicate symbol '{name}'")
        self.symbols[name] = info

    # Lookup symbol in current or parent scopes
    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None

    # Insert a class at top-level
    def add_class(self, class_name, class_info):
        if class_name in self.classes:
            raise Exception(f"Duplicate class '{class_name}'")
        self.classes[class_name] = class_info

    # Lookup class info
    def lookup_class(self, class_name):
        return self.classes.get(class_name, None)

    def __repr__(self):
        return f"SymbolTable(classes={self.classes}, symbols={self.symbols})"