# Coursework testing and automated trace notes

The student reports that all four demonstration programs ran successfully during the original coursework manual tests. Later automated traces differ from those observations. The original manual results have not been independently reproduced in this review, and the discrepancy is unresolved. The technical observations below describe the later automated/static checks rather than a conclusive diagnosis across both testing methods.

Recorded trace-check date: 2026-10-09 (Asia/Shanghai). This report separates artifact preservation and encoding checks from functional correctness. The existing circuit was preserved without logic fixes.

## PASS

- Circuit XML parses; main CPU and all six named circuits are present.
- Circuit is byte-identical to Coursework4.circ, including its embedded program 4 ROM.
- Logisim Evolution 3.9.0 successfully loads the original and relocated circuit through its Java API. All libraries are built-in and no external dependency path is present.
- All 34 words across four programs match the original binary text, executable hex text and raw binary outputs. Normalization changes whitespace only.
- Original gen_bin.py and gen_bin234.py were executed in independent temporary audit directories; their outputs matched the supplied .bin files.
- Consolidated converter was run through its CLI for all four inputs, in both binary and Logisim formats. Big-endian bytes match the original .bin files exactly; generated hex words match each original v2.0 raw image.
- Five automated test methods pass, covering all example encodings and reconstructed annotations, word order, byte order, whitespace, malformed input, error line numbers, missing files, and protection against overwriting input or existing output on malformed input.
- Relocated circuit traces equal original-circuit traces for every program: 121 snapshots each, reset followed by 120 low/high half-ticks. This is preservation evidence, not a claim of CPU correctness.
- Partial functional behavior observed: li, register add/AND/OR, stores, moves, relative calls, returns and halt PC gating in the exercised sequences.
- Local Markdown links and publication-set privacy checks pass. No missing screenshot references, personal identifiers, coursework answer sheet or unsolicited license is included.

Circuit SHA-256: `b6470ea4c073dc8fb3b3dab260ab6e40309d7a896c0f9c8f0b48a9a32a37be8e`

| Program | Words | Bytes | Raw binary SHA-256 |
| --- | ---: | ---: | --- |
| 1 | 6 | 12 | `99b10a59c2bb28f52fb3575ba192eb8a1c063c0b7f1b5dde61ee92769c4b772e` |
| 2 | 5 | 10 | `eecceab1489e4538795011db2ecf23999340315d1aad3feb134a6199da6ce7ef` |
| 3 | 11 | 22 | `41cf4dc536c64f1f5078f06b4db0d24771429a542d3be043b62ea466d20abc14` |
| 4 | 12 | 24 | `c9c2aadfbade9d56df52af6233534b84d8776d13f3c5e4015ddb85679d5f3921` |

## Automated results that differ from intended behavior

Register values below are decimal unless shown as a hexadecimal PC. Expected states are derived from coursework-intended instruction meanings, not prior measured successful runs.

| Program | Intention | Actual simulation |
| --- | --- | --- |
| 1 | Increment r2 while r2 <= r3; intended halt with r1=1, r2=11, r3=10 | At half-tick 7: PC=0004, r2=3. First taken ble makes PC unknown at half-tick 9. No successful loop completion. |
| 2 | r3=6 AND 3=2; r4=2 OR 8=10, then halt | PC holds at 0004, but r3=0 and r4=8. Halt gating works; intended values fail. |
| 3 | RAM[0]=4, RAM[1]=7; load RAM[1] into r7 | PC holds at 000a; RAM stores are 4 and 7, but r7=0. Load writeback fails. |
| 4 | Exercise two calls to address 9 and save their results; a single pass produces r4=10, r5=15 | First call at PC=2 reaches 9 with RA=3. Second call at PC=6 reaches 9 with RA=7. At half-tick 23 r4=10, r5=15; jump at address 8 returns to 3 at tick 25. It never reaches halt at 11 within the bound. Later iterations overwrite r4 with 15. |

Program 4's preserved `jump 3` is an absolute jump in this circuit; interpreting it as a relative skip of three words would change its semantics. Its nontermination is a program/implemented-ISA mismatch, not evidence that absolute jump fails.

## Possible explanations from the later wiring review

1. Taken branches: PC sign-extends one-bit true conditions to two-bit 11. Two four-input muxes select unwired input 3 instead of the branch-target input 1. The decoder's target uses the six-bit signed offset; the intended arithmetic is current PC plus that offset.
2. Immediate arithmetic/logic: top-level PLA at (2270,740) selects register read2 for ALU input A for opcodes 1/2/3. Normal I read2 is the old destination, while the encoded source is read1. The static fault also applies to untested addi.
3. Load: RAM is synchronous-read while register writeback samples on the same rising edge, with no wait cycle. Program 3 samples old read data. Load also lacks explicit operand-selector PLA rows; its address equals source plus old destination, which happens to be zero in this test.
4. Program 4 control flow: call uses a current-PC-relative offset, while jump uses an absolute target. The original word c003 revisits address 3 instead of reaching the final halt.

These issues were documented without modifying original logic or test words. Follow-up fixes should be reviewed separately, preserve the historical baseline, and rerun functional tests rather than merely comparing old traces.

## NOT TESTED

- Opening, memory-loading controls and stepping in the desktop GUI; GUI screenshots.
- Exhaustive ISA coverage: addi, bne, all signed immediate extremes, all register combinations, nested calls, memory bounds and address wraparound.
- Performance, timing or hardware implementation.
- Publication to GitHub and authorization for licensing joint work.

## Reproducing the checks

From the repository root, with Python 3.10 or newer:

```bash
python -m unittest discover -s tests -v
python scripts/generate_memory.py --input examples/program1/machine_code.txt --output examples/program1/memory.bin
python scripts/generate_memory.py --input examples/program1/machine_code.txt --output examples/program1/generated_image.txt --format logisim
```

The trace utility uses the real simulator API, not a reimplemented CPU emulator. It loads program words into ROM in memory, creates a fresh CircuitState, drives reset high then low with propagation, drives Clock.tick explicitly, and records registers and two RAM locations. It does not save or modify the .circ file. Explicit dirty notifications are required because the audit state is separate from the Project's default state.

PowerShell example; replace the JAR path and adjust the installed JDK path:

```powershell
$java = 'C:\Program Files\Java\jdk-24\bin\java.exe'
$jar = 'C:\path\to\logisim-evolution-3.9.0-all.jar'
New-Item -ItemType Directory -Path verification-output -Force | Out-Null
& $java '-Djava.awt.headless=true' -cp $jar scripts/CpuTrace.java cpu/simple_16bit_cpu.circ examples/program1/memory_image.txt 120 > verification-output/program1.log
```

Repeat with program2, program3 and program4. JDK source-file launch avoids a build framework. The tested environment used Python 3.11 and JDK 24.0.2; the PATH java launcher was unusable, so the JDK executable was invoked directly. A successful trace process only means simulation completed; inspect states against the intended results above.

[Program 1 trace](traces/program1.csv), [program 2](traces/program2.csv), [program 3](traces/program3.csv), and [program 4](traces/program4.csv) contain measured snapshots for half-ticks 0..25 plus 120. PC/register/RA cells are hexadecimal; U marks unknown bits. RAM columns are decimal. Odd half-ticks are rising edges. Full 121-snapshot traces are reproducible with the command above. No oscillation was reported in these bounded runs.

## Unresolved comparison

The original manual observations and later automated traces have not been reconciled. [GUI observation notes](screenshots.md) identify views useful for a comparison. No functional repairs or new GUI-success claims are made here. Joint-work publication and licensing rights remain separate from technical validation.
