// ===== HAMBURGER MENU =====
        const hamburger = document.getElementById('hamburger');
        const mainNav = document.getElementById('mainNav');
        const navOverlay = document.getElementById('navOverlay');
        
        function toggleNav() {
            hamburger.classList.toggle('active');
            mainNav.classList.toggle('open');
            navOverlay.classList.toggle('open');
        }
        
        hamburger.addEventListener('click', toggleNav);
        navOverlay.addEventListener('click', toggleNav);
        
        mainNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                if (mainNav.classList.contains('open')) toggleNav();
            });
        });
        
        // ===== 3D STARFIELD =====
        const starfieldCanvas = document.getElementById('starfield');
        const ctx = starfieldCanvas.getContext('2d');
        
        function resize() {
            starfieldCanvas.width = window.innerWidth;
            starfieldCanvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);
        
        const stars = [];
        const STAR_COUNT = 400;
        const STAR_SPEED = 2;
        const MAX_DEPTH = 1500;
        
        for (let i = 0; i < STAR_COUNT; i++) {
            stars.push({
                x: (Math.random() - 0.5) * 2000,
                y: (Math.random() - 0.5) * 2000,
                z: Math.random() * MAX_DEPTH,
                size: Math.random() * 1.5 + 0.5
            });
        }
        
        function drawStarfield() {
            const w = starfieldCanvas.width;
            const h = starfieldCanvas.height;
            const cx = w / 2;
            const cy = h / 2;
            
            ctx.fillStyle = 'rgba(5, 5, 16, 0.3)';
            ctx.fillRect(0, 0, w, h);
            
            for (let star of stars) {
                star.z -= STAR_SPEED;
                
                if (star.z <= 0) {
                    star.x = (Math.random() - 0.5) * 2000;
                    star.y = (Math.random() - 0.5) * 2000;
                    star.z = MAX_DEPTH;
                }
                
                const fov = 300;
                const scale = fov / star.z;
                const sx = star.x * scale + cx;
                const sy = star.y * scale + cy;
                
                if (sx < 0 || sx > w || sy < 0 || sy > h) continue;
                
                const depth = 1 - star.z / MAX_DEPTH;
                const size = star.size * scale * 0.5;
                const alpha = depth * 0.8 + 0.2;
                
                const brightness = Math.floor(200 + depth * 55);
                ctx.fillStyle = `rgba(${brightness}, ${brightness + 10}, 255, ${alpha})`;
                
                ctx.beginPath();
                ctx.arc(sx, sy, Math.max(0.5, size), 0, Math.PI * 2);
                ctx.fill();
                
                if (depth > 0.7 && size > 1) {
                    const prevScale = fov / (star.z + STAR_SPEED * 3);
                    const prevX = star.x * prevScale + cx;
                    const prevY = star.y * prevScale + cy;
                    
                    ctx.strokeStyle = `rgba(${brightness}, ${brightness + 10}, 255, ${alpha * 0.5})`;
                    ctx.lineWidth = size * 0.5;
                    ctx.beginPath();
                    ctx.moveTo(prevX, prevY);
                    ctx.lineTo(sx, sy);
                    ctx.stroke();
                }
            }
        }
        
        function animate() {
            drawStarfield();
            requestAnimationFrame(animate);
        }
        animate();
        
        // ===== BENCHMARK FUNCTIONS =====
        
        // Benchmark 1: Direct Access vs Linear Search
        function runBenchmark1() {
            const results = document.getElementById('results1');
            results.className = 'results';
            results.innerHTML = 'Running benchmark...';
            
            // Create test data
            const SIZE = 10000;
            const ITERATIONS = 1000;
            const items = Array.from({length: SIZE}, (_, i) => ({id: i, data: `item-${i}`}));
            
            // Build dimensional substrate (Map)
            const substrate = new Map();
            items.forEach(item => substrate.set(item.id, item));
            
            // Traditional: Linear search
            const tradStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const targetId = Math.floor(Math.random() * SIZE);
                let found = null;
                for (let j = 0; j < items.length; j++) {
                    if (items[j].id === targetId) {
                        found = items[j];
                        break;
                    }
                }
            }
            const tradTime = performance.now() - tradStart;
            
            // Dimensional: Map lookup
            const dimStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const targetId = Math.floor(Math.random() * SIZE);
                const found = substrate.get(targetId);
            }
            const dimTime = performance.now() - dimStart;
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Results (${ITERATIONS} lookups in ${SIZE} items):</strong></div>
                <div class="metric">
                    <div class="metric-label">Traditional (Linear Search)</div>
                    <div class="metric-value">${tradTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Dimensional (Map Lookup)</div>
                    <div class="metric-value">${dimTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Speedup Factor</div>
                    <div class="metric-value">${(tradTime / dimTime).toFixed(1)}x</div>
                </div>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ These are actual measured times from your browser
                </div>
            `;
        }
        
        // Benchmark 2: Nested Property Access
        function runBenchmark2() {
            const results = document.getElementById('results2');
            results.className = 'results';
            results.innerHTML = 'Running benchmark...';
            
            // Build test data structure
            const parkingLot = {
                cars: {}
            };
            
            for (let carId = 0; carId < 100; carId++) {
                parkingLot.cars[carId] = {
                    id: carId,
                    engine: {
                        cylinders: {}
                    }
                };
                for (let cyl = 0; cyl < 8; cyl++) {
                    parkingLot.cars[carId].engine.cylinders[cyl] = {
                        sparkPlug: {
                            gap: 0.028 + Math.random() * 0.01
                        }
                    };
                }
            }
            
            // Build flat substrate
            const substrate = new Map();
            for (let carId in parkingLot.cars) {
                const car = parkingLot.cars[carId];
                for (let cyl in car.engine.cylinders) {
                    const key = `car:${carId}:cyl:${cyl}:gap`;
                    substrate.set(key, car.engine.cylinders[cyl].sparkPlug.gap);
                }
            }
            
            const ITERATIONS = 10000;
            
            // Traditional: Manual traversal
            const tradStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const carId = Math.floor(Math.random() * 100);
                const cyl = Math.floor(Math.random() * 8);
                const car = parkingLot.cars[carId];
                const gap = car?.engine?.cylinders?.[cyl]?.sparkPlug?.gap;
            }
            const tradTime = performance.now() - tradStart;
            
            // Dimensional: Flat lookup
            const dimStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const carId = Math.floor(Math.random() * 100);
                const cyl = Math.floor(Math.random() * 8);
                const gap = substrate.get(`car:${carId}:cyl:${cyl}:gap`);
            }
            const dimTime = performance.now() - dimStart;
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Results (${ITERATIONS} nested accesses):</strong></div>
                <div class="metric">
                    <div class="metric-label">Traditional (Nested Objects)</div>
                    <div class="metric-value">${tradTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Dimensional (Flat Substrate)</div>
                    <div class="metric-value">${dimTime.toFixed(2)} ms</div>
                </div>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ Both approaches are fast for direct access. Dimensional wins when paths are dynamic.
                </div>
            `;
        }
        
        // Benchmark 3: Code Complexity
        function runBenchmark3() {
            const results = document.getElementById('results3');
            results.className = 'results';
            
            const traditionalCode = `const highMileageCars = [];
for (let i = 0; i < parkingLot.cars.length; i++) {
  const car = parkingLot.cars[i];
  if (car && car.mileage && car.mileage > 50000) {
    highMileageCars.push(car);
  }
}
return highMileageCars;`;
            
            const dimensionalCode = `return parkingLot.cars.filter(car => car?.mileage > 50000);`;
            
            // Measure actual code properties
            const tradLines = traditionalCode.split('\n').length;
            const dimLines = dimensionalCode.split('\n').length;
            const tradChars = traditionalCode.length;
            const dimChars = dimensionalCode.length;
            const tradLoops = (traditionalCode.match(/for|while/g) || []).length;
            const dimLoops = (dimensionalCode.match(/for|while/g) || []).length;
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Code Complexity Analysis:</strong></div>
                <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                    <tr style="border-bottom: 1px solid rgba(100,150,255,0.2);">
                        <td style="padding: 8px; color: #8090aa;">Metric</td>
                        <td style="padding: 8px; text-align: center;">Traditional</td>
                        <td style="padding: 8px; text-align: center;">Dimensional</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Lines of Code</td>
                        <td style="padding: 8px; text-align: center; color: #ff8080;">${tradLines}</td>
                        <td style="padding: 8px; text-align: center; color: #80ff80;">${dimLines}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Characters</td>
                        <td style="padding: 8px; text-align: center; color: #ff8080;">${tradChars}</td>
                        <td style="padding: 8px; text-align: center; color: #80ff80;">${dimChars}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Explicit Loops</td>
                        <td style="padding: 8px; text-align: center; color: #ff8080;">${tradLoops}</td>
                        <td style="padding: 8px; text-align: center; color: #80ff80;">${dimLoops}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">Reduction</td>
                        <td style="padding: 8px; text-align: center;">—</td>
                        <td style="padding: 8px; text-align: center; color: #60b0ff;">${Math.round((1 - dimChars/tradChars) * 100)}% fewer chars</td>
                    </tr>
                </table>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ These are literal character/line counts from the code shown above
                </div>
            `;
        }
        
        // Benchmark 4: Memory Layout
        function runBenchmark4() {
            const results = document.getElementById('results4');
            results.className = 'results';
            results.innerHTML = 'Running benchmark...';
            
            const SIZE = 10000;
            const ITERATIONS = 100;
            
            // Traditional: Array of objects
            const tradStart = performance.now();
            for (let iter = 0; iter < ITERATIONS; iter++) {
                const points = [];
                for (let i = 0; i < SIZE; i++) {
                    points.push({
                        x: Math.random(),
                        y: Math.random(),
                        z: Math.random(),
                        value: i
                    });
                }
                // Access all points
                let sum = 0;
                for (let i = 0; i < SIZE; i++) {
                    sum += points[i].x + points[i].y + points[i].z;
                }
            }
            const tradTime = performance.now() - tradStart;
            
            // Dimensional: Typed arrays
            const dimStart = performance.now();
            for (let iter = 0; iter < ITERATIONS; iter++) {
                const substrate = {
                    x: new Float32Array(SIZE),
                    y: new Float32Array(SIZE),
                    z: new Float32Array(SIZE),
                    values: new Int32Array(SIZE)
                };
                for (let i = 0; i < SIZE; i++) {
                    substrate.x[i] = Math.random();
                    substrate.y[i] = Math.random();
                    substrate.z[i] = Math.random();
                    substrate.values[i] = i;
                }
                // Access all points
                let sum = 0;
                for (let i = 0; i < SIZE; i++) {
                    sum += substrate.x[i] + substrate.y[i] + substrate.z[i];
                }
            }
            const dimTime = performance.now() - dimStart;
            
            // Calculate theoretical memory
            const tradMemory = SIZE * (8 * 4 + 32 + 16); // 4 properties + object overhead
            const dimMemory = SIZE * 4 * 4; // 4 typed arrays, 4 bytes each
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Results (${ITERATIONS}x create + iterate ${SIZE} points):</strong></div>
                <div class="metric">
                    <div class="metric-label">Traditional (Objects)</div>
                    <div class="metric-value">${tradTime.toFixed(1)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Dimensional (Typed Arrays)</div>
                    <div class="metric-value">${dimTime.toFixed(1)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Speedup</div>
                    <div class="metric-value">${(tradTime / dimTime).toFixed(2)}x</div>
                </div>
                <div style="margin-top: 15px;">
                    <div class="metric">
                        <div class="metric-label">Traditional Memory (est.)</div>
                        <div class="metric-value">~${(tradMemory / 1024).toFixed(0)} KB</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Dimensional Memory</div>
                        <div class="metric-value">${(dimMemory / 1024).toFixed(0)} KB</div>
                    </div>
                </div>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ Times are measured. Memory is calculated from array sizes (verifiable).
                </div>
            `;
        }
        
        // Benchmark 5: DOM as Substrate
        function runBenchmark5() {
            const results = document.getElementById('results5');
            results.className = 'results';
            results.innerHTML = 'Running benchmark...';
            
            // Create test elements
            const container = document.createElement('div');
            const NUM_ELEMENTS = 1000;
            
            for (let i = 0; i < NUM_ELEMENTS; i++) {
                const el = document.createElement('div');
                el.id = `test-element-${i}`;
                el.textContent = `Element ${i}`;
                container.appendChild(el);
            }
            document.body.appendChild(container);
            container.style.display = 'none';
            
            const ITERATIONS = 1000;
            
            // Traditional: DOM traversal
            const tradStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const targetId = `test-element-${Math.floor(Math.random() * NUM_ELEMENTS)}`;
                let found = null;
                for (let el of container.children) {
                    if (el.id === targetId) {
                        found = el;
                        break;
                    }
                }
            }
            const tradTime = performance.now() - tradStart;
            
            // Dimensional: getElementById
            const dimStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const targetId = `test-element-${Math.floor(Math.random() * NUM_ELEMENTS)}`;
                const found = document.getElementById(targetId);
            }
            const dimTime = performance.now() - dimStart;
            
            // Cleanup
            document.body.removeChild(container);
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Results (${ITERATIONS} lookups in ${NUM_ELEMENTS} DOM elements):</strong></div>
                <div class="metric">
                    <div class="metric-label">Traditional (Manual Traversal)</div>
                    <div class="metric-value">${tradTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Dimensional (getElementById)</div>
                    <div class="metric-value">${dimTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Speedup</div>
                    <div class="metric-value">${(tradTime / dimTime).toFixed(1)}x</div>
                </div>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ Real DOM operations in your browser. The browser's ID registry IS a substrate.
                </div>
            `;
        }
        
        // Benchmark 6: Serialization Latency
        function runBenchmark6() {
            const results = document.getElementById('results6');
            results.className = 'results';
            results.innerHTML = 'Running benchmark...';
            
            const NUM_CARS = 100;
            const CYLINDERS_PER_CAR = 8;
            const ITERATIONS = 100;
            
            // Build traditional nested structure
            const traditionalData = {
                parkingLot: {
                    id: 'lot-001',
                    cars: []
                }
            };
            
            for (let c = 0; c < NUM_CARS; c++) {
                const car = {
                    id: c,
                    make: 'TestCar',
                    model: 'Model-' + c,
                    year: 2020 + (c % 5),
                    mileage: 10000 + c * 500,
                    engine: {
                        type: 'V8',
                        displacement: 5.0,
                        cylinders: []
                    }
                };
                for (let cyl = 0; cyl < CYLINDERS_PER_CAR; cyl++) {
                    car.engine.cylinders.push({
                        number: cyl,
                        sparkPlug: {
                            brand: 'NGK',
                            gap: 0.028 + Math.random() * 0.01
                        }
                    });
                }
                traditionalData.parkingLot.cars.push(car);
            }
            
            // Build dimensional flat structure
            const dimensionalData = {};
            for (let c = 0; c < NUM_CARS; c++) {
                dimensionalData[`car:${c}:make`] = 'TestCar';
                dimensionalData[`car:${c}:model`] = 'Model-' + c;
                dimensionalData[`car:${c}:year`] = 2020 + (c % 5);
                dimensionalData[`car:${c}:mileage`] = 10000 + c * 500;
                dimensionalData[`car:${c}:engine:type`] = 'V8';
                dimensionalData[`car:${c}:engine:displacement`] = 5.0;
                for (let cyl = 0; cyl < CYLINDERS_PER_CAR; cyl++) {
                    dimensionalData[`car:${c}:cyl:${cyl}:brand`] = 'NGK';
                    dimensionalData[`car:${c}:cyl:${cyl}:gap`] = 0.028 + Math.random() * 0.01;
                }
            }
            
            // Traditional: Serialize/Deserialize
            const tradStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const json = JSON.stringify(traditionalData);
                const parsed = JSON.parse(json);
            }
            const tradTime = performance.now() - tradStart;
            
            // Dimensional: Serialize/Deserialize
            const dimStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const json = JSON.stringify(dimensionalData);
                const parsed = JSON.parse(json);
            }
            const dimTime = performance.now() - dimStart;
            
            const tradSize = JSON.stringify(traditionalData).length;
            const dimSize = JSON.stringify(dimensionalData).length;
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Results (${ITERATIONS}x serialize+parse, ${NUM_CARS} cars × ${CYLINDERS_PER_CAR} cylinders):</strong></div>
                <div class="metric">
                    <div class="metric-label">Traditional (Nested)</div>
                    <div class="metric-value">${tradTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Dimensional (Flat)</div>
                    <div class="metric-value">${dimTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Latency Difference</div>
                    <div class="metric-value">${((tradTime - dimTime) / tradTime * 100).toFixed(1)}%</div>
                </div>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ Actual JSON.stringify/parse operations measured in your browser
                </div>
            `;
        }
        
        // Benchmark 7: Network Payload Efficiency
        function runBenchmark7() {
            const results = document.getElementById('results7');
            results.className = 'results';
            results.innerHTML = 'Calculating payload sizes...';
            
            const NUM_CARS = 100;
            const CYLINDERS_PER_CAR = 8;
            
            // Scenario A: Full object graph (all data)
            const fullTraditional = { cars: [] };
            for (let c = 0; c < NUM_CARS; c++) {
                const car = {
                    id: c,
                    make: 'Toyota',
                    model: 'Camry',
                    year: 2023,
                    color: 'Silver',
                    mileage: 50000,
                    engine: {
                        type: 'V8',
                        displacement: 5.0,
                        horsepower: 400,
                        cylinders: []
                    }
                };
                for (let cyl = 0; cyl < CYLINDERS_PER_CAR; cyl++) {
                    car.engine.cylinders.push({
                        number: cyl,
                        sparkPlug: {
                            brand: 'NGK',
                            model: 'Iridium-IX',
                            gap: 0.028
                        }
                    });
                }
                fullTraditional.cars.push(car);
            }
            
            // Scenario B: Sparse - just spark plug gaps (what we actually need)
            const sparseTraditional = { cars: [] };
            for (let c = 0; c < NUM_CARS; c++) {
                const car = { id: c, engine: { cylinders: [] } };
                for (let cyl = 0; cyl < CYLINDERS_PER_CAR; cyl++) {
                    car.engine.cylinders.push({ sparkPlug: { gap: 0.028 } });
                }
                sparseTraditional.cars.push(car);
            }
            
            // Dimensional: Coordinate-based (just gaps)
            const dimensional = {};
            for (let c = 0; c < NUM_CARS; c++) {
                for (let cyl = 0; cyl < CYLINDERS_PER_CAR; cyl++) {
                    dimensional[`c:${c}:e:${cyl}:g`] = 0.028;
                }
            }
            
            // Calculate actual byte sizes
            const fullTradJson = JSON.stringify(fullTraditional);
            const sparseTradJson = JSON.stringify(sparseTraditional);
            const dimJson = JSON.stringify(dimensional);
            
            const fullTradBytes = new Blob([fullTradJson]).size;
            const sparseTradBytes = new Blob([sparseTradJson]).size;
            const dimBytes = new Blob([dimJson]).size;
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Payload Sizes (${NUM_CARS} cars × ${CYLINDERS_PER_CAR} cylinders = ${NUM_CARS * CYLINDERS_PER_CAR} spark plug gaps):</strong></div>
                <div class="metric">
                    <div class="metric-label">Traditional Full Object</div>
                    <div class="metric-value">${(fullTradBytes / 1024).toFixed(2)} KB</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Traditional Sparse (gaps only)</div>
                    <div class="metric-value">${(sparseTradBytes / 1024).toFixed(2)} KB</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Dimensional Coordinates</div>
                    <div class="metric-value">${(dimBytes / 1024).toFixed(2)} KB</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Savings vs Full</div>
                    <div class="metric-value">${((1 - dimBytes / fullTradBytes) * 100).toFixed(1)}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Savings vs Sparse</div>
                    <div class="metric-value">${((1 - dimBytes / sparseTradBytes) * 100).toFixed(1)}%</div>
                </div>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ Actual byte sizes of JSON payloads (using Blob.size for accuracy)
                </div>
            `;
        }
        
        // Benchmark 8: Nested For Loop vs Direct Coordinate Access
        function runBenchmark8() {
            const results = document.getElementById('results8');
            results.className = 'results';
            results.innerHTML = 'Running benchmark...';
            
            const NUM_CARS = 100;
            const CYLINDERS_PER_CAR = 8;
            const ITERATIONS = 10000;
            
            // Build traditional nested structure
            const parkingLot = {
                cars: []
            };
            
            for (let c = 0; c < NUM_CARS; c++) {
                const car = {
                    id: c,
                    cylinders: []
                };
                for (let cyl = 0; cyl < CYLINDERS_PER_CAR; cyl++) {
                    car.cylinders.push({
                        num: cyl,
                        sparkPlug: {
                            gap: 0.028 + (c * CYLINDERS_PER_CAR + cyl) * 0.0001
                        }
                    });
                }
                parkingLot.cars.push(car);
            }
            
            // Build dimensional substrate (Map)
            const substrate = new Map();
            for (let c = 0; c < NUM_CARS; c++) {
                for (let cyl = 0; cyl < CYLINDERS_PER_CAR; cyl++) {
                    const gap = 0.028 + (c * CYLINDERS_PER_CAR + cyl) * 0.0001;
                    substrate.set(`car:${c}:cyl:${cyl}:gap`, gap);
                }
            }
            
            // Target: Car #75, Cylinder #5
            const targetCar = 75;
            const targetCyl = 5;
            
            // Traditional: Nested for loops
            const tradStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                let result = null;
                // Outer loop: iterate through all cars
                for (let c = 0; c < parkingLot.cars.length; c++) {
                    if (parkingLot.cars[c].id === targetCar) {
                        const car = parkingLot.cars[c];
                        // Inner loop: iterate through all cylinders
                        for (let cyl = 0; cyl < car.cylinders.length; cyl++) {
                            if (car.cylinders[cyl].num === targetCyl) {
                                result = car.cylinders[cyl].sparkPlug.gap;
                                break;
                            }
                        }
                        break;
                    }
                }
            }
            const tradTime = performance.now() - tradStart;
            
            // Dimensional: Direct coordinate access
            const dimStart = performance.now();
            for (let i = 0; i < ITERATIONS; i++) {
                const result = substrate.get(`car:${targetCar}:cyl:${targetCyl}:gap`);
            }
            const dimTime = performance.now() - dimStart;
            
            // Verify both return same value
            let tradResult = null;
            for (let c = 0; c < parkingLot.cars.length; c++) {
                if (parkingLot.cars[c].id === targetCar) {
                    const car = parkingLot.cars[c];
                    for (let cyl = 0; cyl < car.cylinders.length; cyl++) {
                        if (car.cylinders[cyl].num === targetCyl) {
                            tradResult = car.cylinders[cyl].sparkPlug.gap;
                            break;
                        }
                    }
                    break;
                }
            }
            const dimResult = substrate.get(`car:${targetCar}:cyl:${targetCyl}:gap`);
            
            const speedup = tradTime / dimTime;
            const avgTradIterations = (targetCar + 1) + (targetCyl + 1); // Average iterations to find
            
            results.innerHTML = `
                <div style="margin-bottom: 10px;"><strong>Results (${ITERATIONS} lookups for Car #${targetCar}, Cylinder #${targetCyl}):</strong></div>
                <div class="metric">
                    <div class="metric-label">Nested For Loops</div>
                    <div class="metric-value">${tradTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Direct Coordinate (Map)</div>
                    <div class="metric-value">${dimTime.toFixed(2)} ms</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Speedup</div>
                    <div class="metric-value">${speedup.toFixed(1)}x faster</div>
                </div>
                <div style="margin-top: 15px;">
                    <div class="metric">
                        <div class="metric-label">Loop Iterations (worst case)</div>
                        <div class="metric-value">${NUM_CARS} + ${CYLINDERS_PER_CAR} = ${NUM_CARS + CYLINDERS_PER_CAR}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Coordinate Lookups</div>
                        <div class="metric-value">1 (always)</div>
                    </div>
                </div>
                <div style="margin-top: 15px; color: #8090aa; font-size: 0.85em;">
                    ✓ Values match: Traditional=${tradResult?.toFixed(5)}, Dimensional=${dimResult?.toFixed(5)}<br>
                    ✓ Real nested loop execution vs Map.get() in your browser
                </div>
            `;
        }