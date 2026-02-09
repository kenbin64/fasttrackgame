/**
 * ObjectSystem - Structural Role and Object Hierarchy
 * 
 * Defines how pixels relate to objects and structure.
 */

/**
 * Structural role type
 */
export enum StructuralRoleType {
  VERTEX = 'vertex',
  EDGE = 'edge',
  FACE = 'face',
  INTERIOR = 'interior',
  BOUNDARY = 'boundary',
}

/**
 * Structural role for a pixel
 */
export interface StructuralRole {
  /**
   * Role type
   */
  roleType: StructuralRoleType;
  
  /**
   * Object ID this pixel belongs to
   */
  objectID: bigint;
  
  /**
   * Local coordinates within object
   */
  localCoordinates: [number, number, number];
  
  /**
   * Surface normal vector (for lighting)
   */
  normalVector: [number, number, number];
}

/**
 * Create default structural role
 */
export function createDefaultStructuralRole(objectID: bigint = 0n): StructuralRole {
  return {
    roleType: StructuralRoleType.FACE,
    objectID,
    localCoordinates: [0, 0, 0],
    normalVector: [0, 0, 1], // Facing camera
  };
}

