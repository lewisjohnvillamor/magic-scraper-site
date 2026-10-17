import React from 'react';
import { AbsoluteFill, Audio, Easing, Freeze, interpolate, OffthreadVideo, Sequence, spring,
  staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import plan from './plan.json';
import file from './file.json';

const FPS = plan.fps;
const f = (s: number) => Math.round(s * FPS);
const INK = '#14121f', VIOLET = '#5b4bd6', SOFT = '#a78bfa';
const FONT_UI = 'Archivo, Inter, system-ui, sans-serif', FONT_HEAD = 'Fraunces, Georgia, serif';

// ---------------------------------------------------------------- geometry
// The browser window: 1800 wide, a 74px chrome bar, then the recording.
// Only the top 940px of the recording is used: headless Chrome's screencast
// sometimes leaves the bottom ~140px of the frame grey.
const SRC_H = 940;
const WIN = { x: 60, y: 0, w: 1800, bar: 74 };
const K = WIN.w / 1920;                                   // recording -> window scale
const WIN_H = WIN.bar + SRC_H * K;
WIN.y = Math.round((1080 - WIN_H) / 2);
// Camera presets: a point of the recording to centre on, and a zoom.
type Cam = { s: number; x: number; y: number };
const CAMS: Record<string, Cam> = {
  wide: { s: 1, x: 960, y: 540 },
  page: { s: 1.22, x: 640, y: 560 },
  pageTable: { s: 1.3, x: 600, y: 470 },
  panelTop: { s: 1.42, x: 1630, y: 330 },
  panelMid: { s: 1.42, x: 1630, y: 470 },
  panelTable: { s: 1.42, x: 1630, y: 580 },
  icon: { s: 1.55, x: 1830, y: -20 },                     // the toolbar, above the recording
};
// A camera point in output pixels.
const camPx = (c: Cam) => ({ x: WIN.x + c.x * K, y: WIN.y + WIN.bar + c.y * K, s: c.s });
function camAt(keys: [number, string][], p: number) {
  const pts = keys.map(([t, n]) => ({ t, ...camPx(CAMS[n]) }));
  if (p <= pts[0].t) return pts[0];
  for (let i = 1; i < pts.length; i++) {
    if (p <= pts[i].t) {
      const a = pts[i - 1], b = pts[i];
      const e = Easing.inOut(Easing.cubic)((p - a.t) / Math.max(1e-6, b.t - a.t));
      return { x: a.x + (b.x - a.x) * e, y: a.y + (b.y - a.y) * e, s: a.s + (b.s - a.s) * e };
    }
  }
  return pts[pts.length - 1];
}
// Translate so the camera point sits at the frame centre, without showing
// past the window's edges.
function camTransform(c: { x: number; y: number; s: number }) {
  if (c.s <= 1.0001) return 'none';
  let tx = 960 - c.x * c.s, ty = 540 - c.y * c.s;
  const left = WIN.x * c.s + tx, right = (WIN.x + WIN.w) * c.s + tx;
  const top = WIN.y * c.s + ty, bottom = (WIN.y + WIN_H) * c.s + ty;
  if (left > WIN.x) tx -= left - WIN.x;
  if (right < WIN.x + WIN.w) tx += (WIN.x + WIN.w) - right;
  if (top > 0) ty -= top;
  if (bottom < 1080) ty += 1080 - bottom;
  return `translate(${tx}px, ${ty}px) scale(${c.s})`;
}

const Fonts = () => (
  <style>{`
    @font-face { font-family: 'Fraunces'; src: url('${staticFile('fonts/fraunces-var.woff2')}') format('woff2'); font-weight: 100 900; }
    @font-face { font-family: 'Archivo'; src: url('${staticFile('fonts/archivo-var.woff2')}') format('woff2'); font-weight: 100 900; }
  `}</style>
);
const Mark: React.FC<{ size: number }> = ({ size }) => (
  <div style={{ width: size, height: size, borderRadius: size * 0.27, display: 'flex', alignItems: 'center',
    justifyContent: 'center', background: `linear-gradient(145deg, ${VIOLET}, #8b5cf6)`,
    boxShadow: `0 ${size * 0.2}px ${size * 0.55}px -${size * 0.14}px rgba(139,92,246,.85)` }}>
    <svg viewBox="0 0 24 24" width={size * 0.52} height={size * 0.52} fill="none" stroke="#fff" strokeWidth={2.4}
      strokeLinecap="round" strokeLinejoin="round"><path d="M4 20 L14 10" /><path d="M18 3 v5 M15.5 5.5 h5" /></svg>
  </div>
);

// ---------------------------------------------------------------- background
const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const a = frame / FPS;
  return (
    <AbsoluteFill style={{ background: '#0f0d18', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', left: 300 + Math.sin(a / 9) * 120, top: -500 + Math.cos(a / 11) * 80,
        width: 1700, height: 1700, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(139,92,246,.30) 0%, rgba(91,75,214,.10) 42%, transparent 68%)' }} />
      <div style={{ position: 'absolute', right: -500 + Math.cos(a / 13) * 100, bottom: -700,
        width: 1500, height: 1500, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(56,189,248,.10) 0%, transparent 62%)' }} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- browser chrome
const PAGES: Record<string, { title: string; url: string }> = {
  catalogue: { title: 'Catalogue — Northwind Supply', url: 'magicscraper.app/demo/catalogue' },
  rates: { title: 'Delivery rates — Northwind Supply', url: 'magicscraper.app/demo/rates' },
  awkward: { title: 'Clearance — Northwind Supply', url: 'magicscraper.app/demo/awkward' },
};
const Chrome: React.FC<{ page: string; step?: string | null; stepNo?: number | null; iconPulse: number }> =
  ({ page, step, stepNo, iconPulse }) => {
  const p = PAGES[page] || PAGES.catalogue;
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: WIN.w, height: WIN.bar, background: '#ebe9f2',
      borderBottom: '1px solid #d6d3e0', fontFamily: FONT_UI }}>
      <div style={{ position: 'absolute', left: 18, top: 13, display: 'flex', gap: 8 }}>
        {['#ff5f57', '#febc2e', '#28c840'].map((c) => <span key={c} style={{ width: 12, height: 12, borderRadius: 6, background: c }} />)}
      </div>
      <div style={{ position: 'absolute', left: 92, top: 6, height: 30, padding: '0 16px', minWidth: 300,
        background: '#fbfaff', borderRadius: '9px 9px 0 0', display: 'flex', alignItems: 'center', gap: 9,
        fontSize: 13.5, color: '#2a2738' }}>
        <span style={{ width: 14, height: 14, borderRadius: 4, background: '#1f6f50' }} />{p.title}
      </div>
      {step ? (
        <div style={{ position: 'absolute', right: 16, top: 7, height: 26, padding: '0 13px', borderRadius: 13,
          background: INK, color: '#fff', fontSize: 13.5, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ color: SOFT, fontWeight: 700 }}>STEP {stepNo} / {plan.steps}</span>{step}
        </div>
      ) : null}
      <div style={{ position: 'absolute', left: 12, right: 12, top: 38, height: 32, display: 'flex',
        alignItems: 'center', gap: 12, background: '#fbfaff', borderRadius: 8, padding: '0 12px' }}>
        <span style={{ color: '#8a869c', fontSize: 16 }}>‹ ›</span>
        <div style={{ flex: 1, height: 24, borderRadius: 12, background: '#efedf6', display: 'flex', alignItems: 'center',
          padding: '0 14px', fontSize: 14, color: '#3b3850' }}>
          <span style={{ color: '#1f8a5b', marginRight: 8 }}>🔒</span>{p.url}
        </div>
        <span style={{ fontSize: 17, color: '#6f6b82' }}>🧩</span>
        <div style={{ transform: `scale(${1 + iconPulse * 0.25})`, boxShadow: iconPulse ? `0 0 0 ${iconPulse * 7}px rgba(124,108,240,.28)` : 'none',
          borderRadius: 7 }}><Mark size={24} /></div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- footage
type Piece = { play?: number[]; freeze?: number; dur?: number };
const Footage: React.FC<{ pieces: Piece[] }> = ({ pieces }) => {
  let at = 0;
  return (
    <>
      {pieces.map((p, i) => {
        const len = p.play ? f(p.play[1]) - f(p.play[0]) : f(p.dur!);
        const from = at; at += len;
        return (
          <Sequence key={i} from={from} durationInFrames={len} layout="none">
            {p.play ? (
              <OffthreadVideo src={staticFile('walk2.mp4')} startFrom={f(p.play[0])} muted
                style={{ width: 1920 * K, height: 1080 * K, display: 'block' }} />
            ) : (
              <Freeze frame={0}>
                <OffthreadVideo src={staticFile('walk2.mp4')} startFrom={f(p.freeze!)} muted
                  style={{ width: 1920 * K, height: 1080 * K, display: 'block' }} />
              </Freeze>
            )}
          </Sequence>
        );
      })}
    </>
  );
};

// ---------------------------------------------------------------- the file, opened
const FileView: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inn = spring({ frame, fps, config: { damping: 18, mass: 0.8 } });
  const out = interpolate(frame, [dur - 10, dur], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  // The export has 22 columns, links and page titles among them; show the ones
  // a person reads, and say how many there are in all.
  const SHOW = ['Link Text', 'Maker', 'Price', 'Rating', 'Stock', 'detail:SKU', 'detail:Availability',
                'detail:Material', 'detail:Made in', 'detail:Weight'];
  const allHeads: string[] = (file as any).heads;
  const pick = SHOW.map((h) => allHeads.indexOf(h)).filter((i) => i >= 0);
  const heads = pick.map((i) => allHeads[i]);
  const body: string[][] = (file as any).body.map((r: string[]) => pick.map((i) => r[i]));
  const cols = heads.length;
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
  return (
    <AbsoluteFill style={{ background: `rgba(15,13,24,${0.55 * inn * out})` }}>
      <div style={{ position: 'absolute', left: 170, top: 140, width: 1580, borderRadius: 14,
        background: '#fff', overflow: 'hidden', fontFamily: FONT_UI,
        boxShadow: '0 60px 120px -30px rgba(0,0,0,.8)', opacity: out,
        transform: `translateY(${(1 - inn) * 120}px) scale(${0.96 + inn * 0.04})` }}>
        <div style={{ height: 52, background: '#1f6f50', color: '#fff', display: 'flex', alignItems: 'center',
          padding: '0 22px', gap: 14, fontSize: 17 }}>
          <span style={{ background: '#fff', color: '#1f6f50', fontWeight: 800, borderRadius: 5, padding: '2px 7px', fontSize: 14 }}>X</span>
          <b>catalogue-54-rows.xlsx</b>
          <span style={{ opacity: .8, fontSize: 14 }}>{(file as any).total} rows · {allHeads.length} columns · showing {cols}</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: `46px repeat(${cols}, minmax(0, 1fr))`, fontSize: 16 }}>
          <div style={{ background: '#f1f3f2', borderRight: '1px solid #dfe3e1', borderBottom: '1px solid #dfe3e1' }} />
          {heads.map((_, i) => <div key={'l' + i} style={{ background: '#f1f3f2', textAlign: 'center', color: '#6b746f',
            padding: '5px 0', borderRight: '1px solid #dfe3e1', borderBottom: '1px solid #dfe3e1', fontSize: 13 }}>{letters[i]}</div>)}
          <div style={{ background: '#f1f3f2', textAlign: 'center', color: '#6b746f', padding: '7px 0',
            borderRight: '1px solid #dfe3e1', borderBottom: '1px solid #dfe3e1', fontSize: 13 }}>1</div>
          {heads.map((h, i) => <div key={'h' + i} style={{ fontWeight: 700, padding: '7px 9px', whiteSpace: 'nowrap',
            overflow: 'hidden', textOverflow: 'ellipsis', borderRight: '1px solid #e6e9e8', borderBottom: '2px solid #1f6f50',
            color: '#18201c' }}>{h}</div>)}
          {body.map((r, ri) => {
            const show = interpolate(frame, [6 + ri * 1.6, 12 + ri * 1.6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
            return (
              <React.Fragment key={ri}>
                <div style={{ background: '#f1f3f2', textAlign: 'center', color: '#6b746f', padding: '7px 0',
                  borderRight: '1px solid #dfe3e1', borderBottom: '1px solid #eef0ef', fontSize: 13 }}>{ri + 2}</div>
                {r.map((c, ci) => <div key={ci} style={{ padding: '7px 9px', whiteSpace: 'nowrap', overflow: 'hidden',
                  textOverflow: 'ellipsis', borderRight: '1px solid #eef0ef', borderBottom: '1px solid #eef0ef',
                  color: '#26302b', opacity: show }}>{c}</div>)}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- title and outro
const Title: React.FC<{ dur: number }> = ({ dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame: frame - 4, fps, config: { damping: 14 } });
  const t1 = spring({ frame: frame - 14, fps, config: { damping: 20 } });
  const t2 = spring({ frame: frame - 34, fps, config: { damping: 20 } });
  const out = interpolate(frame, [dur - 14, dur], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const chips = ['Find the table', 'Collect every page', 'Open each row’s page', 'Download to Excel'];
  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', opacity: out, fontFamily: FONT_UI, color: '#fff' }}>
      <div style={{ transform: `scale(${pop})` }}><Mark size={112} /></div>
      <div style={{ marginTop: 38, fontFamily: FONT_HEAD, fontWeight: 600, fontSize: 104, letterSpacing: -3, lineHeight: 1,
        opacity: t1, transform: `translateY(${(1 - t1) * 30}px)` }}>Magic Scraper</div>
      <div style={{ marginTop: 22, fontSize: 34, color: '#cfc9e6', opacity: t2, transform: `translateY(${(1 - t2) * 20}px)` }}>
        Any web page, into a clean spreadsheet. <span style={{ color: SOFT }}>The full walkthrough.</span></div>
      <div style={{ display: 'flex', gap: 14, marginTop: 46 }}>
        {chips.map((c, i) => {
          const s = spring({ frame: frame - 60 - i * 9, fps, config: { damping: 18 } });
          return <div key={c} style={{ fontSize: 22, padding: '11px 22px', borderRadius: 999, opacity: s,
            transform: `translateY(${(1 - s) * 18}px)`, border: '1px solid rgba(255,255,255,.22)', color: '#e6e3f2',
            background: 'rgba(255,255,255,.04)' }}><span style={{ color: SOFT, marginRight: 8 }}>{i + 1}</span>{c}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};
const Outro: React.FC<{ dur: number }> = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = spring({ frame: frame - 6, fps, config: { damping: 16 } });
  const b = spring({ frame: frame - 26, fps, config: { damping: 18 } });
  const c = spring({ frame: frame - 48, fps, config: { damping: 18 } });
  const pill = (txt: string, solid = false) => (
    <div style={{ fontSize: 24, padding: '13px 26px', borderRadius: 999, fontWeight: solid ? 700 : 500,
      background: solid ? '#fff' : 'transparent', color: solid ? INK : '#e6e3f2',
      border: solid ? '1px solid #fff' : '1px solid rgba(255,255,255,.25)' }}>{txt}</div>
  );
  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center', fontFamily: FONT_UI, color: '#fff' }}>
      <div style={{ transform: `scale(${a})` }}><Mark size={104} /></div>
      <div style={{ marginTop: 34, fontFamily: FONT_HEAD, fontWeight: 600, fontSize: 92, letterSpacing: -3, opacity: a }}>Magic Scraper</div>
      <div style={{ marginTop: 18, fontSize: 30, color: '#cfc9e6', textAlign: 'center', lineHeight: 1.45, opacity: b }}>
        Detect, tidy, crawl and export: free.<br />Pro opens the page behind every row and compares runs.</div>
      <div style={{ display: 'flex', gap: 14, marginTop: 40, opacity: c, transform: `translateY(${(1 - c) * 16}px)` }}>
        {pill('Free on Chrome & Edge', true)}{pill('Pro $19 once · no subscription')}{pill('Nothing leaves your browser')}
      </div>
      <div style={{ marginTop: 44, fontSize: 30, fontFamily: 'ui-monospace, monospace', color: SOFT, opacity: c }}>magicscraper.app</div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- audio
const voWindows = plan.scenes.map((s: any) => [s.voAt, s.voAt + s.vo] as [number, number]);
function bedVolume(fr: number) {
  const t = fr / FPS;
  let speaking = 0;
  for (const [a, z] of voWindows) {
    const ramp = Math.min(1, Math.max(0, Math.min(t - (a - 0.35), (z + 0.5) - t) / 0.35));
    speaking = Math.max(speaking, ramp);
  }
  const fadeIn = Math.min(1, t / 1.5), fadeOut = Math.min(1, Math.max(0, (plan.total - t) / 4));
  return (0.34 - 0.22 * speaking) * fadeIn * fadeOut;
}

// ---------------------------------------------------------------- the film
export const Walkthrough: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const scenes: any[] = plan.scenes;
  const cur = scenes.find((s) => t >= s.start && t < s.start + s.dur) || scenes[scenes.length - 1];
  const firstVideo = scenes.find((s) => s.kind === 'video');
  const lastVideoEnd = (() => { const v = scenes.filter((s) => s.kind === 'video' || s.kind === 'file'); const l = v[v.length - 1]; return l.start + l.dur; })();
  // The window rises in after the title and settles away before the outro.
  const winIn = interpolate(t, [firstVideo.start - 0.6, firstVideo.start + 0.5], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.out(Easing.cubic) });
  const winOut = interpolate(t, [lastVideoEnd - 0.5, lastVideoEnd + 0.4], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const videoScene = cur.kind === 'video' ? cur : scenes.filter((s) => s.kind === 'video' && s.start <= t).pop() || firstVideo;
  const p = (t - videoScene.start) / videoScene.dur;
  const cam = cur.kind === 'video' ? camAt(videoScene.cam, Math.min(1, Math.max(0, p))) : camPx(CAMS.wide);
  // the toolbar icon pulses as the open scene reaches it
  const openS = scenes.find((s) => s.key === 'open');
  const iconT = (t - openS.start) / openS.dur;
  const iconPulse = interpolate(iconT, [0.52, 0.6, 0.7], [0, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <AbsoluteFill>
      <Fonts />
      <Backdrop />
      <AbsoluteFill style={{ transform: camTransform(cam), transformOrigin: '0 0' }}>
        <div style={{ position: 'absolute', left: WIN.x, top: WIN.y, width: WIN.w, height: WIN_H, borderRadius: 14,
          overflow: 'hidden', background: '#fff', opacity: winIn * winOut,
          transform: `translateY(${(1 - winIn) * 60}px) scale(${0.97 + 0.03 * winIn})`,
          boxShadow: '0 50px 120px -30px rgba(0,0,0,.85), 0 0 0 1px rgba(255,255,255,.08)' }}>
          <Chrome page={videoScene.page} step={cur.step} stepNo={cur.stepNo} iconPulse={iconPulse} />
          <div style={{ position: 'absolute', left: 0, top: WIN.bar, width: WIN.w, height: SRC_H * K, overflow: 'hidden', background: '#fff' }}>
            {scenes.filter((s) => s.kind === 'video').map((s) => (
              <Sequence key={s.key} from={f(s.start)} durationInFrames={f(s.dur) + 1} layout="none">
                <Footage pieces={s.pieces} />
              </Sequence>
            ))}
          </div>
        </div>
      </AbsoluteFill>
      {scenes.map((s) => s.kind === 'title' ? (
        <Sequence key={s.key} from={f(s.start)} durationInFrames={f(s.dur)}><Title dur={f(s.dur)} /></Sequence>
      ) : s.kind === 'file' ? (
        <Sequence key={s.key} from={f(s.start)} durationInFrames={f(s.dur)}><FileView dur={f(s.dur)} /></Sequence>
      ) : s.kind === 'outro' ? (
        <Sequence key={s.key} from={f(s.start)} durationInFrames={f(s.dur)}><Outro dur={f(s.dur)} /></Sequence>
      ) : null)}
      {scenes.map((s) => (
        <Sequence key={'vo-' + s.key} from={f(s.voAt)} durationInFrames={f(s.vo) + 6}>
          <Audio src={staticFile(`vo/${s.key}.wav`)} volume={1} />
        </Sequence>
      ))}
      <Audio src={staticFile('bed.wav')} volume={bedVolume} />
    </AbsoluteFill>
  );
};
