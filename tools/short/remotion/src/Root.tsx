import React from 'react';
import { Composition } from 'remotion';
import { Short, FPS, TOTAL } from './Short';
// Two cuts of the same film: captions, music and effects only, or with the voice.
export const Root: React.FC = () => (
  <>
    <Composition id="ShortText" component={Short} defaultProps={{ voice: false }}
      durationInFrames={Math.round(TOTAL * FPS)} fps={FPS} width={1080} height={1920} />
    <Composition id="ShortVoice" component={Short} defaultProps={{ voice: true }}
      durationInFrames={Math.round(TOTAL * FPS)} fps={FPS} width={1080} height={1920} />
  </>
);
