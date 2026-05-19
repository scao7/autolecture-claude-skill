#!/usr/bin/env python3
"""Transcribe an audio file to Whisper sidecar JSON.

Usage:
    python3 transcribe.py --audio <path> --out <sidecar.json>
    python3 transcribe.py --audio recording.m4a --model base --language zh

Output schema matches AutoLecture's `.whisper.json` sidecar:
{
    "duration_sec": float,
    "language": str,
    "words": [
        {"text": str, "start": float, "end": float},
        ...
    ],
}

Requirements:
    pip install openai-whisper      (or use conda env that has it)
    ffmpeg available on PATH
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _deps import require_system, require_pip  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", required=True, help="path to audio file (mp3/m4a/wav)")
    p.add_argument("--out", help="output JSON path; default: <audio>.whisper.json")
    p.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"])
    p.add_argument("--language", default="zh", help="ISO 639-1 code; zh / en / etc.")
    args = p.parse_args()

    audio = Path(args.audio).resolve()
    if not audio.is_file():
        sys.exit(f"audio not found: {audio}")

    out_path = Path(args.out) if args.out else audio.with_suffix(audio.suffix + ".whisper.json")

    require_system("ffmpeg", apt="ffmpeg", brew="ffmpeg",
                   dnf="ffmpeg", pacman="ffmpeg",
                   note="audio decoding for Whisper")
    require_pip("whisper", package="openai-whisper",
                note="ASR — turns audio into word-timestamped transcript")
    import whisper

    print(f"loading whisper model: {args.model}")
    model = whisper.load_model(args.model)

    print(f"transcribing {audio.name} (language={args.language}, word_timestamps=True)")
    result = model.transcribe(
        str(audio),
        language=args.language,
        word_timestamps=True,
        fp16=False,
    )

    # Flatten segments → word list
    words = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []) or []:
            # whisper returns 'word' with leading space; .strip() removes it
            text = (w.get("word") or "").strip() or (w.get("text") or "").strip()
            if not text:
                continue
            words.append({
                "text": text,
                "start": float(w["start"]),
                "end": float(w["end"]),
            })

    # Duration: prefer last word end, fall back to ffprobe
    duration = words[-1]["end"] if words else 0.0
    if duration == 0.0:
        try:
            import subprocess
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(audio)],
                capture_output=True, text=True,
            )
            duration = float(r.stdout.strip())
        except Exception:
            pass

    sidecar = {
        "duration_sec": duration,
        "language": result.get("language", args.language),
        "words": words,
        "text": result.get("text", "").strip(),
    }
    out_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}  (duration={duration:.2f}s · words={len(words)})")


if __name__ == "__main__":
    main()
