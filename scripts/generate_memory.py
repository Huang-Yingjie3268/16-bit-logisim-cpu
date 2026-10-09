#!/usr/bin/env python3
"""Convert 16-bit binary instructions to big-endian bytes or Logisim hex words."""
import argparse
from pathlib import Path
import re
import sys

def parse_instructions(text: str) -> list[int]:
    words = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        bits = re.sub(r"\s+", "", line)
        if re.fullmatch(r"[01]{16}", bits) is None:
            raise ValueError(f"line {line_number}: expected exactly 16 binary digits")
        words.append(int(bits, 2))
    if not words:
        raise ValueError("input contains no instructions")
    return words

def encode_memory(words: list[int], output_format: str = "binary") -> bytes:
    if any(not 0 <= w <= 0xFFFF for w in words):
        raise ValueError("instruction outside the 16-bit range")
    if output_format == "binary":
        return b"".join(w.to_bytes(2, byteorder="big") for w in words)
    if output_format == "logisim":
        return ("v2.0 raw\n" + "\n".join(f"{w:04x}" for w in words) + "\n").encode("ascii")
    raise ValueError(f"unknown output format: {output_format}")

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--format", choices=("binary", "logisim"), default="binary")
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("input and output paths must be different")
        words = parse_instructions(args.input.read_text(encoding="utf-8-sig"))
        data = encode_memory(words, args.format)
        args.output.write_bytes(data)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {len(words)} words as {args.format}: {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
