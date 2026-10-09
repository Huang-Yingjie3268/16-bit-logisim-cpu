; Reconstructed from preserved words, not original assembly source.
; r1..r8 encode indices 0..7. Mnemonics express coursework intention.
; See docs/isa.md for actual circuit behavior and known faults.
li r1, 1               ; address 00, word 0001
li r2, 2               ; address 01, word 0202
li r3, 10              ; address 02, word 040a
add r2, r1, r2         ; address 03, word 4012
ble r2, r3, -1         ; address 04, word a2bf
halt                   ; address 05, word f000
