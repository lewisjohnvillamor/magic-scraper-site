import React from 'react';
import { Composition } from 'remotion';
import { Short, Thumb, FPS, TOTAL } from './Short';
import { Banner, BANNER_FPS, LOOP } from './Banner';
// Two cuts of the same film: captions, music and effects only, or with the voice.
export const Root: React.FC = () => (
  <>
    <Composition id="ShortText" component={Short} defaultProps={{ voice: false }}
      durationInFrames={Math.round(TOTAL * FPS)} fps={FPS} width={1080} height={1920} />
    <Composition id="ShortVoice" component={Short} defaultProps={{ voice: true }}
      durationInFrames={Math.round(TOTAL * FPS)} fps={FPS} width={1080} height={1920} />
    <Composition id="Banner" component={Banner} durationInFrames={LOOP * BANNER_FPS} fps={BANNER_FPS} width={1270} height={240} />
    <Composition id="Thumb" component={Thumb} durationInFrames={1} fps={FPS} width={1080} height={1920} />
  </>
);
