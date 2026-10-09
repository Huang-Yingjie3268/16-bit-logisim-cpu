# Coursework source notes

The earlier course archive contained 16 files and four directory entries; this is distinct from the organized project ZIP. Every original file is retained in an independent local backup outside this repository, including a copy of the input ZIP and its extracted project. The original course ZIP is untouched. Unfiltered extracts and internal logs are not included in this repository.

| Original file(s) | Classification | Public decision |
| --- | --- | --- |
| `Coursework4.circ` | Essential source | Retain byte-for-byte as `cpu/simple_16bit_cpu.circ`; six circuits and embedded program 4 preserved. |
| `Four_Memory_Image_File/Binary_Machine_Code/Mem-1.txt` through `Mem-4.txt` | Required test inputs | Retain as each example's `machine_code.txt`; normalize whitespace only. Program 1 contains an internal space and program 2 trailing spaces. Words/order unchanged. |
| `Four_Memory_Image_File/Executable_Image_File(Hex)/Mem-1(Executable hex).txt` through `Mem-4(Executable hex).txt` | Required execution assets | Retain byte-for-byte as each example's `memory_image.txt`; preserve `v2.0 raw`. |
| `Mem-1.bin` through `Mem-4.bin` | Redundant generated output | Archive privately; omit publicly because all four are reproducible byte-for-byte and the circuit does not reference them. |
| `gen_bin.py` | Overlapping utility | Archive privately; program 1 generation merged into configurable converter. |
| `gen_bin234.py` | Overlapping utility | Archive privately; despite its name generates all four programs. Consolidate as `scripts/generate_memory.py`. |
| `HW-4-answersheet.docx` | Useful private reference; sensitive/unsuitable coursework | Exclude publicly. Used for mnemonic/intention/contribution cross-checks; contains student identifiers and emails. Conflicting R-type table rows are superseded by the circuit. |

No other files, temporary documents or screenshots were present in that earlier course archive. Directory names have been replaced by examples/program1 through program4. Nothing was deleted from the input or private backup.

## New artifacts

README; architecture and ISA documentation; this report; verification report; manual screenshot guidance; four reconstructed assembly annotations; consolidated Python converter; focused conversion/encoding checks; and a bounded Java circuit trace utility. Assembly is descriptive, not original source or assembler input. No license, simulator JAR, personal information, answer-sheet copy, audit extract or empty image files are included.

## Suggested GitHub metadata

Name: `16-bit-logisim-cpu`

Description: Educational 16-bit CPU in Logisim Evolution with a custom ISA, register file, memory images, and four demonstration programs.

Topics: `computer-architecture`, `digital-logic`, `cpu-design`, `logisim`, `instruction-set-architecture`.

The description summarizes the educational design; unresolved test differences are described separately. No repository was published or remote configured. Joint-work licensing requires appropriate authorization.
