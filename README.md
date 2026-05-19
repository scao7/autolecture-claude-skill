# autolecture-claude-skill

Claude Code skill that turns a script / audio recording / podcast
(optionally + a PDF or GitHub repo) into a finished
[AutoLecture](https://autolecture.ai) video. End-to-end: generate the
project, upload it via the [Python SDK](https://github.com/scao7/autolecture-python),
compile, download the mp4.

## Install (3 steps)

```bash
# 1. Drop the skill into ~/.claude/skills/
#    If you used the predecessor scao7/autolecture-skill (folder name
#    "autolecture-demo"), remove it first to avoid two copies loading:
#       rm -rf ~/.claude/skills/autolecture-demo
git clone https://github.com/scao7/autolecture-claude-skill.git ~/.claude/skills/autolecture-claude-skill

# 2. Install the SDK + a few helper deps
#    (the SDK isn't on PyPI yet — install straight from GitHub for now)
pip install git+https://github.com/scao7/autolecture-python.git
pip install openai-whisper pdfplumber Pillow
#    (also need on PATH: ffmpeg, pdftoppm, git — system packages)

# 3. Mint an API key at https://autolecture.ai/account → 🔑 API Keys
#    → "Generate API key". Copy immediately — shown ONCE.
export AUTOLECTURE_API_KEY='al_live_…'
```

## Use

Open Claude Code anywhere, attach your input file, and ask:

> "做个 autolecture demo" `--include recording.mp3`
>
> "Make me an explainer video from this paper." `--include paper.pdf`

Claude reads `SKILL.md`, generates scenes, runs
`scripts/upload_and_compile.py`, and prints `out.mp4` + a Studio URL
when it's done.

## License

MIT
