section .data
  fmt_int: db "%d", 10, 0

section .text
  global main
  extern printf

main:
  mov eax, 0
LOOP1:
  mov ebx, eax
  cmp ebx, 5
  setl al
  movzx ebx, al
  cmp ebx, 0
  je ENDL2
  push dword eax
  push dword fmt_int
  call printf
  add esp, 8
  mov ecx, eax
  add ecx, 1
  mov eax, ecx
  jmp LOOP1
ENDL2:
  mov eax, 0
  ret