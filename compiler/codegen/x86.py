# compiler/codegen/x86.py
class X86StyleGenerator:
    REG_ORDER = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi']

    def __init__(self):
        self.register_map = {}
        self.next_reg = 0
        self.label_count = 0

    def alloc_reg(self, name):
        # Map temps/vars to registers; immediates should never come here
        if name not in self.register_map:
            if self.next_reg < len(self.REG_ORDER):
                self.register_map[name] = self.REG_ORDER[self.next_reg]
                self.next_reg += 1
            else:
                self.register_map[name] = f"mem_{name}"
        return self.register_map[name]

    def new_label(self, prefix='L'):
        self.label_count += 1
        return f"{prefix}{self.label_count}"

    def _opnd(self, x):
        # helper: produce operand text for reg/imm
        if isinstance(x, int):
            return str(x)
        return self.alloc_reg(x)

    def generate(self, tac):
        lines = []
        lines.append("section .data")
        lines.append("  fmt_int: db \"%d\", 10, 0")
        lines.append("")
        lines.append("section .text")
        lines.append("  global main")
        lines.append("  extern printf")
        lines.append("")
        lines.append("main:")

        saw_end = False

        for instr in tac:
            if not instr:
                continue
            op, a, b, r = instr

            if op == 'begin_main':
                continue

            if op == 'label':
                # Avoid duplicating main: header (we don't expect 'main' now, but be safe)
                if str(a) != 'main':
                    lines.append(f"{a}:")
                continue

            if op == '=':
                dest = self._opnd(r)
                if isinstance(a, int):
                    lines.append(f"  mov {dest}, {a}")
                else:
                    lines.append(f"  mov {dest}, {self._opnd(a)}")
                continue

            if op in ('+', '-', '*', '<'):
                dest = self._opnd(r)

                # Load left into dest (immediate or reg)
                if isinstance(a, int):
                    lines.append(f"  mov {dest}, {a}")
                else:
                    lines.append(f"  mov {dest}, {self._opnd(a)}")

                # Apply op with RHS (handle immediates properly)
                if op == '+':
                    if isinstance(b, int):
                        lines.append(f"  add {dest}, {b}")
                    else:
                        lines.append(f"  add {dest}, {self._opnd(b)}")
                elif op == '-':
                    if isinstance(b, int):
                        lines.append(f"  sub {dest}, {b}")
                    else:
                        lines.append(f"  sub {dest}, {self._opnd(b)}")
                elif op == '*':
                    if isinstance(b, int):
                        lines.append(f"  imul {dest}, {b}")
                    else:
                        lines.append(f"  imul {dest}, {self._opnd(b)}")
                elif op == '<':
                    if isinstance(b, int):
                        lines.append(f"  cmp {dest}, {b}")
                    else:
                        lines.append(f"  cmp {dest}, {self._opnd(b)}")
                    lines.append(f"  setl al")
                    lines.append(f"  movzx {dest}, al")
                continue

            if op == 'if_false':
                # a = cond temp, b = label
                lines.append(f"  cmp {self._opnd(a)}, 0")
                lines.append(f"  je {b}")
                continue

            if op == 'goto':
                lines.append(f"  jmp {a}")
                continue

            if op == 'print':
                val = a
                if isinstance(val, int):
                    lines.append(f"  push {val}")
                else:
                    lines.append(f"  push dword {self._opnd(val)}")
                lines.append(f"  push dword fmt_int")
                lines.append(f"  call printf")
                lines.append(f"  add esp, 8")
                continue

            if op == 'end_main':
                lines.append("  mov eax, 0")
                lines.append("  ret")
                saw_end = True
                continue

            if op == 'return':
                if isinstance(a, int):
                    lines.append(f"  mov eax, {a}")
                else:
                    lines.append(f"  mov eax, {self._opnd(a)}")
                lines.append("  ret")
                continue

            lines.append(f"  ; unsupported: {instr}")

        if not saw_end:
            lines.append("  mov eax, 0")
            lines.append("  ret")

        return "\n".join(lines)
