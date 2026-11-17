import { createContext, useContext } from 'react';
import { Timeline } from './types';

export const TimelineCtx = createContext<Timeline | null>(null);
export const useTimeline = (): Timeline => {
  const t = useContext(TimelineCtx);
  if (!t) throw new Error('useTimeline outside TimelineCtx');
  return t;
};
