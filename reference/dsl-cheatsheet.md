# VideoTeX DSL 速查（autolecture-demo 用）

## 文档结构

```latex
\title{<title>}
\aspect{16:9}     % or 9:16 / 1:1
\style{<风格描述：注入 LLM system prompt + TTS instruct>}

\begin{videotex}
  \begin{view}[opts]
    ...layer 宏...
  \end{view}

  \fade[duration=0.5]{}   % 转场（可选）

  \begin{view}...\end{view}
\end{videotex}
```

## 视觉层宏（每个 view 一个）

| 宏 | 适用 | 备注 |
|---|---|---|
| `\manimFile{path.py}` | Manim Python 源码 | 类名默认 `LectureScene`。`scene=Name` 改类名。`engine=3b1b` 用 manimgl fork |
| `\htmlFile{path.html}` | HTML 源码 | Playwright 实时录屏；独立的内联 CSS |
| `\remotionFile{path.tsx}` | Remotion React 源码 | 必须导出 `Comp` / `FPS` / `WIDTH` / `HEIGHT` / `DURATION_FRAMES` |
| `\imageFile{path.png}` | 上传的图片 | opts: `fit / position / bg / lead` |
| `\image[engine=gemini]{prompt}` | AI 生图 | Gemini，单次生成，同 prompt+style 缓存命中 |
| `\video[start=,end=]{path.mp4}` | 上传的视频片段 | `mute / loop / fit` |

**禁用**：`\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}` / `\show{}` — LLM 出代码，不稳定。

## 音频层

| 宏 | 适用 |
|---|---|
| `\say{text}` | TTS 合成。opts: `voice=mine` / `speaker` / `speed` / `model` / `burn` / `as` |
| `\audio[start=N, end=N]{path.m4a}` | 剪辑原音频（不走 TTS、无自动字幕） |

## 字幕层

| 宏 | 适用 |
|---|---|
| `\text{...}` | 覆盖默认字幕。opts: `position=top|bottom|hidden` / `align=auto|on|off` |

省略时默认行为：`\say` 有 → 字幕用 `\say` 文字；`\audio` 单独用 → 无字幕。

## view-level opts

只有 2 个：`duration`（秒）+ `title`（编辑器显示名）。

## preamble-only 宏

`\title` / `\aspect` / `\style` / `\subtitle{on|off|auto}` / `\bgm[volume=,loop=]{path}` / `\character[voice=,speed=]{name}`。

## body 元素

`\begin{view}...\end{view}` / `\begin{segment}[title=,continuous=]...\end{segment}` / `\fade[duration=,color=]{}` / `\input{path.tex}`。

## 一个最小例子（手写源码模式）

```latex
\title{Hello AutoLecture}
\aspect{16:9}
\style{深色背景 #0d1117, Inter + PingFang SC, 简洁动画}

\begin{videotex}

\begin{view}[title=Hook]
  \say{今天我们来看看世界上最小的世界模型。}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

\begin{view}[title=Card]
  \say{15M 参数，2 个损失函数，48 倍加速。}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

\end{videotex}
```

## 一个 polished 模式例子（剪辑原音频）

```latex
\title{论文解读}
\aspect{16:9}
\style{学术深度解读, 深色背景, 高对比白字, Inter + PingFang SC}

\begin{videotex}

\begin{view}[title=Hook]
  \audio[start=0.00, end=32.34]{podcast.m4a}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

\begin{view}[title=Card]
  \audio[start=32.34, end=66.44]{podcast.m4a}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

\end{videotex}
```
