section .data
  fmt_int: db "%d", 10, 0

section .text
  global main
  extern printf

main:
  mov eax, 2
  mov ebx, 3
  mov ecx, ebx
  imul ecx, ebx
  mov edx, eax
  add edx, ecx
  mov esi, eax
  imul esi, edx
  mov edi, esi
  push dword edi
  push dword fmt_int
  call printf
  add esp, 8
  mov eax, 0
  ret