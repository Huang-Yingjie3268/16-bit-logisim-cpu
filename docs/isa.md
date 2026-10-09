# Instruction set and implemented behavior

The student reports that all four demonstration programs ran successfully during the original coursework manual tests. Later automated traces differ from those observations. The original manual results have not been independently reproduced in this review, and the discrepancy is unresolved. The technical observations below describe the later automated/static checks rather than a conclusive diagnosis across both testing methods.

The circuit is primary evidence. Opcode routing was checked against the decoder PLA, CU PLA, splitters, operand muxes and PC wiring using Logisim Evolution 3.9.0. All four program encodings agree across binary text, hex text and big-endian bytes. Instruction names come from the coursework reference; implemented behavior is described separately below.

## Registers and formats

Names `r1` through `r8` denote indices `000` through `111`. All eight are writable; r1 is not a hardwired zero register. RA is a separate 16-bit register inaccessible through the three-bit general-register index.

```text
R: [15:12 opcode] [11:10 unused] [9:7 rs] [6:4 rt] [3:1 rd] [0 unused]
I: [15:12 opcode] [11:9 rd] [8:6 rs] [5:0 immediate]
J: [15:12 opcode] [11:0 target]
```

Unused R fields are zero in supplied programs; no reserved-bit enforcement exists. R opcodes 4/5/6 select format 0. I opcodes 0/1/2/3/7/8/9 select format 1. Branches A/B select format 2: the same I bits feed read1 from `[11:9]` and read2 from `[8:6]`. C/D select format 3. Return/halt have no explicit decoder-format row, but CU suppresses general writes.

Both six-bit immediates and twelve-bit J targets are **sign-extended**, using the simulator's default extender type. I immediates therefore represent -32..31; J fields represent -2048..2047. Logical immediates also sign-extend. Arithmetic wraps modulo 65536. Memory addresses index 16-bit words, not byte offsets.

The answer sheet's generic R layout matches the decoder, but its individual R rows order operand names differently. The circuit and example words establish the layout above.

## Opcodes and semantics

Here d/s/t are register indices, i is a sign-extended immediate and j a sign-extended J field. Assembly order is destination first, except `store value, address` and branches `left, right, offset`.

| Opcode | Mnemonic and format | Implemented behavior and limitation |
| --- | --- | --- |
| `0000` | `li d, i` (I; rs conventionally zero) | `R[d] = i`; ALU passes its second input. |
| `0001` | `addi d, s, i` (I) | Actually `R[d] = old R[d] + i`; first-operand mux reads old destination. Intended s is ignored. Static analysis only. |
| `0010` | `andi d, s, i` (I) | Actually `R[d] = old R[d] AND i`; same selection fault. |
| `0011` | `ori d, s, i` (I) | Actually `R[d] = old R[d] OR i`; same selection fault. |
| `0100` | `add d, s, t` (R) | `R[d] = R[s] + R[t]`. |
| `0101` | `and d, s, t` (R) | `R[d] = R[s] AND R[t]`. |
| `0110` | `or d, s, t` (R) | `R[d] = R[s] OR R[t]`. |
| `0111` | `move d, s` (I; immediate zero) | ALU adds `R[s] + i`; canonical zero immediate copies s. |
| `1000` | `load d, s` (I; immediate zero) | Enables RAM read/writeback to d. ALU address actually equals `R[s] + old R[d]`. Synchronous RAM read and same-edge writeback cause stale data in program 3. |
| `1001` | `store s, d` (I; immediate zero) | Address `R[d] + i`, data `R[s]`; no general write. |
| `1010` | `ble left, right, i` (branch/I bits) | Signed `R[left] <= R[right]`. Intended taken target `PC + i`; actual selector 3 chooses unwired inputs, making PC unknown. False condition uses `PC + 1`. |
| `1011` | `bne left, right, i` (branch/I bits) | Inequality predicate; same broken taken-branch path. Static analysis only. |
| `1100` | `jump j` (J) | `PC = j`, absolute word address after sign extension. |
| `1101` | `call j` (J) | `RA = PC + 1`; `PC = PC + j`, relative to current instruction. |
| `1110` | `rtn` (canonical `e000`) | `PC = RA`; no stack/nested-call preservation. |
| `1111` | `halt` (canonical `f000`) | Disables PC updates; clock can still toggle. CU disables register/RAM writes. |

Normal sequencing advances PC by one on a rising edge. Reset clears PC, eight general registers and RA, but not RAM. Load's intended behavior is `R[d] = RAM[R[s]]`; that behavior has not passed functional testing.

## Encoding example

`add r3, r1, r2` uses opcode 0100, source indices 000 and 001, destination 010:

```text
0100 00 000 001 010 0 = 0100000000010100 = 0x4014
```

`call 7` is 0xd007; at address 2 it reaches address 9 and saves 3 in RA, as observed. `jump 3` is 0xc003 and targets address 3 absolutely.

## Evidence and coverage

CU has a defined 14-bit row for every opcode. This confirms routing, not full instruction correctness. The four examples do not exercise addi, bne, all negative immediates, or nested calls. Assembly annotations retain historical words even when their intended effect fails. See [architecture.md](architecture.md) and [verification.md](verification.md).

Simulator defaults were checked against versioned sources: [BitExtender.java](https://github.com/logisim-evolution/logisim-evolution/blob/v3.9.0/src/main/java/com/cburch/logisim/std/wiring/BitExtender.java) and [Comparator.java](https://github.com/logisim-evolution/logisim-evolution/blob/v3.9.0/src/main/java/com/cburch/logisim/std/arith/Comparator.java).
