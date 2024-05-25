#!/usr/bin/env python3

from typing import List
import collections

CHECKCOUNT_PREFIX = "# Total elements: "
VERSION_MAJOR = "😂"

Entry = collections.namedtuple("Entry", ["begin_or_sequence", "maybe_end_inclusive", "emoji_version"])

assert len(VERSION_MAJOR) == 1


def parse_entries(data: str) -> List[Entry]:
    entries: List[Entry] = []
    emojis_in_current_block = 0
    for i, line in enumerate(data.split("\n")):
        if not line:
            continue
        if line.startswith(CHECKCOUNT_PREFIX):
            expect = int(line[len(CHECKCOUNT_PREFIX):])
            assert expect == emojis_in_current_block, f"line #{i + 1}: file says this block contains {expect} emojis, but parsed only {emojis_in_current_block}?!"
            emojis_in_current_block = 0
            continue
        if line.startswith("#"):
            continue
        # '25FD..25FE    ; Basic_Emoji                  ; white medium-small square..black medium-small square           # E0.6   [2] (◽..◾)'
        parts = line.split(";")
        assert len(parts) == 3, f"expected data-line to contain three parts, but was {len(parts)}?! line #{i + 1}"
        range_ends = parts[0].rstrip().split("..")
        emoji_ver = parts[2].split("#")[1].lstrip().split(" ")[0]
        assert emoji_ver.startswith("E"), f"expected emoji version, found >>{emoji_ver}<< instead (did not start with 'E'), line #{i + 1}"
        emoji_ver = emoji_ver[1:]  # drop "E"
        if len(range_ends) == 2:
            entry = Entry(int(range_ends[0], 16), int(range_ends[1], 16), emoji_ver)
            emojis_in_current_block += entry.maybe_end_inclusive - entry.begin_or_sequence + 1
        else:
            assert len(range_ends) == 1, f"Range contains more than one '..', but {len(range_ends)}?! line #{i + 1}"
            codepoints_str = range_ends[0].split(" ")
            codepoints = [int(c, 16) for c in codepoints_str]
            entry = Entry(codepoints, None, emoji_ver)
            emojis_in_current_block += 1
        entries.append(entry)
    print(f"Finished parsing {len(entries)} entries.")
    return entries


def expand(entries: List[Entry]) -> str:
    # 'sorted()' is guaranteed to be stable.
    # "Surely emoji versions like 0.3 or 15.1 can be treated as floats, and there is no way this could ever go wrong!"
    entries_by_emojiver = sorted(entries, key=lambda e: float(e.emoji_version))
    parts: List[str] = []
    parts.append("{\n")
    parts.append("\"type\": \"emojiver_expanded_v")
    parts.append(VERSION_MAJOR)
    parts.append("\",\n")
    parts.append("\"entries\": [")
    emitted_entries = False
    for entry in entries_by_emojiver:
        if emitted_entries:
            parts.append(",\n")
        else:
            parts.append("\n")
            emitted_entries = True
        if isinstance(entry.begin_or_sequence, list):
            assert entry.maybe_end_inclusive is None
            typename = "and"
            codepoints = entry.begin_or_sequence
        elif isinstance(entry.begin_or_sequence, int):
            assert isinstance(entry.maybe_end_inclusive, int)
            typename = "or"
            codepoints = list(range(entry.begin_or_sequence, entry.maybe_end_inclusive + 1))
        else:
            raise AssertionError(type(entry.begin_or_sequence), entry)
        parts.append("{\"type\": \"")
        parts.append(typename)
        parts.append("\", \"e_ver\": \"")
        parts.append(entry.emoji_version)
        parts.append("\", \"l\": ")
        parts.append(str(codepoints))
        parts.append(", \"s\": \"")
        parts.append("".join(chr(cp) for cp in codepoints))
        parts.append("\"}")
    parts.append("\n]\n")
    parts.append("}\n")
    return "".join(parts)


def run():
    with open("emoji-sequences.txt", "r") as fp:
        data = fp.read()
    entries = parse_entries(data)
    expanded = expand(entries)
    with open("emoji-sequences-expanded.json", "w") as fp:
        fp.write(expanded)


if __name__ == "__main__":
    run()
