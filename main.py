# main.py
import os
import sys
import traceback

from compiler.lexer import build_lexer
from compiler.parser import build_parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.codegen.intermediate import IRGenerator
from compiler.codegen.x86 import X86StyleGenerator
from compiler.utils.tree_visualizer import visualize_parse_tree
from compiler.utils.errors import CompilerError, error_message

def print_ast(node, depth=0, max_depth=6):
    prefix = "  " * depth
    if node is None:
        print(prefix + "None")
        return
    # prefer node.name if present
    name = getattr(node, "name", node.__class__.__name__)
    print(prefix + f"{name}  ({node.__class__.__name__})")
    if depth >= max_depth:
        return
    # prefer children
    children = getattr(node, "children", None)
    if children is not None:
        for c in children:
            if c is None:
                print(prefix + "  None")
            else:
                print_ast(c, depth+1, max_depth)
        return
    # fallback: inspect attributes that look like AST nodes or lists
    for attr in dir(node):
        if attr.startswith("_") or attr in ("name", "children"):
            continue
        try:
            val = getattr(node, attr)
        except Exception:
            continue
        if isinstance(val, list) and val:
            print(prefix + f"  .{attr} -> [")
            for item in val:
                print_ast(item, depth+2, max_depth)
            print(prefix + "  ]")
        elif hasattr(val, "name"):
            print(prefix + f"  .{attr} ->")
            print_ast(val, depth+1, max_depth)

def compile_file(java_file_path):
    try:
        if not os.path.isfile(java_file_path):
            print(f"Error: File '{java_file_path}' does not exist.")
            return

        base_name = os.path.splitext(os.path.basename(java_file_path))[0]
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        print(f"--- Compiling {java_file_path} ---")
        with open(java_file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        parser, lexer = build_parser()

        # Tokens (fresh lexer)
        
        lexer.input(source_code)
        tokens_out = []
        print("--- 1. Lexical Tokens ---")
        for tok in lexer:
            tokens_out.append(str(tok))
        print("-------------------------")

        # Save tokens to file (same basename as test file)
        base_name = os.path.splitext(os.path.basename(java_file_path))[0]
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Write tokens to file
        tokens_path = os.path.join(output_dir, f"{base_name}_tokens.txt")
        with open(tokens_path, "w", encoding="utf-8") as f:
            f.write("\n".join(tokens_out))
        print(f"Tokens saved to {tokens_path}")
        print("----------------------------\n")

        # Parsing
        print("--- 2. Parsing (Syntax Analysis) ---")
        try:
            ast = parser.parse(source_code, lexer=lexer)
        except CompilerError as e:
            print(error_message(e))
            return
        except Exception as e:
            print("Parsing raised an unexpected exception:")
            traceback.print_exc()
            return

        if ast is None:
            print("Parser returned None (no AST). Stopping.")
            return

        # Visualize parse tree -> saves to output/<base_name>.png
        tree_image_path = os.path.join(output_dir, f"{base_name}")
        try:
            png_path = visualize_parse_tree(ast, tree_image_path)
            print(f"Parse tree saved to {png_path}")
        except Exception:
            print("Warning: Could not generate parse tree image; stacktrace follows:")
            traceback.print_exc()

        # Semantic analysis
        print("\n--- 3. Semantic Analysis ---")
        semantic = SemanticAnalyzer()
        errors = semantic.analyze(ast)
        if errors:
            print("Semantic errors found:")
            for err in errors:
                print(f" - {err}")
            return
        print("No semantic errors.")
        print("----------------------------\n")

        # IR / TAC generation
        print("--- 4. IR (TAC) Generation ---")
        ir_gen = IRGenerator()
        tac = ir_gen.visit(ast)
        if tac is None:
            print("IR generator returned None (expected list). Stopping.")
            return

        # Save TAC
        tac_output_path = os.path.join(output_dir, f"{base_name}_tac.txt")
        with open(tac_output_path, 'w', encoding='utf-8') as f:
            for instr in tac:
                f.write(str(instr) + "\n")
        print(f"TAC saved to {tac_output_path}")
        print("-----------------------------\n")

        # x86 generation
        print("--- 5. x86-Style Code Generation ---")
        x86 = X86StyleGenerator()
        asm = x86.generate(tac)
        asm_output_path = os.path.join(output_dir, f"{base_name}.asm")
        with open(asm_output_path, 'w', encoding='utf-8') as f:
            f.write(asm)
        print(f"x86-style assembly saved to {asm_output_path}")
        print("-------------------------------\n")

    except Exception:
        print("Unexpected compiler error:")
        traceback.print_exc()

def main():
    print("=== MiniJava Compiler (x86 backend) ===")
    if len(sys.argv) > 1:
        java_file_path = sys.argv[1]
    else:
        java_file_path = input("Enter the path to the MiniJava (.java) source file: ").strip()
    compile_file(java_file_path)

if __name__ == "__main__":
    main()
