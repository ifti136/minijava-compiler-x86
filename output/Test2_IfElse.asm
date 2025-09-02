section .data
  fmt_int: db "%d", 10, 0

section .text
  global main
  extern printf

main:
  mov eax, 4
  mov ebx, 6
  mov ecx, eax
  cmp ecx, ebx
  setl al
  movzx ecx, al
  cmp ecx, 0
  je ELSE1
  push dword eax
  push dword fmt_int
  call printf
  add esp, 8
  jmp END_IF2
ELSE1:
  push dword ebx
  push dword fmt_int
  call printf
  add esp, 8
END_IF2:
  mov eax, 0
  ret