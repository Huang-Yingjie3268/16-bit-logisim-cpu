"""Independent encoding, byte-order and input-validation checks."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/generate_memory.py"
spec = importlib.util.spec_from_file_location("generate_memory", SCRIPT)
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)
OPCODES = dict(zip("li addi andi ori add and or move load store ble bne jump call rtn halt".split(), range(16)))

def assemble_annotation(instruction):
    tokens = instruction.replace(",", " ").split()
    op = OPCODES[tokens[0]]
    values = [int(x[1:]) - 1 if x.startswith("r") else int(x) for x in tokens[1:]]
    word = op << 12
    if op in (4, 5, 6):
        d, s, t = values
        return word | (s << 7) | (t << 4) | (d << 1)
    if op in (12, 13):
        return word | (values[0] & 0xFFF)
    if op in (14, 15):
        return word
    if op == 0:
        d, immediate = values
        return word | (d << 9) | (immediate & 63)
    if op == 9:  # source value, address register
        source, address = values
        return word | (address << 9) | (source << 6)
    d, s = values[:2]
    return word | (d << 9) | (s << 6) | ((values[2] & 63) if len(values) == 3 else 0)

class MemoryConversionTests(unittest.TestCase):
    def test_all_examples_agree_with_hex_and_annotations(self):
        for n, count in enumerate((6, 5, 11, 12), 1):
            with self.subTest(program=n):
                folder = ROOT / "examples" / f"program{n}"
                words = converter.parse_instructions((folder / "machine_code.txt").read_text())
                tokens = (folder / "memory_image.txt").read_text().split()
                self.assertEqual(tokens[:2], ["v2.0", "raw"])
                hex_words = [int(t, 16) for t in tokens[2:]]
                self.assertEqual(len(words), count)
                self.assertEqual(words, hex_words)
                instructions = [l.split(";")[0].strip() for l in (folder / "program.asm").read_text().splitlines()]
                self.assertEqual([assemble_annotation(l) for l in instructions if l], words)
                binary = converter.encode_memory(words)
                self.assertEqual(binary, bytes.fromhex("".join(f"{w:04x}" for w in hex_words)))
                text = converter.encode_memory(words, "logisim").decode().split()
                self.assertEqual([int(t, 16) for t in text[2:]], words)

    def test_original_whitespace_and_big_endian(self):
        self.assertEqual(converter.parse_instructions("\n1010 001010111111  \n"), [0xA2BF])
        self.assertEqual(converter.encode_memory([0x1234, 0xABCD]), b"\x12\x34\xab\xcd")

    def test_invalid_inputs(self):
        for text in ("", "  \n", "0" * 15, "0" * 17, "0" * 15 + "2", "0000000000000001 # comment"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                converter.parse_instructions(text)
        with self.assertRaisesRegex(ValueError, "line 2"):
            converter.parse_instructions("0" * 16 + "\n" + "1" * 15)

    def test_cli_does_not_overwrite_on_invalid_input(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp); source = folder / "input.txt"; output = folder / "memory.bin"
            source.write_text("0101"); output.write_bytes(b"keep")
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--output", str(output)], capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(output.read_bytes(), b"keep")
            self.assertIn(b"line 1", result.stderr)

    def test_cli_same_path_and_missing_input(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.txt"; source.write_text("0" * 16)
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--output", str(source)], capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(source.read_text(), "0" * 16)
            missing = source.with_name("missing.txt")
            result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(missing), "--output", str(source)], capture_output=True)
            self.assertEqual(result.returncode, 1)

if __name__ == "__main__":
    unittest.main()
