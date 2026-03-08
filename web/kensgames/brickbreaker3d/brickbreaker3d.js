// Brickbreaker 3D — Neon Glass Arena Edition
// Local Three.js only; full-screen canvas; CameraController integrated.
// Arena: glass cylinder + six crystal tile levels; paddle as cue ball, ball half-size glossy.

(function(){
  if(typeof THREE === 'undefined'){
    console.error('[BB3D] Three.js not loaded');
    return;
  }
  console.log('[BB3D] boot');

  const container = document.getElementById('container');
  if(!container){ console.error('[BB3D] #container missing'); return; }

  // Renderer
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(container.clientWidth, container.clientHeight, false);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.shadowMap.enabled = true;
  container.appendChild(renderer.domElement);

  // Scene
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050510);

  // Camera
  const camera = new THREE.PerspectiveCamera(58, Math.max(1, container.clientWidth)/Math.max(1, container.clientHeight), 0.1, 2000);
  camera.position.set(0, 8, 18);
  scene.add(camera);

  // Lights
  const hemi = new THREE.HemisphereLight(0x9ccfff, 0x101018, 0.9);
  scene.add(hemi);
  const key = new THREE.DirectionalLight(0xffffff, 1.0);
  key.position.set(12, 18, 8);
  key.castShadow = true;
  key.shadow.mapSize.set(1024,1024);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0x66ccff, 0.35);
  fill.position.set(-10, 6, -12);
  scene.add(fill);

  // Arena params
  const arenaRadius = 9.0;
  const arenaHeight = 14.0;
  const wallThickness = 0.15; // collider thickness (invisible)

  // Visual glass cylinder (open ended)
  const wallGeom = new THREE.CylinderGeometry(arenaRadius, arenaRadius, arenaHeight, 64, 1, true);
  const wallMat = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color(0x68d5ff).multiplyScalar(0.6),
    metalness: 0.15,
    roughness: 0.08,
    transparent: true,
    opacity: 0.28,
    envMapIntensity: 1.0,
    reflectivity: 0.7,
    clearcoat: 0.9,
    clearcoatRoughness: 0.05,
    side: THREE.DoubleSide
  });
  const wallMesh = new THREE.Mesh(wallGeom, wallMat);
  wallMesh.receiveShadow = false; wallMesh.castShadow = false;
  scene.add(wallMesh);

  // Neon ring accents inside the arena
  const rings = new THREE.Group();
  for(let i=0;i<8;i++){
    const y = -arenaHeight/2 + 1.0 + i * (arenaHeight-2.0)/7;
    const ringGeom = new THREE.TorusGeometry(arenaRadius-0.2, 0.03, 12, 128);
    const ringMat = new THREE.MeshStandardMaterial({ color: 0x29e3ff, emissive: 0x1ad9ff, emissiveIntensity: 0.6, metalness: 0.2, roughness: 0.2 });
    const ring = new THREE.Mesh(ringGeom, ringMat);
    ring.rotation.x = Math.PI/2;
    ring.position.y = y;
    rings.add(ring);
  }
  scene.add(rings);

  // Floor and ceiling visuals
  const floorGeom = new THREE.CircleGeometry(arenaRadius-0.05, 64);
  const floorMat = new THREE.MeshStandardMaterial({ color: 0x0c0c18, metalness: 0.6, roughness: 0.6 });
  const floor = new THREE.Mesh(floorGeom, floorMat);
  floor.rotation.x = -Math.PI/2; floor.position.y = -arenaHeight/2;
  floor.receiveShadow = true; scene.add(floor);

  const ceil = new THREE.Mesh(floorGeom, floorMat);
  ceil.rotation.x = Math.PI/2; ceil.position.y = arenaHeight/2;
  ceil.receiveShadow = false; scene.add(ceil);

  // Invisible colliders (cylinder wall, floor, ceiling) for physics
  const bounds = {
    min: new THREE.Vector3(-arenaRadius, -arenaHeight/2, -arenaRadius),
    max: new THREE.Vector3( arenaRadius,  arenaHeight/2,  arenaRadius)
  };

  // Tile levels (6 crystal rings)
  const levelColors = [0x00e5ff, 0xff3cac, 0xa3ff4d, 0xffd700, 0xb040ff, 0xff9933];
  const levels = new THREE.Group();
  const bricks = []; // store for collision
  const ringCount = 6;
  const ringSpacing = (arenaHeight - 4.0) / (ringCount - 1);
  for(let i=0;i<ringCount;i++){
    const y = -arenaHeight/2 + 2.0 + i*ringSpacing;
    const group = new THREE.Group();
    const brickRad = arenaRadius - 1.2;
    const segments = 18;
    for(let s=0;s<segments;s++){
      const ang = (s + (i%2?0.5:0)) * (Math.PI*2/segments);
      const bx = Math.cos(ang)*brickRad;
      const bz = Math.sin(ang)*brickRad;
      const geo = new THREE.BoxGeometry(1.2, 0.5, 0.6);
      const mat = new THREE.MeshPhysicalMaterial({
        color: levelColors[i],
        metalness: 0.6,
        roughness: 0.18,
        transparent: true,
        opacity: 0.72,
        emissive: levelColors[i],
        emissiveIntensity: 0.1,
        clearcoat: 0.6,
        clearcoatRoughness: 0.08
      });
      const b = new THREE.Mesh(geo, mat);
      b.position.set(bx, y, bz);
      b.lookAt(0,y,0);
      b.castShadow = true; b.receiveShadow = true;
      group.add(b);
      bricks.push(b);
    }
    levels.add(group);
  }
  scene.add(levels);

  // Paddle (cue ball) and breaker ball
  const paddleRadius = 0.6;
  const ballRadius = 0.3; // half size
  const cueMat = new THREE.MeshPhysicalMaterial({ color: 0xffffff, metalness: 0.05, roughness: 0.05, clearcoat: 1.0, clearcoatRoughness: 0.03 });
  const paddle = new THREE.Mesh(new THREE.SphereGeometry(paddleRadius, 32, 24), cueMat);
  paddle.castShadow = true; paddle.receiveShadow = false;
  paddle.position.set(0, -arenaHeight/2 + 1.2, arenaRadius - 1.4);
  scene.add(paddle);

  const ballMat = new THREE.MeshPhysicalMaterial({ color: 0xfff0d0, metalness: 0.08, roughness: 0.06, clearcoat: 0.9, clearcoatRoughness: 0.04 });
  const ball = new THREE.Mesh(new THREE.SphereGeometry(ballRadius, 32, 24), ballMat);
  ball.castShadow = true; ball.receiveShadow = false;
  ball.position.set(0, paddle.position.y + 0.5, arenaRadius - 2.2);
  scene.add(ball);

  // Camera controller
  const camCtrl = (typeof CameraController !== 'undefined') ? new CameraController(camera, scene, bounds, {
    margin: 0.18,
    minFov: 48,
    maxFov: 66,
    tiltDeg: 15,
    smoothPos: 9,
    smoothZoom: 7,
    near: 0.1,
    far: 800,
    wallClearance: 0.6,
  }) : null;
  if(camCtrl){ camCtrl.setTargets(ball, paddle); }

  // Input — mouse X maps to paddle angle along cylinder (limited arc), Space/Click launches
  let launched = false;
  const vel = new THREE.Vector3(3.8, 4.2, -6.5);
  function onPointerMove(e){
    const rect = renderer.domElement.getBoundingClientRect();
    const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1; // -1..1
    const ang = THREE.MathUtils.lerp(-0.45*Math.PI, 0.45*Math.PI, (nx+1)/2);
    const r = arenaRadius - 1.4;
    paddle.position.x = Math.cos(ang) * r;
    paddle.position.z = Math.sin(ang) * r;
    paddle.lookAt(0, paddle.position.y, 0);
  }
  function onClick(){ launched = true; }
  window.addEventListener('pointermove', onPointerMove);
  window.addEventListener('click', onClick);
  window.addEventListener('keydown', (e)=>{ if(e.code==='Space') launched = true; });

  // HUD
  const scoreEl = document.getElementById('score');
  const livesEl = document.getElementById('lives');
  let score = 0, lives = 3;

  // Resize
  function onResize(){
    const w = container.clientWidth, h = container.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = Math.max(0.1, w/Math.max(1,h));
    camera.updateProjectionMatrix();
    if(camCtrl) camCtrl.onResize(w,h);
  }
  window.addEventListener('resize', onResize);
  onResize();

  // Physics helpers
  const tmpV = new THREE.Vector3();
  function reflectVec(v, n){ // reflect v about normal n
    return v.sub(tmpV.copy(n).multiplyScalar(2 * v.dot(n)));
  }

  function updatePhysics(dt){
    if(!launched) return;
    // integrate
    ball.position.addScaledVector(vel, dt);

    // Wall collision (cylinder)
    const r = Math.sqrt(ball.position.x*ball.position.x + ball.position.z*ball.position.z);
    const maxR = arenaRadius - 0.3 - ballRadius;
    if(r > maxR){
      const n = new THREE.Vector3(ball.position.x, 0, ball.position.z).normalize();
      // project velocity onto normal and reflect
      const vn = n.clone().multiplyScalar(vel.dot(n));
      const vt = vel.clone().sub(vn);
      vel.copy(vt.sub(vn));
      // push inside
      ball.position.x = n.x * maxR;
      ball.position.z = n.z * maxR;
    }

    // Floor/ceiling collisions
    const minY = -arenaHeight/2 + ballRadius;
    const maxY =  arenaHeight/2 - ballRadius;
    if(ball.position.y < minY){ ball.position.y = minY; vel.y = Math.abs(vel.y); }
    if(ball.position.y > maxY){ ball.position.y = maxY; vel.y = -Math.abs(vel.y); }

    // Paddle collision (sphere-sphere)
    const d2 = ball.position.distanceToSquared(paddle.position);
    const rr = (ballRadius + paddleRadius)*(ballRadius + paddleRadius);
    if(d2 <= rr){
      const n = tmpV.copy(ball.position).sub(paddle.position).normalize();
      // Reflect velocity
      reflectVec(vel, n);
      // Add English based on paddle movement tangent
      const t = new THREE.Vector3(-Math.sin(Math.atan2(paddle.position.z, paddle.position.x)), 0, Math.cos(Math.atan2(paddle.position.z, paddle.position.x)));
      vel.addScaledVector(t, 0.8);
      // Push apart
      ball.position.copy(paddle.position).addScaledVector(n, ballRadius + paddleRadius + 1e-3);
    }

    // Brick collisions (AABB test)
    for(let i=bricks.length-1;i>=0;i--){
      const b = bricks[i];
      if(!b.visible) continue;
      const hx = 0.6, hy = 0.25, hz = 0.3; // half extents
      const dx = THREE.MathUtils.clamp(ball.position.x, b.position.x - hx, b.position.x + hx) - ball.position.x;
      const dy = THREE.MathUtils.clamp(ball.position.y, b.position.y - hy, b.position.y + hy) - ball.position.y;
      const dz = THREE.MathUtils.clamp(ball.position.z, b.position.z - hz, b.position.z + hz) - ball.position.z;
      const dist2 = dx*dx + dy*dy + dz*dz;
      if(dist2 <= ballRadius*ballRadius){
        // pick axis of minimum penetration
        const ax = Math.abs(dx), ay = Math.abs(dy), az = Math.abs(dz);
        if(ax <= ay && ax <= az){ vel.x *= -1; }
        else if(ay <= ax && ay <= az){ vel.y *= -1; }
        else { vel.z *= -1; }
        // remove brick with small pop
        b.visible = false;
        score += 10; if(scoreEl) scoreEl.textContent = String(score);
      }
    }

    // Lose condition: ball below paddle ring exiting front arc
    const frontR = arenaRadius - 0.8;
    const frontY = paddle.position.y - 0.6;
    const bz = ball.position.z; // heuristic; keep simple
    if(bz > frontR && ball.position.y < frontY){
      lives = Math.max(0, lives - 1); if(livesEl) livesEl.textContent = String(lives);
      launched = false;
      ball.position.set(0, paddle.position.y + 0.5, arenaRadius - 2.2);
      vel.set(3.8, 4.2, -6.5);
    }
  }

  // Animation loop
  let last = performance.now();
  console.log('[BB3D] init');
  function tick(now){
    const dt = Math.min(0.033, (now - last)/1000);
    last = now;

    updatePhysics(dt);
    if(camCtrl){ camCtrl.update(dt); }

    renderer.render(scene, camera);
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
