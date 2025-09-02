# MiniJava Compiler (x86 Backend)

This project is a **MiniJava Compiler** implemented in **Python**.  
It takes a simplified subset of Java (MiniJava) as input and translates it through the full compilation pipeline:

1. **Lexical Analysis** – Tokenizes the source code using PLY.
2. **Syntax Analysis** – Parses the code into an Abstract Syntax Tree (AST).
3. **Semantic Analysis** – Performs type checking and validates program correctness.
4. **Intermediate Code Generation (TAC)** – Produces three-address code.
5. **x86-Style Assembly Generation** – Converts TAC into assembly-style output.

---

## 🚀 Features
- Supports MiniJava syntax (classes, main method, variables, arithmetic, if/while, print).
- Token stream output saved to `.txt`.
- Parse tree visualization generated as `.png` using Graphviz.
- Semantic error detection with descriptive messages.
- TAC (three-address code) generation.
- x86-style assembly code output.

---

## 📂 Project Structure
minijava-compiler-x86/
│── main.py # Compiler driver
│── compiler/
│ ├── lexer.py # Lexical analyzer
│ ├── parser.py # Syntax analyzer
│ ├── semantic/
│ │ ├── analyzer.py # Semantic analysis
│ │ └── symbol_table.py # Symbol table
│ ├── ast_nodes/ # AST node definitions & visitor
│ ├── codegen/
│ │ ├── intermediate.py # IR (TAC) generation
│ │ └── x86.py # x86-style assembly generator
│ ├── utils/
│ │ ├── errors.py # Custom compiler errors
│ │ └── tree_visualizer.py # Parse tree visualization
│ └── tests/ # Place for sample test programs
│── output/ # Generated tokens, TAC, assembly, trees

---

## ⚙️ Requirements
- **Python 3.8+**
- [PLY](https://www.dabeaz.com/ply/) (Python Lex-Yacc)
- [Graphviz](https://graphviz.org/) (for parse tree visualization)

Install dependencies:
```bash
pip install ply graphviz

You also need to have Graphviz installed on your system:

Windows: Download installer [https://graphviz.org/download/]

Linux (Debian/Ubuntu):
```bash
sudo apt-get install graphviz

macOS (Homebrew):
```bash
brew install graphviz

