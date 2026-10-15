/* Short #1, "Find partners": a motion graphic, 1080x1920, about 27 s.
   Hook -> problem -> rehook -> answer -> call to action. Nothing here is a
   screen recording; the directory, the spreadsheet and the companies in them
   are drawn here and are fictional. The words on screen are timed to the
   voice (words.json, from voice.py), so the captioned cut reads at the pace
   the voiced cut speaks. */
import React from 'react';
import { AbsoluteFill, Audio, Easing, interpolate, Sequence, spring, staticFile, useCurrentFrame } from 'remotion';
import words from './words.json';

export const FPS = 30;
export const TOTAL = 27.5;
const W = 1080, H = 1920;
const INK = '#0d0b16', VIOLET = '#6d5cf0', SOFT = '#b4a2ff', MINT = '#34d399', BLUE = '#3b82f6';
const UI = 'Archivo, Inter, system-ui, sans-serif', HEAD = 'Fraunces, Georgia, serif';

// ------------------------------------------------------------------ timeline (seconds)
const T = {
  hook: [0, 2.6], problem: [2.6, 10.4], rehook: [10.4, 12.0], click: [12.0, 13.3],
  answer: [13.3, 17.6], list: [17.6, 20.6], cta: [20.6, TOTAL],
};
// When each line of the voice starts.
const VO: Record<string, number> = {
  hook: 0.25, problem1: 2.75, problem2: 6.15, rehook: 10.5, click: 12.1,
  answer1: 13.5, answer2: 17.8, cta: 20.95,
};
const WJ = words as Record<string, { dur: number; words: [string, number, number][] }>;
const wordAt = (key: string, i: number) => VO[key] + (WJ[key].words[Math.min(i, WJ[key].words.length - 1)]?.[1] ?? 0);
const voEnd = (key: string) => VO[key] + WJ[key].dur;

// ------------------------------------------------------------------ helpers
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const lin = (t: number, a: number[], b: number[], ease?: (x: number) => number) =>
  interpolate(t, a, b, ease ? { ...clamp, easing: ease } : clamp);
const useT = () => useCurrentFrame() / FPS;
const sp = (t: number, at: number, damping = 16, mass = 0.7) =>
  spring({ frame: Math.round((t - at) * FPS), fps: FPS, config: { damping, mass } });
const inWin = (t: number, w: number[], pad = 0) => t >= w[0] - pad && t < w[1] + pad;

// ------------------------------------------------------------------ the companies (fictional)
const CO: [string, string, string][] = [
  ['Halden Logistics', 'Leeds', '555-0142'], ['Brightwater Foods', 'Austin', '555-0187'],
  ['Northgate Packaging', 'Toronto', '555-0119'], ['Copperline Electrical', 'Denver', '555-0164'],
  ['Meridian Print Co.', 'Bristol', '555-0131'], ['Oakridge Supply', 'Portland', '555-0176'],
  ['Bluefin Marine Parts', 'Halifax', '555-0158'], ['Lantern Creative', 'Melbourne', '555-0122'],
  ['Fairway Interiors', 'Dublin', '555-0193'], ['Summit Cold Storage', 'Calgary', '555-0105'],
  ['Redwood Tile & Stone', 'Sacramento', '555-0148'], ['Kestrel Freight', 'Glasgow', '555-0170'],
  ['Atlas Signworks', 'Phoenix', '555-0136'], ['Juniper Catering', 'Auckland', '555-0181'],
  ['Ironbridge Fabrication', 'Sheffield', '555-0114'], ['Silverleaf Florists', 'Adelaide', '555-0167'],
  ['Harbor Light Media', 'Seattle', '555-0129'], ['Pinecrest Builders', 'Boise', '555-0152'],
  ['Westmoor Accounting', 'Manchester', '555-0198'], ['Cobalt Cleaning Co.', 'Chicago', '555-0143'],
  ['Granite Peak HVAC', 'Salt Lake City', '555-0111'], ['Riverside Print Lab', 'Cork', '555-0185'],
  ['Maple & Main Bakery', 'Vancouver', '555-0126'], ['Vantage Event Hire', 'Cardiff', '555-0160'],
];
const HUES = [262, 200, 152, 28, 340, 190, 220, 12, 285, 170, 45, 310];
const site = (name: string) => name.toLowerCase().replace(/&/g, 'and').replace(/[^a-z ]/g, '').trim().split(/\s+/).slice(0, 2).join('-') + '.com';
const initials = (name: string) => name.split(/\s+/).filter((w) => /^[A-Z]/.test(w)).slice(0, 2).map((w) => w[0]).join('');
const TOTAL_ROWS = 412, PAGES = 21;

