<!DOCTYPE html>
<!--
  Scene NN — <HEADLINE>  (~<EST_DURATION>s, audio drives actual length)

  AUDIO-FIRST TIMING — HTML can't read the live audio duration the way
  Remotion can, and the compiler doesn't rewrite CSS keyframes the way
  it AST-rewrites Manim. So the discipline is:

    1. **Short intro** (1.0-1.5s) — entrance animations finish quickly so
       the scene feels "live" even on a 2s audio cut.
    2. **Continuous motion in the residual** — at least one element keeps
       breathing (subtle pulse, slow drift, animated underline scan) so
       the rest of the scene isn't a frozen frame on long audio (>10s).
    3. **NEVER hardcode "this scene is 8s" in animation-delay chains.**
       If your reveal sequence runs `delay: 0s; 1s; 2s; 3s` and audio
       turns out 4s, the last item never appears — and the user has to
       re-author. Use short sequential delays (0.2s, 0.4s, 0.6s) then
       keep continuous motion.

  Compiler behavior: Playwright records this page for `target_duration`
  seconds. If target is 30s and your animations all finish by 3s, you
  get 27s of static frame. The continuous-motion pattern below prevents
  that.

  Use <style> inline. No external CSS/font fetches — Playwright is
  offline at record time and a missed @import will silently un-style.
-->
<html lang="zh">
<head>
<meta charset="UTF-8" />
<title>Scene NN</title>
<style>
  html, body {
    margin: 0; padding: 0; width: 100%; height: 100%;
    background: #0d1117; overflow: hidden;
    font-family: 'Inter', system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    color: #ffffff;
  }
  .stage {
    width: 100vw; height: 100vh;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 50px; box-sizing: border-box;
  }

  /* ─── Short-intro animations (finish in 1-1.5s) ──────────────── */
  .kicker {
    font-size: 14px; letter-spacing: 6px;
    color: #6ec1e4; text-transform: uppercase;
    opacity: 0; animation: in .5s ease-out forwards;
  }
  h1 {
    font-size: 56px; font-weight: 800;
    letter-spacing: -1px;
    margin: 12px 0 36px;
    opacity: 0;
    animation: in .6s ease-out .2s forwards;
  }
  h1 em { font-style: normal; color: #6ec1e4; }

  .grid {
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 28px; width: 100%; max-width: 1100px;
  }
  .card {
    padding: 28px 24px;
    border: 1px solid #2a2f3a; border-radius: 12px;
    background: rgba(255,255,255,0.02);
    opacity: 0; transform: translateY(20px);
  }
  /* Sequential reveal, all done within 1.5s — keeps short-audio cuts coherent */
  .card.c1 { animation: in .5s ease-out .6s forwards; }
  .card.c2 { animation: in .5s ease-out .9s forwards; }
  .card.c3 { animation: in .5s ease-out 1.2s forwards; }

  .num {
    font-size: 64px; font-weight: 800;
    letter-spacing: -2px; line-height: 1;
  }
  .c1 .num { color: #6ec1e4; }
  .c2 .num { color: #f4d35e; }
  .c3 .num { color: #ee6c4d; }

  .label {
    font-size: 13px; letter-spacing: 3px; color: #888;
    text-transform: uppercase; margin-top: 12px;
  }
  .desc {
    margin-top: 8px; font-size: 16px;
    color: #c4cad8; line-height: 1.45;
  }

  /* ─── Continuous motion (runs forever; prevents frozen-frame on long audio) ─── */
  .accent-pulse {
    color: #6ec1e4;
    animation: pulse 2.4s ease-in-out infinite;
  }
  .underline-scan {
    /* Slow horizontal sheen across the title — barely-there, but breathing */
    position: relative;
  }
  .underline-scan::after {
    content: '';
    position: absolute; left: 0; right: 0; bottom: -6px;
    height: 2px;
    background: linear-gradient(90deg,
      transparent, #6ec1e4 50%, transparent);
    background-size: 200% 100%;
    animation: scan 4s linear infinite;
  }

  @keyframes in    { to { opacity: 1; transform: translate(0); } }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.55; } }
  @keyframes scan  { 0% { background-position: 200% 0; }
                     100% { background-position: -200% 0; } }
</style>
</head>
<body>
<div class="stage">
  <div class="kicker">section name</div>
  <h1 class="underline-scan">
    主标题 <em class="accent-pulse">关键词</em>
  </h1>
  <div class="grid">
    <div class="card c1"><div class="num">15M</div><div class="label">参数</div><div class="desc">说明 1</div></div>
    <div class="card c2"><div class="num">2</div><div class="label">损失</div><div class="desc">说明 2</div></div>
    <div class="card c3"><div class="num">48×</div><div class="label">加速</div><div class="desc">说明 3</div></div>
  </div>
</div>
</body>
</html>
