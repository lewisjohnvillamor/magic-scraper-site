/* G2 profile banner, 1270x240: a looping animation (exported as a GIF) and a
   still. Rows leave a directory page and land in a spreadsheet, beside the
   one-line promise. The loop is LOOP seconds and ends where it begins. */
import React from 'react';
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame } from 'remotion';

export const BANNER_FPS = 15;
export const LOOP = 4;
const INK = '#0d0b16', VIOLET = '#6d5cf0', SOFT = '#b4a2ff', BLUE = '#3b82f6';
const UI = 'Archivo, Inter, system-ui, sans-serif', HEAD = 'Fraunces, Georgia, serif';
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const ease = Easing.inOut(Easing.cubic);

const ROWS: [string, string, string, number][] = [
  ['Halden Logistics', 'Leeds', '555-0142', 262], ['Brightwater Foods', 'Austin', '555-0187', 200],
  ['Northgate Packaging', 'Toronto', '555-0119', 152], ['Copperline Electrical', 'Denver', '555-0164', 28],
];
const PAGE = { x: 640, y: 34, w: 250, h: 172 };
const SHEET = { x: 958, y: 34, w: 282, h: 172 };
const CARD_H = 34, ROW_H = 30;

const Mark: React.FC<{ size: number }> = ({ size }) => (
  <div style={{ width: size, height: size, borderRadius: size * 0.27, display: 'flex', alignItems: 'center', justifyContent: 'center',
    background: 'linear-gradient(145deg, #5b4bd6, #8b5cf6)', boxShadow: `0 ${size * 0.15}px ${size * 0.5}px -${size * 0.1}px rgba(139,92,246,.9)` }}>
    <svg viewBox="0 0 24 24" width={size * 0.52} height={size * 0.52} fill="none" stroke="#fff" strokeWidth={2.4}
      strokeLinecap="round" strokeLinejoin="round"><path d="M4 20 L14 10" /><path d="M18 3 v5 M15.5 5.5 h5" /></svg>
  </div>
);

