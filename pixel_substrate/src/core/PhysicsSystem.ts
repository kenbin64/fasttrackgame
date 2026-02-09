/**
 * PhysicsSystem - Physics State and Motion for Pixels
 * 
 * Defines physical properties and motion for pixels.
 * For static images, this is simplified but ready for animation.
 */

/**
 * Physics state for a pixel
 */
export interface PhysicsState {
  // ========================================
  // POSITION & MOTION
  // ========================================
  
  /**
   * Position in 3D space [x, y, z]
   */
  position: [number, number, number];
  
  /**
   * Velocity [vx, vy, vz] (units/second)
   */
  velocity: [number, number, number];
  
  /**
   * Acceleration [ax, ay, az] (units/second²)
   */
  acceleration: [number, number, number];
  
  // ========================================
  // MASS & FORCES
  // ========================================
  
  /**
   * Mass (kg)
   */
  mass: number;
  
  /**
   * Applied forces [fx, fy, fz] (Newtons)
   */
  forces: [number, number, number];
  
  // ========================================
  // MOTION PLANNING
  // ========================================
  
  /**
   * Next position (for animation)
   */
  nextPosition: [number, number, number];
  
  /**
   * Time step (seconds)
   */
  timeStep: number;
}

/**
 * Create default physics state
 */
export function createDefaultPhysicsState(
  position: [number, number, number] = [0, 0, 0]
): PhysicsState {
  return {
    position,
    velocity: [0, 0, 0],
    acceleration: [0, 0, 0],
    mass: 1.0,
    forces: [0, 0, 0],
    nextPosition: [...position],
    timeStep: 1.0 / 60.0, // 60 FPS
  };
}

/**
 * Apply forces to update acceleration
 * F = ma, so a = F/m
 */
export function applyForces(state: PhysicsState): void {
  const [fx, fy, fz] = state.forces;
  const m = state.mass;
  
  state.acceleration = [fx / m, fy / m, fz / m];
}

/**
 * Integrate motion using Euler method
 * Simple but sufficient for most cases
 */
export function integrateMotion(state: PhysicsState): void {
  const dt = state.timeStep;
  const [vx, vy, vz] = state.velocity;
  const [ax, ay, az] = state.acceleration;
  const [px, py, pz] = state.position;
  
  // Update velocity: v = v + a*dt
  state.velocity = [
    vx + ax * dt,
    vy + ay * dt,
    vz + az * dt,
  ];
  
  // Update position: p = p + v*dt
  state.nextPosition = [
    px + state.velocity[0] * dt,
    py + state.velocity[1] * dt,
    pz + state.velocity[2] * dt,
  ];
}

/**
 * Commit next position to current position
 */
export function commitPosition(state: PhysicsState): void {
  state.position = [...state.nextPosition];
}

