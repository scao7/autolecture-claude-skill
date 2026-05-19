// Scene NN — <HEADLINE>  (~<EST_DURATION>s, but audio drives actual length)
//
// AUDIO-FIRST TIMING — load-bearing.
// All animations are expressed as fractions of `dur` (live duration from
// the Player config), NOT as hardcoded frame numbers. Compiler overrides
// the exported DURATION_FRAMES to match the audio at render time; the
// component re-reads via useVideoConfig() so EVERY animation auto-stretches.
//
// What this means in practice:
//   ❌ interpolate(frame, [0, 30], [0, 1])           ← bad: ends at 1s regardless of audio
//   ✅ interpolate(frame, [0, dur * 0.1], [0, 1])    ← good: ends at 10% of actual duration
import React from 'react';
import {
  AbsoluteFill, useCurrentFrame, useVideoConfig,
  interpolate, spring,
} from 'remotion';

export const FPS = 30;
export const WIDTH = 1280;
export const HEIGHT = 720;
// Author estimate; compiler will override at render time to match audio.
// Pick a number that lets you preview while writing — 10s @ 30fps = 300.
export const DURATION_FRAMES = 10 * FPS;

const C = {
  bg: '#0d1117',
  fg: '#ffffff',
  accent: '#6ec1e4',
  highlight: '#f4d35e',
  warn: '#ee6c4d',
  mint: '#4ec9b0',
  dim: '#5a6273',
  sub: '#aab1c0',
};

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames: dur } = useVideoConfig();

  // ── Phase boundaries as FRACTIONS of `dur` ───────────────────────
  // Whole component stretches with audio: short audio = quick reveal,
  // long audio = slower paced reveal. Stays readable at either extreme.
  const IN_END    = dur * 0.10;    // kicker fades in by 10% of scene
  const TITLE_END = dur * 0.20;    // headline lands by 20%
  const ACCENT    = dur * 0.85;    // optional outro accent starts at 85%

  const kickerOp = interpolate(frame, [0, IN_END], [0, 1], { extrapolateRight: 'clamp' });

  // Spring still uses fps (correct — it's a physical motion), but the
  // frame offset is fraction-of-duration so the bounce timing scales.
  const titleSpring = spring({
    frame: frame - IN_END,
    fps,
    config: { damping: 14 },
    durationInFrames: TITLE_END - IN_END,
  });
  const titleOp = interpolate(titleSpring, [0, 1], [0, 1]);
  const titleY  = interpolate(titleSpring, [0, 1], [30, 0]);

  // Late-scene accent (e.g., final-state highlight) — fires near the end.
  const accentOp = interpolate(frame, [ACCENT, dur], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg,
        fontFamily: 'Inter, system-ui, "PingFang SC", sans-serif',
        alignItems: 'center', justifyContent: 'center',
        padding: 80,
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <div style={{
          opacity: kickerOp,
          fontSize: 14, letterSpacing: 6,
          color: C.accent, textTransform: 'uppercase',
          marginBottom: 14,
        }}>
          KICKER
        </div>
        <div style={{
          opacity: titleOp,
          transform: `translateY(${titleY}px)`,
          fontSize: 72, fontWeight: 800, color: C.fg, letterSpacing: -1.5,
        }}>
          标题文字 <span style={{ color: C.accent }}>关键词</span>
        </div>
        <div style={{
          marginTop: 22,
          fontSize: 18, color: C.sub,
          opacity: accentOp,
          letterSpacing: 1,
        }}>
          (outro accent — appears in the last 15% of the scene)
        </div>
      </div>
    </AbsoluteFill>
  );
};