// ------------------------------------------------------------------ small pieces
const Fonts = () => (
  <style>{`
    @font-face { font-family: 'Fraunces'; src: url('${staticFile('fonts/fraunces-var.woff2')}') format('woff2'); font-weight: 100 900; }
    @font-face { font-family: 'Archivo'; src: url('${staticFile('fonts/archivo-var.woff2')}') format('woff2'); font-weight: 100 900; }
  `}</style>
);
const Mark: React.FC<{ size: number; glow?: number }> = ({ size, glow = 1 }) => (
  <div style={{ width: size, height: size, borderRadius: size * 0.27, display: 'flex', alignItems: 'center',
    justifyContent: 'center', background: `linear-gradient(145deg, #5b4bd6, #8b5cf6)`,
    boxShadow: `0 ${size * 0.2}px ${size * 0.6}px -${size * 0.12}px rgba(139,92,246,${0.9 * glow})` }}>
    <svg viewBox="0 0 24 24" width={size * 0.52} height={size * 0.52} fill="none" stroke="#fff" strokeWidth={2.4}
      strokeLinecap="round" strokeLinejoin="round"><path d="M4 20 L14 10" /><path d="M18 3 v5 M15.5 5.5 h5" /></svg>
  </div>
);
const Logo: React.FC<{ i: number; size: number }> = ({ i, size }) => {
  const h = HUES[i % HUES.length];
  return (
    <div style={{ width: size, height: size, borderRadius: size / 2, flex: 'none', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: `hsl(${h} 70% 92%)`, color: `hsl(${h} 55% 34%)`, fontWeight: 800,
      fontSize: size * 0.38, fontFamily: UI }}>{initials(CO[i % CO.length][0])}</div>
  );
};
const Cursor: React.FC<{ x: number; y: number; press?: number; size?: number }> = ({ x, y, press = 0, size = 64 }) => (
  <div style={{ position: 'absolute', left: x, top: y, width: size, height: size, transform: `scale(${1 - press * 0.15})`,
    transformOrigin: '0 0', filter: 'drop-shadow(0 6px 10px rgba(0,0,0,.45))', zIndex: 50 }}>
    <svg viewBox="0 0 24 24" width={size} height={size}>
      <path d="M4 2 L4 19 L8.5 14.8 L11.6 21.5 L14.4 20.2 L11.3 13.6 L17.5 13.4 Z" fill="#fff" stroke={INK} strokeWidth={1.3} strokeLinejoin="round" />
    </svg>
  </div>
);
const Keycap: React.FC<{ label: string; x: number; y: number; s: number }> = ({ label, x, y, s }) => (
  <div style={{ position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) scale(${s})`, opacity: Math.min(1, s * 1.4),
    display: 'flex', gap: 10, zIndex: 60 }}>
    {label.split(' ').map((k) => (
      <div key={k} style={{ minWidth: 76, height: 76, padding: '0 18px', borderRadius: 16, background: '#fff', color: INK,
        fontFamily: UI, fontWeight: 800, fontSize: 34, display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 7px 0 #b9b4cc, 0 18px 30px -8px rgba(0,0,0,.55)' }}>{k}</div>
    ))}
  </div>
);

// Words that rise in as they are spoken. `lines` lays out the line's words
// (same count as the voice's words); `hi` marks word indexes to highlight.
const Spoken: React.FC<{ k: string; lines: string[][]; size: number; font?: string; weight?: number;
  hi?: number[]; hiColor?: string; marker?: number[]; lineHeight?: number; align?: 'center' | 'left' }> =
  ({ k, lines, size, font = UI, weight = 800, hi = [], hiColor = SOFT, marker = [], lineHeight = 1.08, align = 'center' }) => {
  const t = useT();
  let idx = 0;
  return (
    <div style={{ fontFamily: font, fontWeight: weight, fontSize: size, lineHeight, color: '#fff', textAlign: align,
      letterSpacing: font === HEAD ? -2 : -1 }}>
      {lines.map((ln, li) => (
        <div key={li} style={{ display: 'flex', justifyContent: align === 'center' ? 'center' : 'flex-start', flexWrap: 'wrap', gap: `0 ${size * 0.26}px` }}>
          {ln.map((w) => {
            const i = idx++;
            const at = wordAt(k, i) - 0.06;
            const s = sp(t, at, 14, 0.55);
            const isHi = hi.includes(i), isMark = marker.includes(i);
            const mk = lin(t, [at + 0.05, at + 0.35], [0, 1], Easing.out(Easing.cubic));
            return (
              <span key={i} style={{ position: 'relative', display: 'inline-block', opacity: Math.min(1, s * 1.5),
                transform: `translateY(${(1 - s) * size * 0.45}px) scale(${0.9 + 0.1 * s})`, color: isHi ? hiColor : '#fff' }}>
                {isMark ? <span style={{ position: 'absolute', left: -size * 0.1, right: -size * 0.1, top: '18%', bottom: '4%',
                  background: VIOLET, borderRadius: size * 0.12, transform: `scaleX(${mk})`, transformOrigin: '0 50%', zIndex: -1 }} /> : null}
                {w}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

// ------------------------------------------------------------------ background
const Backdrop: React.FC = () => {
  const t = useT();
  const flash = lin(t, [12.03, 12.08, 12.6], [0, 0.55, 0]);
  const dim = lin(t, [10.4, 10.7, 11.85, 12.0], [0, 0.45, 0.45, 0]);
  return (
    <AbsoluteFill style={{ background: INK, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', left: -380 + Math.sin(t / 3) * 90, top: -300 + Math.cos(t / 4) * 70, width: 1500, height: 1500,
        borderRadius: '50%', background: 'radial-gradient(circle, rgba(139,92,246,.34) 0%, rgba(91,75,214,.12) 40%, transparent 68%)' }} />
      <div style={{ position: 'absolute', right: -520 + Math.cos(t / 3.5) * 80, bottom: -420, width: 1400, height: 1400,
        borderRadius: '50%', background: 'radial-gradient(circle, rgba(56,189,248,.16) 0%, transparent 62%)' }} />
      <div style={{ position: 'absolute', inset: 0, opacity: 0.22,
        backgroundImage: 'radial-gradient(rgba(255,255,255,.35) 1.4px, transparent 1.6px)', backgroundSize: '44px 44px',
        backgroundPosition: `0 ${-(t * 14) % 44}px` }} />
      <div style={{ position: 'absolute', inset: 0, background: '#000', opacity: dim }} />
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at 50% 46%, #a78bfa, #5b4bd6 60%)', opacity: flash }} />
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 1. hook
const Hook: React.FC = () => {
  const t = useT();
  if (!inWin(t, T.hook, 0.3)) return null;
  const out = lin(t, [2.35, 2.65], [0, 1], Easing.in(Easing.cubic));
  const chip = sp(t, 0.05);
  // Businesses drift around the question, and draw lines to it as "partner" is said.
  const link = lin(t, [wordAt('hook', 4) - 0.1, wordAt('hook', 4) + 0.5], [0, 1], Easing.out(Easing.cubic));
  const spots = [[260, 470], [820, 560], [240, 1290], [830, 1230], [540, 380], [560, 1440]];
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `translateY(${-out * 160}px)` }}>
      <svg width={W} height={H} style={{ position: 'absolute', inset: 0 }}>
        {spots.map(([x, y], i) => (
          <line key={i} x1={540} y1={880} x2={x + Math.sin(t * 1.3 + i) * 10} y2={y + Math.cos(t * 1.1 + i) * 12}
            stroke={SOFT} strokeWidth={3} strokeDasharray="8 10" opacity={0.55 * link}
            pathLength={1} style={{ strokeDashoffset: 0 }} />
        ))}
      </svg>
      {spots.map(([x, y], i) => {
        const s = sp(t, 0.1 + i * 0.09, 13);
        return (
          <div key={i} style={{ position: 'absolute', left: x + Math.sin(t * 1.3 + i) * 10, top: y + Math.cos(t * 1.1 + i) * 12,
            transform: `translate(-50%,-50%) scale(${s})`, display: 'flex', alignItems: 'center', gap: 14, padding: '14px 22px 14px 14px',
            borderRadius: 999, background: 'rgba(255,255,255,.95)', boxShadow: '0 20px 40px -14px rgba(0,0,0,.6)',
            fontFamily: UI, fontWeight: 700, fontSize: 28, color: INK, whiteSpace: 'nowrap' }}>
            <Logo i={i} size={50} />{CO[i][0]}
          </div>
        );
      })}
      <div style={{ position: 'absolute', left: 0, right: 0, top: 250, display: 'flex', justifyContent: 'center' }}>
        <div style={{ transform: `scale(${chip})`, padding: '12px 28px', borderRadius: 999, border: `2px solid ${SOFT}`,
          color: SOFT, fontFamily: UI, fontWeight: 800, fontSize: 30, letterSpacing: 4 }}>FOR BUSINESSES</div>
      </div>
      <div style={{ position: 'absolute', left: 60, right: 60, top: 700 }}>
        <Spoken k="hook" lines={[['Looking', 'for'], ['businesses'], ['to', 'partner', 'with?']]} size={124} font={HEAD}
          weight={650} hi={[2]} marker={[4, 5]} lineHeight={1.12} />
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ the stage: a directory page and a spreadsheet
// Shared by the problem (copied by hand) and the answer (one click).
const BR = { x: 60, y: 470, w: 960, h: 560, bar: 58 };
const CARD = { w: 438, h: 112, gx: 24, gy: 14, x0: 30, y0: 104 };
const cardPos = (k: number) => ({ x: BR.x + CARD.x0 + (k % 2) * (CARD.w + CARD.gx), y: BR.y + BR.bar + CARD.y0 + Math.floor(k / 2) * (CARD.h + CARD.gy) });
const SH0 = { x: 60, y: 1070, w: 960, h: 420 };
const COLS = [{ n: 'Company', w: 380 }, { n: 'City', w: 190 }, { n: 'Phone', w: 180 }, { n: 'Website', w: 210 }];
const ROW_H = 56, SH_BAR = 54, SH_HEAD = 52;

const Browser: React.FC<{ page: number; slide: number; outline: (k: number) => number; selected: (k: number) => number;
  pagerHot: number; badge: number }> = ({ page, slide, outline, selected, pagerHot, badge }) => {
  const base = ((page - 1) * 6) % CO.length;
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: BR.w, height: BR.h, borderRadius: 22, overflow: 'hidden',
      background: '#fff', boxShadow: '0 40px 90px -30px rgba(0,0,0,.85), 0 0 0 1px rgba(255,255,255,.1)', fontFamily: UI }}>
      <div style={{ height: BR.bar, background: '#eceaf3', display: 'flex', alignItems: 'center', gap: 10, padding: '0 20px' }}>
        {['#ff5f57', '#febc2e', '#28c840'].map((c) => <span key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c }} />)}
        <div style={{ marginLeft: 14, flex: 1, height: 36, borderRadius: 18, background: '#fff', display: 'flex', alignItems: 'center',
          padding: '0 18px', fontSize: 22, color: '#4b475d' }}>🔒 business-network.org/members?page={page}</div>
        <div style={{ position: 'relative' }}>
          <Mark size={36} glow={0.4} />
          {badge > 0 ? <div style={{ position: 'absolute', right: -6, top: -8, padding: '2px 8px', borderRadius: 10, background: MINT,
            color: '#05301f', fontSize: 16, fontWeight: 800, transform: `scale(${badge})` }}>6</div> : null}
        </div>
      </div>
      <div style={{ position: 'relative', height: BR.h - BR.bar }}>
        <div style={{ position: 'absolute', left: CARD.x0, top: 20, right: CARD.x0, display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
          <span style={{ fontFamily: HEAD, fontWeight: 650, fontSize: 40, color: '#17142a' }}>Member directory</span>
          <span style={{ fontSize: 23, color: '#6f6a85' }}>412 companies</span>
        </div>
        <div style={{ position: 'absolute', inset: 0, transform: `translateX(${slide}px)`, opacity: 1 - Math.abs(slide) / 600 }}>
          {Array.from({ length: 6 }, (_, k) => {
            const i = (base + k) % CO.length; const [name, city, phone] = CO[i];
            const p = cardPos(k); const o = outline(k), s = selected(k);
            return (
              <div key={k} style={{ position: 'absolute', left: p.x - BR.x, top: p.y - BR.y - BR.bar, width: CARD.w, height: CARD.h,
                borderRadius: 14, border: `${o > 0 ? 3 : 1.5}px solid ${o > 0 ? BLUE : '#e4e1ee'}`,
                background: o > 0 ? `rgba(59,130,246,${0.1 * o})` : '#fbfaff', display: 'flex', alignItems: 'center', gap: 18, padding: '0 18px',
                boxShadow: o > 0 ? `0 0 0 ${4 * o}px rgba(59,130,246,.18)` : 'none' }}>
                <Logo i={i} size={58} />
                <div style={{ minWidth: 0, position: 'relative' }}>
                  {s > 0 ? <div style={{ position: 'absolute', left: -4, top: -4, bottom: -4, width: `calc(${s * 100}% + 8px)`,
                    background: 'rgba(59,130,246,.32)', borderRadius: 4 }} /> : null}
                  <div style={{ position: 'relative', fontWeight: 800, fontSize: 27, color: '#17142a', whiteSpace: 'nowrap' }}>{name}</div>
                  <div style={{ position: 'relative', fontSize: 21, color: '#5f5a75', marginTop: 4, whiteSpace: 'nowrap' }}>{city} · {phone}</div>
                  <div style={{ position: 'relative', fontSize: 20, color: VIOLET, marginTop: 2 }}>{site(name)}</div>
                </div>
              </div>
            );
          })}
        </div>
        <div style={{ position: 'absolute', left: 0, right: 0, bottom: 14, display: 'flex', justifyContent: 'center', gap: 8, fontSize: 21 }}>
          {['‹', '1', '2', '3', '…', '21', '›'].map((p, i) => {
            const on = (p === String(page)) || (i === 1 && page === 1) || (p === '…' && page > 3 && page < 21);
            const label = p === '…' && page > 3 && page < 21 ? String(page) : p;
            return (
              <span key={i} style={{ minWidth: 34, height: 30, padding: '0 6px', borderRadius: 8, display: 'flex', alignItems: 'center',
                justifyContent: 'center', background: on ? '#17142a' : (p === '21' && pagerHot > 0 ? `rgba(239,68,68,${pagerHot})` : 'transparent'),
                color: on || (p === '21' && pagerHot > 0.4) ? '#fff' : '#4b475d', fontWeight: 700,
                transform: p === '21' ? `scale(${1 + pagerHot * 0.35})` : 'none' }}>{label}</span>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const Sheet: React.FC<{ w: number; h: number; title: string; rows: number[]; rowIn: (r: number) => number; scroll: number;
  count?: string; stamp?: number; hotCol?: number }> = ({ w, h, title, rows, rowIn, scroll, count, stamp = 0, hotCol = -1 }) => (
  <div style={{ position: 'absolute', left: 0, top: 0, width: w, height: h, borderRadius: 22, overflow: 'hidden', background: '#fff',
    boxShadow: '0 40px 90px -30px rgba(0,0,0,.85), 0 0 0 1px rgba(255,255,255,.1)', fontFamily: UI }}>
    <div style={{ height: SH_BAR, background: '#1f6f50', color: '#fff', display: 'flex', alignItems: 'center', gap: 14, padding: '0 22px', fontSize: 25 }}>
      <span style={{ background: '#fff', color: '#1f6f50', fontWeight: 900, borderRadius: 6, padding: '1px 9px', fontSize: 22 }}>X</span>
      <b>{title}</b>
      <span style={{ marginLeft: 'auto', fontWeight: 700, opacity: 0.95 }}>{count}</span>
    </div>
    <div style={{ display: 'flex', height: SH_HEAD, background: '#f2f4f3', borderBottom: '2px solid #1f6f50' }}>
      {COLS.map((c, ci) => (
        <div key={c.n} style={{ width: c.w, padding: '0 16px', display: 'flex', alignItems: 'center', fontWeight: 800, fontSize: 24,
          color: '#18201c', borderRight: '1px solid #e1e5e3', background: ci === hotCol ? '#fde68a' : 'transparent' }}>{c.n}</div>
      ))}
    </div>
    <div style={{ position: 'relative', height: h - SH_BAR - SH_HEAD, overflow: 'hidden' }}>
      <div style={{ transform: `translateY(${-scroll}px)` }}>
        {rows.map((r) => {
          const a = rowIn(r); if (a <= 0) return <div key={r} style={{ height: ROW_H }} />;
          const [name, city, phone] = CO[r % CO.length];
          const cells = [name, city, phone, site(name)];
          return (
            <div key={r} style={{ display: 'flex', height: ROW_H, borderBottom: '1px solid #eef0ef', opacity: Math.min(1, a * 1.3),
              transform: `translateX(${(1 - a) * 40}px)`, background: r % 2 ? '#fafbfa' : '#fff' }}>
              {cells.map((c, ci) => (
                <div key={ci} style={{ width: COLS[ci].w, padding: '0 16px', display: 'flex', alignItems: 'center', fontSize: 24,
                  color: ci === 3 ? '#4338ca' : '#26302b', fontWeight: ci === 0 ? 700 : 500, whiteSpace: 'nowrap', overflow: 'hidden',
                  borderRight: '1px solid #eef0ef' }}><span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{c}</span></div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
    {stamp > 0 ? (
      <div style={{ position: 'absolute', right: 26, top: SH_BAR + SH_HEAD + 22, transform: `rotate(-6deg) scale(${stamp})`,
        padding: '12px 22px', borderRadius: 14, border: `4px solid ${MINT}`, color: '#047857', background: 'rgba(236,253,245,.95)',
        fontWeight: 900, fontSize: 34, letterSpacing: 1 }}>✓ 412 COMPANIES</div>
    ) : null}
  </div>
);

// ------------------------------------------------------------------ 2. problem: copied by hand
const CYCLES = [[6.25, 1.0], [7.25, 0.9], [8.15, 0.78], [8.93, 0.68], [9.61, 0.6]];  // [start, length]
const rowPos = (r: number) => ({ x: SH0.x + 140, y: SH0.y + SH_BAR + SH_HEAD + r * ROW_H + ROW_H / 2 });
function problemCursor(t: number) {
  const home = { x: 1000, y: 1700 };
  const card = (k: number) => { const p = cardPos(k); return { x: p.x + 120, y: p.y + 44 }; };
  if (t < CYCLES[0][0]) {
    const p = lin(t, [5.6, CYCLES[0][0]], [0, 1], Easing.inOut(Easing.cubic));
    const c = card(0); return { x: home.x + (c.x - home.x) * p, y: home.y + (c.y - home.y) * p };
  }
  for (let i = CYCLES.length - 1; i >= 0; i--) {
    const [c0, d] = CYCLES[i];
    if (t < c0) continue;
    const from = i === 0 ? card(0) : rowPos(i - 1), to = card(i), row = rowPos(i);
    const a = lin(t, [c0, c0 + 0.28 * d], [0, 1], Easing.inOut(Easing.cubic));
    const b = lin(t, [c0 + 0.42 * d, c0 + 0.7 * d], [0, 1], Easing.inOut(Easing.cubic));
    const p1 = { x: from.x + (to.x - from.x) * a, y: from.y + (to.y - from.y) * a };
    return { x: p1.x + (row.x - p1.x) * b, y: p1.y + (row.y - p1.y) * b };
  }
  return card(0);
}

const Stage: React.FC = () => {
  const t = useT();
  const inProblem = inWin(t, T.problem, 0.3), inAnswer = t >= T.answer[0] - 0.2 && t < T.cta[0] + 0.3;
  if (!inProblem && !inAnswer) return null;

  if (inProblem) {
    const enter = sp(t, 2.55, 17);
    const leave = lin(t, [10.25, 10.6], [0, 1], Easing.in(Easing.cubic));
    const sheetIn = sp(t, 5.75, 17);
    const sel = (k: number) => { const c = CYCLES[k]; return c ? lin(t, [c[0] + 0.12 * c[1], c[0] + 0.3 * c[1]], [0, 1]) : 0; };
    const rowIn = (r: number) => { const c = CYCLES[r]; return c ? sp(t, c[0] + 0.75 * c[1], 15) : 0; };
    const copied = CYCLES.filter((c) => t >= c[0] + 0.75 * c[1]).length;
    const hot = lin(t, [9.75, 9.95, 10.3], [0, 1, 0.8]);
    // the columns light up as they are named
    const hotCol = t >= wordAt('problem2', 6) ? 3 : t >= wordAt('problem2', 4) ? 2 : t >= wordAt('problem2', 3) ? 0 : -1;
    const hotOn = t < wordAt('problem2', 7) + 0.1 ? hotCol : -1;
    const cur = problemCursor(t);
    const caps: React.ReactNode[] = [];
    CYCLES.forEach(([c0, d], i) => {
      const cc = c0 + 0.3 * d, vv = c0 + 0.75 * d;
      const s1 = lin(t, [cc, cc + 0.08, cc + 0.3, cc + 0.4], [0, 1.08, 1, 0]);
      const s2 = lin(t, [vv, vv + 0.08, vv + 0.3, vv + 0.4], [0, 1.08, 1, 0]);
      const p = cardPos(i), r = rowPos(i);
      if (s1 > 0) caps.push(<Keycap key={'c' + i} label="Ctrl C" x={p.x + CARD.w - 40} y={p.y - 20} s={s1} />);
      if (s2 > 0) caps.push(<Keycap key={'v' + i} label="Ctrl V" x={r.x + 520} y={r.y - 50} s={s2} />);
    });
    // the clock races while the rows crawl in
    const mins = Math.round(lin(t, [6.2, 10.2], [0, 160], Easing.in(Easing.quad)));
    const clock = sp(t, 6.4, 15);
    const shake = Math.sin(t * 60) * 6 * lin(t, [9.8, 9.9, 10.2], [0, 1, 0]);
    return (
      <AbsoluteFill style={{ opacity: 1 - leave, transform: `scale(${1 - leave * 0.12}) translateX(${shake}px)`, filter: `blur(${leave * 10}px)` }}>
        <div style={{ position: 'absolute', left: BR.x, top: BR.y, transform: `translateY(${(1 - enter) * 900}px)` }}>
          <Browser page={1} slide={0} outline={() => 0} selected={sel} pagerHot={hot} badge={0} />
        </div>
        <div style={{ position: 'absolute', left: SH0.x, top: SH0.y, transform: `translateY(${(1 - sheetIn) * 900}px)` }}>
          <Sheet w={SH0.w} h={SH0.h} title="Untitled spreadsheet" rows={[0, 1, 2, 3, 4, 5]} rowIn={rowIn} scroll={0} hotCol={hotOn} />
        </div>
        {clock > 0 ? (
          <div style={{ position: 'absolute', left: '50%', top: 1018, transform: `translateX(-50%) scale(${clock}) rotate(${Math.sin(t * 40) * (mins > 120 ? 3 : 0)}deg)`,
            padding: '10px 22px', borderRadius: 999, background: mins > 120 ? '#ef4444' : '#17142a', color: '#fff', fontFamily: UI,
            fontWeight: 800, fontSize: 32, boxShadow: '0 14px 30px -10px rgba(0,0,0,.6)', zIndex: 40, whiteSpace: 'nowrap',
            fontVariantNumeric: 'tabular-nums' }}>
            ⏱ {Math.floor(mins / 60)}h {String(mins % 60).padStart(2, '0')}m · {copied} of 412 copied
          </div>
        ) : null}
        {caps}
        {t > 5.55 ? <Cursor x={cur.x} y={cur.y} press={caps.length ? 1 : 0} /> : null}
      </AbsoluteFill>
    );
  }

  // ---- the answer: the same page, one click, every page, one sheet
  const enter = sp(t, 13.3, 16);
  const outline = (k: number) => sp(t, 13.65 + k * 0.1, 14);
  const badge = sp(t, 14.35, 12);
  const fly0 = 14.45;                                       // rows leave the cards for the sheet
  const flipStart = 15.35, flipEnd = 17.25;
  const pf = lin(t, [flipStart, flipEnd], [0, 1], Easing.inOut(Easing.quad));
  const page = t < flipStart ? 1 : Math.min(PAGES, 1 + Math.floor(pf * (PAGES - 1) + 0.0001));
  const pageFrac = t < flipStart ? 0 : (pf * (PAGES - 1)) % 1;
  const slide = t < flipStart || page >= PAGES ? 0 : -pageFrac * 120;
  const count = t < flipStart ? [0, 1, 2, 3, 4, 5].filter((r) => t >= fly0 + r * 0.1 + 0.36).length : Math.round(6 + pf * (TOTAL_ROWS - 6));
  // the list: the page leaves and the sheet takes the screen
  const L = lin(t, [17.6, 18.15], [0, 1], Easing.inOut(Easing.cubic));
  const leave = lin(t, [20.45, 20.75], [0, 1], Easing.in(Easing.cubic));
  const sh = { y: SH0.y + (470 - SH0.y) * L, h: SH0.h + (1030 - SH0.h) * L };
  const visible = Math.floor((sh.h - SH_BAR - SH_HEAD) / ROW_H) + 1;
  // While the pages flip, the newest rows are kept at the bottom; in the list, back to the top and drift down.
  const listScroll = lin(t, [18.6, 20.6], [0, ROW_H * 3], Easing.inOut(Easing.quad));
  const firstRow = L > 0 ? 0 : Math.max(0, count - 6);
  const rows = Array.from({ length: visible + 4 }, (_, j) => firstRow + j);
  const rowIn = (r: number) => {
    if (L > 0) return 1;
    if (r < 6) return t < fly0 ? 0 : sp(t, fly0 + r * 0.1 + 0.32, 15);
    return r < count ? 1 : 0;
  };
  const stamp = sp(t, 17.75, 11);
  const ghosts = t >= fly0 && t < fly0 + 1.2 ? Array.from({ length: 6 }, (_, k) => {
    const p = lin(t, [fly0 + k * 0.1, fly0 + k * 0.1 + 0.36], [0, 1], Easing.inOut(Easing.cubic));
    if (p <= 0 || p >= 1) return null;
    const a = cardPos(k), b = { x: SH0.x + 16, y: SH0.y + SH_BAR + SH_HEAD + k * ROW_H + 6 };
    const x = a.x + (b.x - a.x) * p, y = a.y + (b.y - a.y) * p - Math.sin(p * Math.PI) * 140;
    return (
      <div key={k} style={{ position: 'absolute', left: x, top: y, padding: '10px 18px', borderRadius: 12, background: BLUE, color: '#fff',
        fontFamily: UI, fontWeight: 800, fontSize: 24, whiteSpace: 'nowrap', boxShadow: '0 16px 30px -10px rgba(59,130,246,.8)',
        transform: `scale(${1 - 0.15 * Math.sin(p * Math.PI)})`, zIndex: 30 }}>{CO[k][0]}</div>
    );
  }) : null;
  const counterS = sp(t, 15.3, 14);
  return (
    <AbsoluteFill style={{ opacity: Math.min(1, enter * 1.4) * (1 - leave), transform: `scale(${(0.92 + 0.08 * enter) * (1 - leave * 0.1)})` }}>
      <div style={{ position: 'absolute', left: BR.x, top: BR.y, opacity: 1 - L, transform: `translateY(${-L * 260}px) scale(${1 - L * 0.08})` }}>
        <Browser page={page} slide={slide} outline={t < flipStart ? outline : () => 1} selected={() => 0} pagerHot={0} badge={badge} />
      </div>
      <div style={{ position: 'absolute', left: SH0.x, top: sh.y }}>
        <Sheet w={SH0.w} h={sh.h} title="partners.xlsx" rows={rows} rowIn={rowIn}
          scroll={L > 0 ? listScroll : 0} count={counterS > 0 && L < 0.5 ? '' : `${count} rows`} stamp={stamp} />
      </div>
      {ghosts}
      {counterS > 0 && L < 1 ? (
        <div style={{ position: 'absolute', left: 0, right: 84, top: 1044, display: 'flex', justifyContent: 'flex-end', gap: 14,
          transform: `scale(${counterS})`, transformOrigin: '100% 50%', opacity: 1 - L, zIndex: 35 }}>
          {[`Page ${page} / ${PAGES}`, `${count} companies`].map((s, i) => (
            <div key={i} style={{ padding: '10px 26px', borderRadius: 999, background: i ? VIOLET : '#fff', color: i ? '#fff' : INK,
              fontFamily: UI, fontWeight: 900, fontSize: 30, boxShadow: '0 16px 30px -12px rgba(0,0,0,.7)',
              fontVariantNumeric: 'tabular-nums' }}>{s}</div>
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// Captions over the stage, in the band at the top.
const Captions: React.FC = () => {
  const t = useT();
  const band = (k: string, lines: string[][], from: number, to: number, opts: any = {}) => {
    if (t < from || t >= to) return null;
    const o = lin(t, [to - 0.18, to], [1, 0]);
    return (
      <div key={k} style={{ position: 'absolute', left: 50, right: 50, top: 210, height: 240, display: 'flex', flexDirection: 'column',
        justifyContent: 'center', opacity: o }}>
        <Spoken k={k} lines={lines} size={opts.size || 66} {...opts} />
      </div>
    );
  };
  return (
    <>
      {band('problem1', [['You', 'found', 'the', 'perfect'], ['directory.'], ['400', 'companies.']], 2.7, VO.problem2 - 0.1, { hi: [5, 6] })}
      {band('problem2', [["Now", "you're", 'copying'], ['names,', 'phones', 'and', 'websites…'], ['one', 'by', 'one.']], VO.problem2 - 0.05, 10.35,
        { hi: [3, 4, 6], size: 62 })}
      {band('answer1', [['Every', 'company,'], ['on', 'every', 'page,'], ['in', 'one', 'spreadsheet.']], 13.4, T.list[0], { hi: [7] , marker: []})}
      {band('answer2', [['Your', 'outreach', 'list', 'is', 'ready'], ['before', 'lunch.']], T.list[0], 20.55, { marker: [5, 6] })}
    </>
  );
};

// ------------------------------------------------------------------ 3. rehook and the click
const Rehook: React.FC = () => {
  const t = useT();
  if (!inWin(t, T.rehook, 0.05)) return null;
  const shake = Math.sin(t * 70) * lin(t, [11.2, 11.9], [0, 7]);
  const out = lin(t, [11.86, 11.98], [0, 1]);
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', opacity: 1 - out, transform: `translateX(${shake}px) scale(${1 + lin(t, [10.5, 11.95], [0, 0.08])})` }}>
      <div style={{ width: 960, marginTop: -120 }}>
        <Spoken k="rehook" lines={[["There's", 'a'], ['faster', 'way.']]} size={150} font={HEAD} weight={650} hi={[2, 3]} lineHeight={1.05} />
      </div>
    </AbsoluteFill>
  );
};
const Click: React.FC = () => {
  const t = useT();
  if (!inWin(t, T.click, 0.1)) return null;
  const pop = sp(t, 11.98, 10, 0.6);
  const cx = 540, cy = 820;
  const cp = lin(t, [11.98, 12.06], [0, 1], Easing.out(Easing.cubic));
  const press = lin(t, [12.03, 12.06, 12.16], [0, 1, 0]);
  const out = lin(t, [13.1, 13.35], [0, 1], Easing.in(Easing.cubic));
  return (
    <AbsoluteFill style={{ opacity: 1 - out, transform: `scale(${1 + out * 0.6})` }}>
      {[0, 1, 2].map((i) => {
        const r = lin(t, [12.05 + i * 0.12, 12.85 + i * 0.12], [0, 1], Easing.out(Easing.cubic));
        return r > 0 && r < 1 ? <div key={i} style={{ position: 'absolute', left: cx, top: cy, width: 900 * r, height: 900 * r,
          marginLeft: -450 * r, marginTop: -450 * r, borderRadius: '50%', border: `${10 * (1 - r)}px solid ${SOFT}`, opacity: 1 - r }} /> : null;
      })}
      <div style={{ position: 'absolute', left: cx - 130, top: cy - 130, transform: `scale(${pop * (1 - press * 0.12)})` }}><Mark size={260} glow={1.4} /></div>
      <Cursor x={cx + 40 + (1 - cp) * 380} y={cy + 30 + (1 - cp) * 520} press={press} size={110} />
      <div style={{ position: 'absolute', left: 0, right: 0, top: 1080 }}>
        <Spoken k="click" lines={[['One', 'click.']]} size={132} font={HEAD} weight={650} />
      </div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ 4. call to action
const Cta: React.FC = () => {
  const t = useT();
  if (t < T.cta[0] - 0.05) return null;
  const a = sp(t, 20.75, 12);
  const name = sp(t, wordAt('cta', 0) - 0.05, 16);
  const free = sp(t, wordAt('cta', 2) - 0.05, 14);
  const noAcc = sp(t, wordAt('cta', 7) - 0.05, 14);
  const data = sp(t, wordAt('cta', 8) + 0.25, 14);
  const url = sp(t, voEnd('cta') - 0.3, 16);
  const line = lin(t, [voEnd('cta') - 0.15, voEnd('cta') + 0.35], [0, 1], Easing.out(Easing.cubic));
  const hint = sp(t, voEnd('cta') + 0.5, 18);
  const pill = (txt: string, s: number, solid = false) => (
    <div style={{ transform: `translateY(${(1 - s) * 40}px) scale(${0.9 + 0.1 * s})`, opacity: Math.min(1, s * 1.4), padding: '18px 34px',
      borderRadius: 999, fontFamily: UI, fontSize: 38, fontWeight: solid ? 800 : 600, background: solid ? '#fff' : 'rgba(255,255,255,.06)',
      color: solid ? INK : '#ece9f8', border: solid ? '2px solid #fff' : '2px solid rgba(255,255,255,.28)' }}>{txt}</div>
  );
  return (
    <AbsoluteFill style={{ alignItems: 'center', fontFamily: UI, color: '#fff' }}>
      <div style={{ marginTop: 430, transform: `scale(${a}) rotate(${(1 - a) * -20}deg)` }}><Mark size={190} /></div>
      <div style={{ marginTop: 50, fontFamily: HEAD, fontWeight: 650, fontSize: 132, letterSpacing: -4, lineHeight: 1,
        opacity: name, transform: `translateY(${(1 - name) * 40}px)` }}>Magic Scraper</div>
      <div style={{ marginTop: 26, fontSize: 44, color: '#d5cfee', opacity: name }}>Any directory, into your partner list.</div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20, marginTop: 64 }}>
        {pill('Free for Chrome & Edge', free, true)}
        <div style={{ display: 'flex', gap: 18 }}>{pill('No account', noAcc)}{pill('Data stays on your computer', data)}</div>
      </div>
      <div style={{ marginTop: 74, position: 'relative', opacity: url, transform: `scale(${0.9 + 0.1 * url})` }}>
        <div style={{ fontFamily: 'ui-monospace, Menlo, monospace', fontSize: 64, fontWeight: 700, color: SOFT }}>magicscraper.app</div>
        <div style={{ height: 6, borderRadius: 3, background: SOFT, marginTop: 8, transform: `scaleX(${line})`, transformOrigin: '0 50%' }} />
      </div>
      <div style={{ marginTop: 34, fontSize: 32, color: '#a9a3c4', opacity: hint, transform: `translateY(${(1 - hint) * 20}px)` }}>
        or search “Magic Scraper” in the Chrome Web Store</div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ sound
// [effect, second, volume]
const SFX: [string, number, number][] = [
  ['pop', 0.08, 0.5], ...[0, 1, 2, 3, 4, 5].map((i) => ['pop', 0.12 + i * 0.09, 0.22] as [string, number, number]),
  ['whoosh', 2.4, 0.7], ['pop', wordAt('problem1', 5), 0.5], ['whoosh', 5.7, 0.45],
  ...CYCLES.flatMap(([c0, d]) => [['key', c0 + 0.3 * d, 0.9], ['key', c0 + 0.75 * d, 0.9], ['pop', c0 + 0.78 * d, 0.3]] as [string, number, number][]),
  ['tick', 9.8, 0.8], ['whoosh', 10.3, 0.6],
  ['click', 12.04, 1.0], ['impact', 12.04, 0.9],
  ['whoosh', 13.2, 0.6], ...[0, 1, 2, 3, 4, 5].map((k) => ['tick', 13.65 + k * 0.1, 0.5] as [string, number, number]),
  ...[0, 1, 2, 3, 4, 5].map((k) => ['pop', 14.45 + k * 0.1 + 0.34, 0.3] as [string, number, number]),
  ['whoosh', 15.3, 0.35], ['ding', 17.75, 0.75], ['whoosh', 17.6, 0.45],
  ['whoosh', 20.5, 0.6], ['pop', 20.78, 0.6], ['pop', voEnd('cta') - 0.3, 0.5],
];
const LINES = ['hook', 'problem1', 'problem2', 'rehook', 'click', 'answer1', 'answer2', 'cta'];

export const Short: React.FC<{ voice: boolean }> = ({ voice }) => {
  const bed = (fr: number) => {
    const t = fr / FPS;
    let duck = 0;
    if (voice) for (const k of LINES) {
      const a = VO[k], z = voEnd(k);
      duck = Math.max(duck, Math.min(1, Math.max(0, Math.min(t - (a - 0.15), (z + 0.25) - t) / 0.15)));
    }
    return (voice ? 0.62 - 0.3 * duck : 0.8) * Math.min(1, (TOTAL - t) / 0.8);
  };
  return (
    <AbsoluteFill style={{ background: INK }}>
      <Fonts />
      <Backdrop />
      <Hook />
      <Stage />
      <Captions />
      <Rehook />
      <Click />
      <Cta />
      <Audio src={staticFile('bed.wav')} volume={bed} />
      {SFX.map(([name, at, vol], i) => (
        <Sequence key={i} from={Math.max(0, Math.round(at * FPS))} durationInFrames={Math.round(1.3 * FPS)}>
          <Audio src={staticFile(`sfx/${name}.wav`)} volume={vol * (voice ? 0.8 : 1)} />
        </Sequence>
      ))}
      {voice ? LINES.map((k) => (
        <Sequence key={k} from={Math.round(VO[k] * FPS)} durationInFrames={Math.ceil((WJ[k].dur + 0.2) * FPS)}>
          <Audio src={staticFile(`vo/${k}.wav`)} volume={1} />
        </Sequence>
      )) : null}
    </AbsoluteFill>
  );
};
