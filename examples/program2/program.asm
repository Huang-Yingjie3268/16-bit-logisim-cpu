; Reconstructed from preserved words, not original assembly source.
; r1..r8 encode indices 0..7. Mnemonics express coursework intention.
; See docs/isa.md for actual circuit behavior and known faults.
li r1, 6               ; address 00, word 0006
li r2, 5               ; address 01, word 0205
andi r3, r1, 3         ; address 02, word 2403
ori r4, r3, 8          ; address 03, word 3688
halt                   ; address 04, word f000
