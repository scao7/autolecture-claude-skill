# {{PROJECT_TITLE}} —— AutoLecture 项目包

## 怎么用

1. 上 [https://autolecture.ai](https://autolecture.ai) 新建一个空白项目
2. 把这个目录里所有文件拖进项目的 `assets/`（或者用 zip 上传功能一次性传）
3. 把 `{{PROJECT_FILE}}` 设为主 tex（编辑器顶部切换），或在 `main.tex` 里 `\input{{{PROJECT_FILE}}}`
4. 点 ▶ Recompile all

预期编译时长：约 {{COMPILE_ETA}} 分钟（缓存命中后 ~1-2 分钟）。

## 包含什么

- `{{PROJECT_FILE}}` —— 主 tex
- `scenes/` —— {{N_SCENES}} 个手写的视觉源码
  - `.tsx` 是 Remotion React 组件
  - `.html` 是 Playwright 录屏的网页
  - `.py` 是 Manim Python 脚本
{{AUDIO_BLOCK}}
- `beat_plan.md` —— 叙事节拍 / 视觉路由记录（仅供参考）
- `transcript_corrections.md` —— 转录错字修正映射（如果有）

## 设计原则

- **手写源码**：所有视觉都是 `\manimFile{}` / `\htmlFile{}` / `\remotionFile{}` 引外部源码 — 不走 LLM 提示词，编译稳、调试简单。
- **统一调色板**：深底 `#0d1117`、accent `#6ec1e4`、highlight `#f4d35e`、warn `#ee6c4d`、dim `#aab1c0`
- **统一字体栈**：Inter + PingFang SC
- **统一动画语法**：fade-up / pop / strike / typewriter — 让 18 分钟视频感觉是一部片子

## 想改？

- 改某一段画面：直接编辑 `scenes/scene_NN_*.<ext>` 然后点 ↻ Re-render（只重渲这一个 view）
- 改叙事顺序：调整 `{{PROJECT_FILE}}` 里 view 的顺序
- 加旁白：在 view 里加 `\say{...}`（rough/text 模式）或 `\audio[start=,end=]{}`（polished 模式）
- 改风格：编辑 preamble 里的 `\style{...}` 描述

## 调试

- 单个 view 编译失败 → 看 BlockCard 上的错误提示
- Manim 超时 → 简化场景或换用 Remotion（这个包里默认 70s+ 的复杂场景已经路由到 Remotion）
- HTML 渲染白屏 → 检查 `<style>` 内联是否完整，`<body>` 内容是否在 `.stage` 容器里

完整 DSL 语法见 [autolecture.ai/docs/dsl](https://autolecture.ai/docs/dsl)。
