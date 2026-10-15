import React from 'react';
import { Composition } from 'remotion';
import { Walkthrough } from './Walkthrough';
import plan from './plan.json';
export const Root: React.FC = () => (
  <Composition id="Walkthrough" component={Walkthrough} durationInFrames={Math.ceil(plan.total * plan.fps)}
    fps={plan.fps} width={1920} height={1080} />
);
