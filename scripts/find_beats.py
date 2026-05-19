#!/usr/bin/env python3
"""Locate narrative beats in a Whisper sidecar by anchor-phrase search.

Workflow:
    1. You read the transcript and pick N "anchor phrases" — short verbatim
       substrings (5-15 chars) that uniquely mark the start of each scene.
    2. This script searches each anchor in the transcript's concatenated text,
       maps the character position back to the word index, and outputs the
       first word's `start` time. End time = next beat's start.
    3. Output: JSON list of {idx, anchor, headline, start, end, dur}, ready
       to feed into your .tex generation step (paste start/end into
       `\\audio[start=,end=]{}` opts).

The anchors must exist verbatim in the Whisper transcript (typos included).
The headlines are what you display in the visual — those can use the
corrected text from transcript_corrections.md.

Usage:
    python3 find_beats.py --whisper <path.json> --anchors anchors.json
    python3 find_beats.py --whisper recording.m4a.whisper.json --anchors my_beats.json --out beats.json

Anchors file format (JSON):
    [
        {"anchor": "如果你把", "headline": "几十亿参数 → AI 还能推导物理吗？"},
        {"anchor": "这听起来真的像是在开玩笑", "headline": "天方夜谭"},
        ...
    ]
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--whisper", required=True, help="Whisper sidecar JSON path")
    p.add_argument("--anchors", required=True, help="anchors JSON: list of {anchor, headline}")
    p.add_argument("--out", help="output beats JSON; default: print to stdout")
    args = p.parse_args()

    sidecar = json.loads(Path(args.whisper).read_text(encoding="utf-8"))
    anchors = json.loads(Path(args.anchors).read_text(encoding="utf-8"))
    if not isinstance(anchors, list):
        sys.exit("anchors must be a JSON list of {anchor, headline} objects")

    words = sidecar.get("words", [])
    duration = sidecar.get("duration_sec", 0.0)
    if not words:
        sys.exit("Whisper sidecar has no words[] — check the file")

    # Concat words into one string, record char→word index map
    text = ""
    char_to_word = []
    for wi, w in enumerate(words):
        for ch in w.get("text", ""):
            char_to_word.append(wi)
        text += w.get("text", "")

    beats = []
    cursor = 0
    for i, item in enumerate(anchors):
        anchor = item.get("anchor", "")
        headline = item.get("headline", anchor)
        if not anchor:
            print(f"!! beat {i+1}: missing anchor, skipping", file=sys.stderr)
            continue
        pos = text.find(anchor, cursor)
        if pos < 0:
            # try from start (handles out-of-order anchors)
            pos = text.find(anchor)
        if pos < 0:
            print(f"!! beat {i+1}: anchor not found in transcript: {anchor!r}", file=sys.stderr)
            continue
        word_idx = char_to_word[pos]
        start = words[word_idx]["start"]
        beats.append({
            "idx": len(beats) + 1,
            "anchor": anchor,
            "headline": headline,
            "start": round(start, 2),
        })
        cursor = pos + len(anchor)

    # Fill in end times
    for i, b in enumerate(beats):
        b["end"] = round(beats[i + 1]["start"] if i + 1 < len(beats) else duration, 2)
        b["dur"] = round(b["end"] - b["start"], 2)

    # Output
    if args.out:
        Path(args.out).write_text(json.dumps(beats, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.out}  ({len(beats)} beats)", file=sys.stderr)

    print(f"{'#':>3} {'start':>8} {'end':>8} {'dur':>6}  headline")
    print("-" * 80)
    for b in beats:
        print(f"{b['idx']:>3} {b['start']:>8.2f} {b['end']:>8.2f} {b['dur']:>6.2f}  {b['headline']}")


if __name__ == "__main__":
    main()
