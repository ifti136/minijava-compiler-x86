# compiler/utils/errors.py

class CompilerError(Exception):
    pass

class LexerError(CompilerError):
    pass

class ParserError(CompilerError):
    pass

class SemanticError(CompilerError):
    pass

def error_message(e):
    return f"[{e.__class__.__name__}] {str(e)}"
