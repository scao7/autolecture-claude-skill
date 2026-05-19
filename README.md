# autolecture-claude-skill

A [Claude Code skill](https://docs.claude.com/claude-code/skills) that
turns a script / audio recording / podcast into a render-ready
[AutoLecture](https://autolecture.ai) project — hand-written
`\manimFile` / `\htmlFile` / `\remotionFile` source for every scene,
real PDF / GitHub repo figures matched to narration beats, and
end-to-end upload + compile via the
[`autolecture` Python SDK](https://github.com/scao7/autolecture-python).

The skill replaces the previous "ask the user to drag a zip to
autolecture.ai" loop: the final step now uses the SDK to upload, kick
off a compile, and download the finished mp4 — Claude prints the
Studio URL when it's done.

## Install

```bash
# 1. Drop the skill into your ~/.claude/skills/ directory.
git clone https://github.com/scao7/autolecture-claude-skill.git
cp -r autolecture-claude-skill ~/.claude/skills/autolecture-demo

# 2. Install the SDK + a couple of scripts' system deps.
pip install autolecture openai-whisper pdfplumber Pillow
# (ffmpeg, pdftoppm, git must also be on PATH — system packages.)

# 3. Mint an AutoLecture API key at https://autolecture.ai/account
#    (open the page, find "API Keys", click Generate, copy ONCE).
export AUTOLECTURE_API_KEY='al_live_…'
```

The skill folder name (`autolecture-demo`) is the trigger phrase
Claude Code searches for; rename if you'd rather invoke it as
`/my-skill-name`.

## How to use

In any Claude Code session, just describe what you want:

> "我有一段 90 秒的语音介绍二分查找,做个 demo." `--include recording.mp3`
>
> "Make me an explainer video from this PDF paper." `--include paper.pdf`
>
> "I have a GitHub repo at github.com/foo/bar — make a demo of how to use it."

Claude will:

1. Pick the right input mode (`rough` audio / `polished` podcast /
   `text`-only script) per `SKILL.md`.
2. Generate scenes — hand-written Manim / HTML / Remotion source per
   beat, no LLM-codegen macros (per the skill's HARD BANS).
3. Optionally match PDF figures / GitHub screenshots to specific
   beats with anchor sentences.
4. Run `scripts/upload_and_compile.py` to ship the project to
   AutoLecture, compile it, and download the final mp4 to the
   work-dir.

The result is `out.mp4` next to the work-dir plus a Studio URL Claude
will print so you can open the project in the web UI for further
tweaking.

## What's in this repo

```
autolecture-claude-skill/
  SKILL.md                  authoritative skill spec (steps 1-10, HARD BANS, examples)
  scripts/
    transcribe.py             Whisper word-level ASR
    find_beats.py             locate narrative beats via anchor-phrase grep
    extract_pdf_figures.py    pdftoppm + pdfplumber figure crops
    clone_github_assets.py    sparse-checkout GitHub repo images
    package_zip.py            (optional) bundle the work-dir as a zip
    upload_and_compile.py     SDK-driven upload → compile → download
    _deps.py                  shared dependency-checking helpers
  templates/                  6 .tpl files (main.tex, README, scene skeletons)
  reference/                  5 .md docs Claude consults (palette, engine routing, …)
  examples/                   empty by curation rule (human-only, no AI samples)
  README.md / LICENSE / .gitignore
```

## Skill philosophy

`SKILL.md` is the authoritative spec — read it once if you're using
or extending the skill. The HARD BANS (no LLM-codegen macros, no
"96-card template" reuse, no silent fallbacks) reflect lessons from
real demos that didn't ship; respect them.

The skill is intentionally non-degrading: missing system deps
(ffmpeg, pdftoppm, …) hard-exit with install instructions rather than
producing a half-baked output.

## License

MIT — see [LICENSE](LICENSE).

## Links

- AutoLecture web app — <https://autolecture.ai>
- Python SDK — <https://github.com/scao7/autolecture-python>
- AutoLecture backend — <https://github.com/scao7/autolecture>
- DSL reference — <https://autolecture.ai/docs/dsl>
- Claude Code skills docs — <https://docs.claude.com/claude-code/skills>
