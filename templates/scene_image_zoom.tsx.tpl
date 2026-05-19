// Scene NN — Ken Burns zoom-in on a figure (~<EST_DURATION>s, audio drives)
//
// AUDIO-FIRST TIMING — the Ken Burns drift uses `dur` from useVideoConfig
// so the figure pans the same FRACTION of its journey regardless of how
// long the audio for this beat is. Short audio = quick zoom; long audio =
// slow contemplative zoom. The image stays readable at either extreme.
//
// Three modes the same component supports — tune the props:
//   1. SLOW PAN  : scale 1.0 → 1.05, translate L→R (whole-figure scan)
//   2. ZOOM-IN   : scale 1.0 → 1.4, translate toward focal point
//   3. PAGE STAY : scale 1.0 → 1.0 (no movement) + caption banner on top
import React from 'react';
import {
  AbsoluteFill, Img, useCurrentFrame, useVideoConfig,
  interpolate, staticFile,
} from 'remotion';

export const FPS = 30;
export const WIDTH = 1280;
export const HEIGHT = 720;
// Author estimate; compiler will override at render time to match audio.
export const DURATION_FRAMES = 10 * FPS;

// ── Tunables ────────────────────────────────────────────────────────────
const SRC      = 'figures/fig-3.png';
const CAPTION  = 'Figure 3 · Representation collapse in latent space';
const ZOOM_FROM = 1.00;
const ZOOM_TO   = 1.18;
const FOCAL_X   = 0.50;   // 0..1 fraction across image width
const FOCAL_Y   = 0.55;   // 0..1 fraction down image height
const BG        = '#0d1117';

const C = {
  fg: '#ffffff', accent: '#6ec1e4', dim: '#aab1c0',
  banner: 'rgba(13,17,23,0.78)',
};

export const Comp: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames: dur } = useVideoConfig();

  // Normalized progress 0..1 across the actual rendered duration.
  // Ease-out-quart: most motion happens early, slow tail (gives viewer
  // time to read details once we've zoomed in).
  const t = Math.min(1, frame / dur);
  const easedT = 1 - Math.pow(1 - t, 4);

  const scale = interpolate(easedT, [0, 1], [ZOOM_FROM, ZOOM_TO]);
  const tx = (0.5 - FOCAL_X) * 120 * easedT;
  const ty = (0.5 - FOCAL_Y) * 120 * easedT;

  // Caption banner: slide down in the first 8% of the scene, hold rest.
  const BAN_IN_END = dur * 0.08;
  const banOp = interpolate(frame, [BAN_IN_END * 0.3, BAN_IN_END], [0, 1],
                             { extrapolateRight: 'clamp' });
  const banY  = interpolate(frame, [BAN_IN_END * 0.3, BAN_IN_END], [-30, 0],
                             { extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill style={{ background: BG, overflow: 'hidden' }}>
      <AbsoluteFill style={{
        alignItems: 'center', justifyContent: 'center',
        transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
        transformOrigin: `${FOCAL_X * 100}% ${FOCAL_Y * 100}%`,
      }}>
        <Img
          src={staticFile(SRC)}
          style={{ maxWidth: '92%', maxHeight: '92%', objectFit: 'contain' }}
        />
      </AbsoluteFill>

      {CAPTION && (
        <div style={{
          position: 'absolute',
          top: 40, left: 40, right: 40,
          opacity: banOp, transform: `translateY(${banY}px)`,
          background: C.banner, backdropFilter: 'blur(8px)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 10,
          padding: '14px 22px',
          fontFamily: 'Inter, system-ui, "PingFang SC", sans-serif',
          fontSize: 20, fontWeight: 600, color: C.fg,
          letterSpacing: -0.2,
          display: 'inline-block',
          width: 'fit-content',
        }}>
          {CAPTION}
        </div>
      )}
    </AbsoluteFill>
  );
};
