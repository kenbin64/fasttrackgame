/**
 * AnimationSystem - Animation State for Pixels
 * 
 * For static images, this is minimal.
 * Ready for future animation support.
 */

/**
 * Easing function type
 */
export type EasingFunction = (t: number) => number;

/**
 * Common easing functions
 */
export const Easing = {
  linear: (t: number) => t,
  easeIn: (t: number) => t * t,
  easeOut: (t: number) => t * (2 - t),
  easeInOut: (t: number) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t,
};

/**
 * Animation state for a pixel
 */
export interface AnimationState {
  /**
   * Current keyframe phase [0-1]
   */
  keyframePhase: number;
  
  /**
   * Easing curve
   */
  easingCurve: EasingFunction;
  
  /**
   * Is animating?
   */
  isAnimating: boolean;
}

/**
 * Create default animation state
 */
export function createDefaultAnimationState(): AnimationState {
  return {
    keyframePhase: 0,
    easingCurve: Easing.linear,
    isAnimating: false,
  };
}

