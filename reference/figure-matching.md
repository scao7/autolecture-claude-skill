# 把素材 match 到音频 beat

抽到的图（PDF page / figure / repo screenshot）怎么对应到 transcript 的哪一段 — 锚句规则 + 设计建议。

## 通用原则

**每张被用上的图都要有锚句证据**。写到 `beat_plan.md` 里：

```markdown
| 图 | match 到 beat | anchor 证据（transcript 原句） |
|---|---|---|
| `figures/fig-3.png` | beat 7 (collapse) | "如图 3 所示，所有向量都坍塌到同一点" |
```

没找到锚句 → **不要用**。宁愿一段画面没有图，也不要凭"这段差不多是讲这个"瞎塞。

---

## PDF 论文的 anchor 规则

**默认只用 figure crop** — `extract_pdf_figures.py` 默认 figures-only。整页栅格只在显式做「文字 highlight」时才出（`--with-pages` 开关）。

### 强匹配（直接用 figure）

| transcript 出现 | 匹配到 |
|---|---|
| "图 1 / 图 2 / 图 3" | `fig-1.png` / `fig-2.png` / ...（按 manifest 里检测顺序编号） |
| "Figure 1 / Fig. 2" | 同上（中英混录场景） |
| "如图所示 / 上图 / 下图" | 上下文最近的 figure（look-back/forward in beats） |
| 论文 caption 文字片段出现 | "Loss landscape 这个图" 匹配 caption 包含 "loss landscape" 的 figure |

### 文字 highlight 场景（需要 `--with-pages`）

下面这些场景**才**需要整页栅格 — 单 figure 不够用。规划时显式标注 `[needs-page]`，重跑 `extract_pdf_figures.py --with-pages`：

| transcript 场景 | 整页用法 |
|---|---|
| "我们看公式 (3) 这一段" | 整页 + zoom 到公式区域 + 红框 annotate |
| "原文里这段说..." 引用一段文字 | 整页 + highlight 那段文字的 bounding box |
| 论文 abstract / introduction 整段朗读 | 整页 slow scroll |
| 章节首页作为分割卡 | 整页作 chapter divider 静态展示 |

### 不匹配（不强加图）

- 整段在讲宏观叙事 / 哲学 / 致谢 → 用纯 Remotion/HTML scene
- 没有任何 figure-relevant 锚句 → 不强加图

---

## GitHub repo 的 anchor 规则

### 强匹配

| transcript 出现 | 匹配到 |
|---|---|
| README 里出现过的标题 / 段落 | 那一节 README 引用的图（看 `manifest.json::readme_refs`） |
| 截图标题 / alt 文本 | "我们打开设置页" → 匹配 alt="Settings page" 的图 |
| 模块名 / 文件名 | "看 dashboard 这个组件" → 匹配 `dashboard.png` 或 `docs/dashboard/*` 路径下的图 |
| 命令 / 终端输出 | 匹配 terminal screenshot（如有） |

### 弱匹配

| transcript 出现 | hint |
|---|---|
| logo / brand 名 | 仅在开头介绍段 / 结尾感谢段使用 logo |
| "demo" / "演示" | 用 README 头部 hero 截图 |

---

## 视觉效果决策

按图的内容和 beat 节奏选效果（避免裸铺图，禁止全部用同一种）：

| 场景 | 推荐效果 | 实现位置 |
|---|---|---|
| 论文 figure，单图，重点是某个区域 | **Crop + Ken Burns zoom-in**（focal point 慢推） | `scene_image_zoom.tsx.tpl` |
| 论文 figure，整图都重要（架构图、流程图） | **Ken Burns slow pan**（左到右扫一遍） | 同上，调参数 |
| 两张图对比（before / after） | **Side-by-side**，错位入场 | HTML grid |
| repo 截图，需要指出某个 UI 元素 | **Annotate overlay**（红框 + 箭头 + 文字标签） | Remotion，`<svg>` 在图上方 |
| repo 多张截图，连续 walkthrough | **Card transition**，淡入下一张 | HTML keyframe |
| 配 logo 出场 | **Pop + scale up**（弹簧） | Remotion `spring` |
| 论文公式 page (`--with-pages`) | **Page 滚动**（translateY），到公式停 + 红框 highlight 公式 | Remotion 手写 |
| 论文一段文字引用 (`--with-pages`) | **Highlight rect**：整页 dim 到 50%，文字 bbox 处保留 100% 亮度 | Remotion `<svg mask>` |

### Ken Burns 参数建议

10s scene + 1280×720 canvas 用：
- start: `scale(1.0) translate(0,0)`
- end:   `scale(1.15) translate(-40px, -20px)` (subtle drift toward focal point)
- easing: `easeOutQuart` (50% 进度时已完成 70% 动画 — 给观众缓冲看清楚)

公式 zoom 用：
- start: 整页可见
- mid (t=2s): zoom 4× to formula region
- hold mid 6s (让用户读)
- end (t=10s): 微微 zoom 5× 强调

### Annotate 模式

红框 + 箭头 + 标签建议在 figure 上方画一个 `<svg>` 绝对定位层。三色调色板：
- `#ee6c4d` (warn) — 主标注
- `#6ec1e4` (accent) — 次标注  
- `#f4d35e` (highlight) — 引导线

---

## 不带音频锚句但想用图的场景

少数情况：用户给了图但音频里没明确提及 — 比如 logo 出场、章节封面页。这时候允许使用，但**必须**标记 `[no anchor — decorative]` 在 `beat_plan.md` 里，且只能用于：

- 开场片头（logo / paper title page）
- 章节分割卡（论文 section header page）
- 收尾致谢（合作者照片等）

正文叙述段坚决不允许"凭感觉塞图"。
