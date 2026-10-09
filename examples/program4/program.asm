; Reconstructed from preserved words, not original assembly source.
; r1..r8 encode indices 0..7. Mnemonics express coursework intention.
; See docs/isa.md for actual circuit behavior and known faults.
li r1, 6               ; address 00, word 0006
li r2, 4               ; address 01, word 0204
call 7                 ; address 02, word d007
move r4, r3            ; address 03, word 7680
li r1, 7               ; address 04, word 0007
li r2, 8               ; address 05, word 0208
call 3                 ; address 06, word d003
move r5, r3            ; address 07, word 7880
jump 3                 ; address 08, word c003
add r3, r1, r2         ; address 09, word 4014
rtn                    ; address 10, word e000
halt                   ; address 11, word f000
