// CameraController for Brickbreaker 3D
// Keeps ball + paddle in frame, fits with margin, smooths motion, clamps tilt/near/far, avoids wall clipping.
// Requires Three.js loaded globally as THREE

(function(global){
  class CameraController{
    constructor(camera, scene, arenaBounds, opts={}){
      if(!camera) throw new Error('CameraController requires a THREE.PerspectiveCamera');
      this.camera = camera;
      this.scene = scene;
      this.arenaBounds = arenaBounds || { min:new THREE.Vector3(-10,-10,-30), max:new THREE.Vector3(10,10,10) };

      // Options
      this.margin = opts.margin ?? 0.12; // 12%
      this.minFov = opts.minFov ?? 45;
      this.maxFov = opts.maxFov ?? 60;
      this.tiltDeg = THREE.MathUtils.clamp(opts.tiltDeg ?? 15, 5, 45); // camera tilt down toward arena
      this.smoothPos = opts.smoothPos ?? 10.0; // spring stiffness
      this.smoothZoom = opts.smoothZoom ?? 8.0;
      this.near = opts.near ?? 0.1;
      this.far = opts.far ?? 2000;
      this.wallClearance = opts.wallClearance ?? 0.6; // offset from arena walls to avoid clipping
      this.up = new THREE.Vector3(0,1,0);

      this.targetBall = null;
      this.targetPaddle = null;

      // Internal state
      this._targetCenter = new THREE.Vector3();
      this._targetRadius = 1.0;
      this._currentFov = THREE.MathUtils.clamp(camera.fov || 50, this.minFov, this.maxFov);
      this._desiredFov = this._currentFov;
      this._desiredPos = new THREE.Vector3().copy(camera.position);

      // Set camera defaults
      this.camera.fov = this._currentFov;
      this.camera.near = this.near;
      this.camera.far = this.far;
      this.camera.updateProjectionMatrix();

      // Default facing: look from positive Z toward origin with slight tilt down
      this.baseForward = new THREE.Vector3(0, -Math.sin(THREE.MathUtils.degToRad(this.tiltDeg)), -Math.cos(THREE.MathUtils.degToRad(this.tiltDeg)));
      this.baseRight = new THREE.Vector3(1,0,0);

      // Working vars
      this._box = new THREE.Box3();
      this._tmpV = new THREE.Vector3();
      this._arenaBox = new THREE.Box3(
        arenaBounds?.min?.clone?.() || new THREE.Vector3(-10,-10,-30),
        arenaBounds?.max?.clone?.() || new THREE.Vector3(10,10,10)
      );
    }

    setTargets(ballMesh, paddleMesh){
      this.targetBall = ballMesh || null;
      this.targetPaddle = paddleMesh || null;
    }

    setArenaBounds(bounds){
      if(bounds?.min && bounds?.max){
        this._arenaBox.min.copy(bounds.min);
        this._arenaBox.max.copy(bounds.max);
      }
    }

    onResize(w, h){
      if(!this.camera) return;
      this.camera.aspect = Math.max(0.1, w / Math.max(1,h));
      this.camera.updateProjectionMatrix();
    }

    // Compute a bounding sphere for ball + paddle; return center and radius
    _computeFraming(){
      const box = this._box;
      box.makeEmpty();
      if(this.targetBall){ box.expandByObject(this.targetBall); }
      if(this.targetPaddle){ box.expandByObject(this.targetPaddle); }

      if(box.isEmpty()){
        // fallback to arena center small radius
        box.copy(this._arenaBox);
      }

      const center = this._targetCenter;
      const radius = Math.max(0.001, box.getBoundingSphere(new THREE.Sphere()).radius);
      box.getCenter(center);

      // Inflate by margin
      const r = radius * (1 + this.margin);
      this._targetRadius = r;

      // Clamp center within arena with clearance
      center.clamp(
        this._tmpV.copy(this._arenaBox.min).addScalar(this.wallClearance),
        this._tmpV.copy(this._arenaBox.max).addScalar(-this.wallClearance)
      );
    }

    // Fit FOV so that the framing sphere fits within vertical FOV
    _computeDesired(camera){
      // Distance needed so that tan(fov/2) = radius / distance_vertical
      const fovRad = THREE.MathUtils.degToRad(THREE.MathUtils.clamp(camera.fov, this.minFov, this.maxFov));
      const dist = this._targetRadius / Math.tan(fovRad * 0.5);

      // Place camera at base direction from target center
      const dir = this.baseForward; // already normalized approx
      this._desiredPos.copy(this._targetCenter).addScaledVector(dir, dist + 0.001);

      // Keep within arena extents (avoid clipping through walls)
      this._desiredPos.clamp(
        this._tmpV.copy(this._arenaBox.min).addScalar(this.wallClearance),
        this._tmpV.copy(this._arenaBox.max).addScalar(-this.wallClearance)
      );

      // Recompute desired FOV if we are aspect-limited horizontally
      const aspect = Math.max(0.0001, camera.aspect || 1.0);
      const vFov = fovRad;
      const hFov = 2 * Math.atan(Math.tan(vFov/2) * aspect);
      // Ensure sphere also fits horizontally; if not, increase vFov within clamp
      const needsWider = (this._targetRadius / Math.tan(hFov/2)) > (this._targetRadius / Math.tan(vFov/2));
      let desiredFovDeg = THREE.MathUtils.radToDeg(vFov);
      if(needsWider){
        // approximate wider vFov from horizontal constraint
        const requiredVFov = 2 * Math.atan(Math.tan(hFov/2) / aspect);
        desiredFovDeg = THREE.MathUtils.clamp(THREE.MathUtils.radToDeg(requiredVFov), this.minFov, this.maxFov);
      }
      this._desiredFov = desiredFovDeg;
    }

    // Critically-damped spring toward target value
    _spring(current, target, lambda, dt){
      const t = 1 - Math.exp(-lambda * dt);
      return current + (target - current) * t;
    }

    update(dt){
      if(!this.camera) return;
      // 1) Compute framing
      this._computeFraming();
      // 2) Compute desired camera pos and FOV
      this._computeDesired(this.camera);
      // 3) Smooth FOV
      const fov = this._spring(this.camera.fov, this._desiredFov, this.smoothZoom, dt || 0.016);
      this._currentFov = THREE.MathUtils.clamp(fov, this.minFov, this.maxFov);
      if(Math.abs(this.camera.fov - this._currentFov) > 0.001){
        this.camera.fov = this._currentFov;
        this.camera.updateProjectionMatrix();
      }
      // 4) Smooth position
      this.camera.position.lerp(this._desiredPos, 1 - Math.exp(-(this.smoothPos) * (dt || 0.016)) );
      // 5) Look at target center with tilt (lock roll)
      this.camera.lookAt(this._targetCenter);
      this.camera.up.copy(this.up);

      // 6) Clamp tilt by projecting camera vector
      const toTarget = this._tmpV.copy(this._targetCenter).sub(this.camera.position).normalize();
      const tilt = Math.asin(Math.max(-1, Math.min(1, toTarget.y))); // approx vertical angle
      const maxTilt = THREE.MathUtils.degToRad(this.tiltDeg + 10);
      const minTilt = THREE.MathUtils.degToRad(-this.tiltDeg - 10);
      if(tilt > maxTilt || tilt < minTilt){
        // Reposition along a cone around target to satisfy tilt clamp
        const dist = this.camera.position.distanceTo(this._targetCenter);
        const y = Math.sin(THREE.MathUtils.clamp(tilt, minTilt, maxTilt)) * dist;
        const planar = Math.sqrt(Math.max(0.0001, dist*dist - y*y));
        // Keep heading toward -Z
        this.camera.position.set(this._targetCenter.x, this._targetCenter.y + y, this._targetCenter.z + planar * -1);
        this.camera.lookAt(this._targetCenter);
      }

      // 7) Ensure near/far encapsulate arena depth
      const arenaDepth = this._arenaBox.max.distanceTo(this._arenaBox.min);
      this.camera.near = Math.max(0.05, Math.min(this.near, distToAABB(this.camera.position, this._arenaBox) * 0.5));
      this.camera.far = Math.max(this.far, arenaDepth * 2);
      this.camera.updateProjectionMatrix();
    }
  }

  // Distance from point to AABB (approx along view ray avoided here)
  function distToAABB(p, box){
    const dx = Math.max(box.min.x - p.x, 0, p.x - box.max.x);
    const dy = Math.max(box.min.y - p.y, 0, p.y - box.max.y);
    const dz = Math.max(box.min.z - p.z, 0, p.z - box.max.z);
    return Math.sqrt(dx*dx + dy*dy + dz*dz);
  }

  // UMD export
  if(typeof module !== 'undefined' && module.exports){ module.exports = CameraController; }
  else { global.CameraController = CameraController; }

})(this);
