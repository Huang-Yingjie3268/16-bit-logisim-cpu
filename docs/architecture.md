# Implemented CPU architecture

The student reports that all four demonstration programs ran successfully during the original coursework manual tests. Later automated traces differ from those observations. The original manual results have not been independently reproduced in this review, and the discrepancy is unresolved. The technical observations below describe the later automated/static checks rather than a conclusive diagnosis across both testing methods.

The project declares Logisim Evolution 3.9.0 and main circuit CPU. Its six circuits are CPU, PC, REG_file, ALU, op_decode and CU. ROM/RAM are built-in components in CPU. Instruction, register, ALU and memory data paths are 16 bits. Both memories have 16 address bits: 65536 word locations each.

## Top-level datapath

PC drives ROM address and the target adder. ROM feeds op_decode; opcode feeds CU and three top-level PLAs. Decoded register fields drive register selection. Register reads and immediate drive operand muxes; ALU result drives writeback and RAM address. Register read1 supplies RAM write data; RAM output feeds writeback. ALU predicates and RA feed PC; RA receives current PC plus one on call. No instruction register or pipeline stages are present. The README diagram summarizes these actual paths.

## Program counter

PC contains a 16-bit rising-edge register at (870,280), incrementer with constant 1, and target/return muxes. Reset drives clear; inverted Halt drives enable. The top-level target adder forms `PC + decoded target`; a mux chooses decoded target directly only for opcode C. Therefore jump is absolute and call relative.

Inside PC, one-bit branch flags and PCSrc_Branch are expanded to two bits using **sign extension**. True becomes 11, not 01. Target mux (770,340) and next-PC mux (1020,310) have their branch target wired only to input 1. A taken branch selects unwired input 3; this causes program 1's unknown PC. Call uses JumpType 01 and reaches the wired target. Return uses JumpType 10; the final mux selects RA and overrides the intermediate path.

## Register file

Eight 16-bit registers encode indices 0..7, ordered top to bottom at x=810. A three-to-eight decoder and AND gates combine destination selection with RegWrite. A shared input mux chooses ALU result (0), RAM data (1), immediate (2), or zero (3). Li actually uses ALU pass-through and source 0; its direct immediate mux input exists but is not selected by the CU row.

Two eight-input muxes provide combinational reads. General writes, RA writes and PC updates share a rising edge. The separate RA register at (730,1330) stores PC+1 when RaWrite is asserted. Reset clears all nine registers. A new call overwrites RA; no call stack is supplied.

## ALU and operand selection

ALU mux choices are add (0), AND (1), OR (2), second-input pass-through (3). Signed two's-complement comparison computes ble from NOT(greater-than) and bne from NOT(equal), gated by BranchCond bits.

Top-level mux (2220,620) chooses read2 or immediate for input B. Mux (2230,580) chooses read1 or read2 for input A. The later wiring review identifies PLA (2270,740) as selecting read2 for A during immediate arithmetic/logic. Load is absent from both operand-selector PLAs, taking their zero outputs: A=read1, B=read2. Its address therefore depends on old destination data. Store selects A=read2, B=immediate.

## Decoder and control

op_decode splits opcode bits 15:12, extracts R/I fields, and uses a PLA to select format. Branch format reverses read selectors relative to I. Immediate and target extenders both default to sign extension. [isa.md](isa.md) gives exact fields.

CU maps opcodes to 14-bit control words split as:

```text
[13:12] JumpType    [11:10] RegWriteSource
[9] Halt           [8] RaWrite
[7:6] BranchCond   [5] PCSrc_Branch
[4] MemWrite       [3] MemRead
[2:1] ALUOp        [0] RegWrite
```

Opcode 4 has word `00000000000001`: ALU add and general write. Opcode D has `01000100100000`: target selection and RA write. Opcode F has `00001000000000`: halt gating.

## ROM, RAM and reset

ROM at CPU (870,190) embeds program 4 in XML. No external file or library path needs rewriting after relocation. RAM at (2340,260) has distinct input/output data buses despite its stored `databus=bibus` attribute under the selected byte-enable configuration. Loaded attributes include asyncread=false, trigger=rising and readbehav=raw. Read output updates on the edge when the destination register samples writeback. Program 3 stores RAM[1]=7 but leaves r7=0 at halt. No load wait cycle exists. RAM has no clear/reset pin; independent trials use fresh states.

## An actual instruction trace

Program 3 at PC=2 contains 0x5014 (`and r3, r1, r2`), after r1=6 and r2=5:

1. ROM emits 0x5014; decoder selects rs=0, rt=1, rd=2.
2. CU selects ALUOp=1 and enables ALU writeback.
3. Read ports and operand muxes supply 6 and 5.
4. ALU computes `6 AND 5 = 4`.
5. Next rising edge stores r3=4 and advances PC to 3; the simulator trace records this at half-tick 5.

## Verification boundary

Circuit bytes, layout, wires, embedded ROM and historical program words are unchanged. Loading and bounded real-simulator execution were tested. GUI screenshots, exhaustive ISA tests and performance measurements remain untested. The recorded trace concerns remain available for comparison with the original manual observations; no circuit changes were made.