export const Banner: React.FC = () => {
  const t = useCurrentFrame() / BANNER_FPS;
  // each row: outlined on the page, flies over, lands in the sheet; all fade out together at the end of the loop
  const land = (i: number) => 0.5 + i * 0.55;
  const fade = interpolate(t, [LOOP - 0.45, LOOP - 0.05], [1, 0], clamp);
  const count = ROWS.filter((_, i) => t >= land(i) + 0.45).length;
  return (
    <AbsoluteFill style={{ background: INK, overflow: 'hidden', fontFamily: UI }}>
      <style>{`
        @font-face { font-family: 'Fraunces'; src: url('${staticFile('fonts/fraunces-var.woff2')}') format('woff2'); font-weight: 100 900; }
        @font-face { font-family: 'Archivo'; src: url('${staticFile('fonts/archivo-var.woff2')}') format('woff2'); font-weight: 100 900; }
      `}</style>
      <div style={{ position: 'absolute', left: -200, top: -520, width: 1100, height: 1100, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(139,92,246,.38) 0%, rgba(91,75,214,.12) 42%, transparent 68%)' }} />
      <div style={{ position: 'absolute', right: -260, top: -380, width: 900, height: 900, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(56,189,248,.14) 0%, transparent 62%)' }} />
      <div style={{ position: 'absolute', inset: 0, opacity: 0.18,
        backgroundImage: 'radial-gradient(rgba(255,255,255,.4) 1.2px, transparent 1.4px)', backgroundSize: '26px 26px' }} />

      {/* the promise */}
      <div style={{ position: 'absolute', left: 54, top: 40, color: '#fff' }}>
        <div style={{ fontFamily: HEAD, fontWeight: 650, fontSize: 46, lineHeight: 1.06, letterSpacing: -1.5 }}>
          Any web page, into a<br />
          <span style={{ position: 'relative', zIndex: 1 }}>
            <span style={{ position: 'absolute', left: -8, right: -8, top: '14%', bottom: '2%', background: VIOLET, borderRadius: 10, zIndex: -1 }} />
            clean spreadsheet.</span>
        </div>
        <div style={{ marginTop: 22, display: 'flex', gap: 10, fontSize: 17, fontWeight: 700 }}>
          {['Free for Chrome & Edge', 'No account', 'Excel · CSV · JSON'].map((p, i) => (
            <span key={p} style={{ padding: '7px 14px', borderRadius: 999, background: i ? 'rgba(255,255,255,.07)' : '#fff',
              color: i ? '#e6e2f6' : INK, border: i ? '1.5px solid rgba(255,255,255,.25)' : '1.5px solid #fff' }}>{p}</span>
          ))}
        </div>
      </div>

      {/* the page */}
      <div style={{ position: 'absolute', left: PAGE.x, top: PAGE.y, width: PAGE.w, height: PAGE.h, borderRadius: 12, background: '#fff',
        overflow: 'hidden', boxShadow: '0 20px 40px -16px rgba(0,0,0,.8)' }}>
        <div style={{ height: 22, background: '#eceaf3', display: 'flex', alignItems: 'center', gap: 5, padding: '0 9px' }}>
          {['#ff5f57', '#febc2e', '#28c840'].map((c) => <span key={c} style={{ width: 7, height: 7, borderRadius: 4, background: c }} />)}
          <span style={{ marginLeft: 6, fontSize: 10, color: '#6f6a85' }}>Member directory</span>
        </div>
        {ROWS.map(([name, city, , hue], i) => {
          const o = interpolate(t, [land(i) - 0.35, land(i) - 0.15], [0, 1], clamp) * fade;
          return (
            <div key={i} style={{ position: 'absolute', left: 8, right: 8, top: 28 + i * (CARD_H + 2), height: CARD_H, borderRadius: 7,
              display: 'flex', alignItems: 'center', gap: 8, padding: '0 8px', border: `${o > 0.05 ? 2 : 1}px solid ${o > 0.05 ? BLUE : '#e7e4ef'}`,
              background: `rgba(59,130,246,${0.1 * o})` }}>
              <span style={{ width: 20, height: 20, borderRadius: 10, background: `hsl(${hue} 70% 90%)`, flex: 'none' }} />
              <div style={{ lineHeight: 1.1 }}>
                <div style={{ fontSize: 12, fontWeight: 800, color: '#17142a' }}>{name}</div>
                <div style={{ fontSize: 10, color: '#6f6a85' }}>{city}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* the click between them */}
      <div style={{ position: 'absolute', left: (PAGE.x + PAGE.w + SHEET.x) / 2 - 27, top: 93,
        transform: `scale(${1 + 0.08 * Math.max(0, Math.sin(t * Math.PI * 2 / LOOP * 4))})` }}><Mark size={54} /></div>

      {/* the sheet */}
      <div style={{ position: 'absolute', left: SHEET.x, top: SHEET.y, width: SHEET.w, height: SHEET.h, borderRadius: 12, background: '#fff',
        overflow: 'hidden', boxShadow: '0 20px 40px -16px rgba(0,0,0,.8)' }}>
        <div style={{ height: 24, background: '#1f6f50', color: '#fff', display: 'flex', alignItems: 'center', gap: 6, padding: '0 9px', fontSize: 11 }}>
          <b style={{ background: '#fff', color: '#1f6f50', borderRadius: 3, padding: '0 4px', fontSize: 10 }}>X</b>
          <b>partners.xlsx</b><span style={{ marginLeft: 'auto', fontWeight: 700 }}>{count} rows</span>
        </div>
        <div style={{ display: 'flex', height: 22, background: '#f2f4f3', borderBottom: '1.5px solid #1f6f50', fontSize: 11, fontWeight: 800, color: '#18201c' }}>
          {[['Company', 136], ['City', 70], ['Phone', 76]].map(([n, w]) => (
            <div key={n as string} style={{ width: w as number, padding: '0 8px', display: 'flex', alignItems: 'center' }}>{n}</div>
          ))}
        </div>
        {ROWS.map(([name, city, phone], i) => {
          const a = interpolate(t, [land(i) + 0.35, land(i) + 0.55], [0, 1], clamp) * fade;
          return (
            <div key={i} style={{ display: 'flex', height: ROW_H, borderBottom: '1px solid #eef0ef', fontSize: 11.5, color: '#26302b', opacity: a,
              transform: `translateX(${(1 - a) * 14}px)` }}>
              <div style={{ width: 136, padding: '0 8px', display: 'flex', alignItems: 'center', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden' }}>{name}</div>
              <div style={{ width: 70, padding: '0 8px', display: 'flex', alignItems: 'center' }}>{city}</div>
              <div style={{ width: 76, padding: '0 8px', display: 'flex', alignItems: 'center' }}>{phone}</div>
            </div>
          );
        })}
      </div>

      {/* rows in flight */}
      {ROWS.map(([name], i) => {
        const p = interpolate(t, [land(i) - 0.15, land(i) + 0.4], [0, 1], { ...clamp, easing: ease });
        if (p <= 0 || p >= 1) return null;
        const ax = PAGE.x + 30, ay = PAGE.y + 30 + i * (CARD_H + 2), bx = SHEET.x + 8, by = SHEET.y + 48 + i * ROW_H;
        return (
          <div key={i} style={{ position: 'absolute', left: ax + (bx - ax) * p, top: ay + (by - ay) * p - Math.sin(p * Math.PI) * 42,
            padding: '4px 10px', borderRadius: 7, background: BLUE, color: '#fff', fontSize: 12, fontWeight: 800, whiteSpace: 'nowrap',
            boxShadow: '0 8px 18px -6px rgba(59,130,246,.9)' }}>{name}</div>
        );
      })}
      <div style={{ position: 'absolute', right: 30, bottom: 10, fontFamily: 'ui-monospace, Menlo, monospace', fontSize: 13, color: SOFT, opacity: 0.9 }}>magicscraper.app</div>
    </AbsoluteFill>
  );
};
