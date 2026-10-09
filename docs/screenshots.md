# GUI observation notes

No GUI screenshots are included, and opening, loading and stepping the desktop GUI were not independently reproduced during this review. These views can help compare a manual run with the [automated traces](verification.md):

| View | Useful observations |
| --- | --- |
| `CPU` | PC, ROM, decoder, CU, register file, ALU and RAM; the circuit spans roughly x=260..2770 |
| `PC` | Target multiplexers, incrementer, PC register, halt/reset and return paths |
| `REG_file` | Eight general registers, read multiplexers, write decoder and separate return-address register |
| Program 3 | PC, RAM locations 0 and 1, and r7; the automated trace holds PC at 000a with RAM values 4 and 7 and r7=0 |
| Program 4 | The first return and later control flow; the recorded first-return state has PC=3, r3=10 and RA=3 |

Pause clocks before loading ROM or toggling reset high/low. Reset does not clear RAM, so independent runs need fresh simulation states. Step low/high phases with propagation. A screenshot of a particular state would document that observation; it would not by itself establish complete program success or resolve the manual/automated discrepancy.
