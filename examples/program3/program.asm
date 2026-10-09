; Reconstructed from preserved words, not original assembly source.
; r1..r8 encode indices 0..7. Mnemonics express coursework intention.
; See docs/isa.md for actual circuit behavior and known faults.
li r1, 6               ; address 00, word 0006
li r2, 5               ; address 01, word 0205
and r3, r1, r2         ; address 02, word 5014
li r8, 0               ; address 03, word 0e00
store r3, r8           ; address 04, word 9e80
or r4, r1, r2          ; address 05, word 6016
li r8, 1               ; address 06, word 0e01
store r4, r8           ; address 07, word 9ec0
li r8, 1               ; address 08, word 0e01
load r7, r8            ; address 09, word 8dc0
halt                   ; address 10, word f000
