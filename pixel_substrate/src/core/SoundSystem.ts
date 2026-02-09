/**
 * SoundSystem - Sound Interaction for Pixels
 * 
 * For static images, this is minimal.
 * Ready for future sound simulation.
 */

/**
 * Sound interaction state
 */
export interface SoundInteraction {
  /**
   * Incoming sound waves
   */
  incomingSound: any[];
  
  /**
   * Absorbed sound energy
   */
  absorbedSound: number;
}

/**
 * Create default sound interaction
 */
export function createDefaultSoundInteraction(): SoundInteraction {
  return {
    incomingSound: [],
    absorbedSound: 0,
  };
}

