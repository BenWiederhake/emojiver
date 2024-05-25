#!/usr/bin/env python3

import json

VERSION_MAJOR = "😂"

assert len(VERSION_MAJOR) == 1


def resolve(entry):
    if "l" in entry and "s" in entry:
        s_expected = "".join(chr(cp) for cp in entry["l"])
        assert s_expected == entry["s"]
        return entry["s"]
    if "l" in entry:
        return [chr(cp) for cp in entry["l"]]
    if "s" in entry:
        return entry["s"]
    raise AssertionError("missing data: entry has neither 's'(tring) nor 'l'(ist of codepoints)?!")


def encounter(by_first_codepoint, sequence):
    first_codepoint = sequence[0]
    assert first_codepoint not in by_first_codepoint, f"conflict: >>{sequence}<< and >>{by_first_codepoint[first_codepoint]}<<"
    by_first_codepoint[first_codepoint] = sequence


def extract_sequences(entries):
    # Input examples:
    # {"type": "or", "e_ver": "0.6", "l": [128017, 128018], "s": "🐑🐒"},
    #  => Two code points, two version numbers with one codepoint each
    # {"type": "and", "e_ver": "0.6", "l": [9851, 65039], "s": "♻️"},
    #  => Two code points, one version number (which is two codepoints long)
    by_first_codepoint = dict()
    sequences = []
    for i, entry in enumerate(entries):
        codepoints = resolve(entry)
        if entry["type"] == "or":
            for cp in codepoints:
                sequence = cp
                encounter(by_first_codepoint, sequence)
                sequences.append(sequence)
        elif entry["type"] == "and":
            sequence = codepoints
            encounter(by_first_codepoint, sequence)
            sequences.append(sequence)
        else:
            raise AssertionError(f"Invalid type: >>{entry['type']}<<")
    return sequences


def extract_emojis(decided_sequences):
    type_expected = "emojiver_expanded_v" + VERSION_MAJOR
    assert decided_sequences["type"] == type_expected, f"expected filetype {type_expected}, but was >>{decided_sequences['type']}<<"
    version = VERSION_MAJOR + decided_sequences["version_minor_and_patch"]
    assert len(version) == 3, "version must have exactly three emojis"
    return version, extract_sequences(decided_sequences["entries"])


def run():
    with open("emoji-sequences-decided.json", "r") as fp:
        decided_sequences = json.load(fp)
    version, emojis = extract_emojis(decided_sequences)
    data = {
        "type": "emojiver" + VERSION_MAJOR,
        "full_version": version,
        "order": emojis,
    }
    with open("emojiver_order.json", "w") as fp:
        json.dump(data, fp)


if __name__ == "__main__":
    run()
