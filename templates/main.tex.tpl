% {{PROJECT_TITLE}} —— autolecture-claude-skill 生成
% Mode: {{MODE}}        (rough / polished / text)
% Source audio: {{AUDIO_FILE}}    (omit for text mode)
% Generated scenes: {{N_SCENES}}

\title{{{PROJECT_TITLE}}}
\aspect{16:9}
\style{{{STYLE_DESCRIPTION}}}

\begin{videotex}

% ──────────────── Example: text / rough mode (TTS) ────────────────
\begin{view}[title=Scene_01_Hook]
  \say{这里是这一段的旁白文字，TTS 会朗读。}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

% ──────────────── Example: polished mode (clip 原音频) ────────────
\begin{view}[title=Scene_02_Card]
  \audio[start=32.34, end=66.44]{{{AUDIO_FILE}}}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

% ──────────────── Example: Manim 数学 ─────────────────────────────
\begin{view}[title=Scene_03_Math]
  \audio[start=66.44, end=87.40]{{{AUDIO_FILE}}}
  \manimFile{scenes/scene_03_math.py}
\end{view}

% ──────────────── Example: AI image ───────────────────────────────
\begin{view}[title=Scene_04_Illustration]
  \say{这一段用 AI 生图配画面。}
  \image[engine=gemini]{a thoughtful person looking up at the sky,
                         hand-drawn watercolor with warm pastel palette}
\end{view}

% ──────────────── Example: 上传的图片 ──────────────────────────────
\begin{view}[title=Scene_05_Photo]
  \say{这是从相机里导入的照片。}
  \imageFile[fit=contain]{figures/photo_01.jpg}
\end{view}

\end{videotex}
