# autolecture-claude-skill

Claude Code skill that turns a script / audio recording / podcast
(optionally + a PDF or GitHub repo) into a finished
[AutoLecture](https://autolecture.ai) video. End-to-end: generate the
project, upload it via the [Python SDK](https://github.com/scao7/autolecture-python),
compile, download the mp4.

## Install (3 steps)

```bash
# 1. Drop the skill into ~/.claude/skills/
git clone https://github.com/scao7/autolecture-claude-skill.git ~/.claude/skills/autolecture-claude-skill

# 2. Install the SDK + a few helper deps
#    (the SDK isn't on PyPI yet — install straight from GitHub for now)
pip install git+https://github.com/scao7/autolecture-python.git
pip install openai-whisper pdfplumber Pillow
#    (also need on PATH: ffmpeg, pdftoppm, git — system packages)

# 3. Mint an API key. The Account-page UI isn't wired yet, so for the
#    bootstrap user, sign in at https://autolecture.ai and run:
#
#      curl -X POST -H "Authorization: Bearer <YOUR_JWT_FROM_BROWSER>" \
#        https://autolecture.ai/api/v2/me/api-key
#
#    (Grab the JWT from devtools → Application → localStorage → al_token.)
#    Copy the `api_key` field of the response — it's only shown once.
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
