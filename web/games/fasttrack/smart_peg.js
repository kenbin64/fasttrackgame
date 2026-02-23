// ============================================================
// SMART PEG SYSTEM — Hop-Counting Movement Engine
// ============================================================
//
// Replaces the bug-prone getTrackSequence() + step loop with
// a simple hop-by-hop traversal using pre-computed adjacency.
//
// Architecture:
//   BoardAdjacency  → Pre-computed next-hole map (84-hole track)
//   SmartPeg         → Self-aware peg that hops hole-by-hole
//   GameManager      → Central authority: validates, tracks, broadcasts
//
// Flow:
//   Card drawn → GameManager asks SmartPeg "hop N times"
//             → SmartPeg hops through adjacency, counting
//             → SmartPeg reports destination + path
//             → GameManager validates hop count matches card
//             → GameManager broadcasts state to all players
// ============================================================

'use strict';

// ============================================================
// BOARD ADJACENCY — Pre-computed next-hole map
// ============================================================
class BoardAdjacency {
    constructor() {
        this.perimeterTrack = [];       // Ordered 84-hole clockwise track
        this.holeToIndex = new Map();   // holeId → index in perimeterTrack
        this._build();
    }

    _build() {
        // Build the 84-hole perimeter track in clockwise order
        // Each of the 6 sections has 14 holes:
        //   side-left-{p}-1..4, outer-{p}-0..3, home-{p}, side-right-{p}-4..1, ft-{(p+1)%6}
        for (let p = 0; p < 6; p++) {
            for (let h = 1; h <= 4; h++) this.perimeterTrack.push(`side-left-${p}-${h}`);
            for (let h = 0; h < 4; h++) this.perimeterTrack.push(`outer-${p}-${h}`);
            this.perimeterTrack.push(`home-${p}`);
            for (let h = 4; h >= 1; h--) this.perimeterTrack.push(`side-right-${p}-${h}`);
            this.perimeterTrack.push(`ft-${(p + 1) % 6}`);
        }

        // Index map for O(1) lookups
        for (let i = 0; i < this.perimeterTrack.length; i++) {
            this.holeToIndex.set(this.perimeterTrack[i], i);
        }

        console.log(`🗺️ [BoardAdjacency] Built ${this.perimeterTrack.length}-hole perimeter track`);
    }

    // Get next hole on the perimeter (clockwise or counter-clockwise)
    getNextPerimeter(holeId, clockwise = true) {
        const idx = this.holeToIndex.get(holeId);
        if (idx === undefined) return null;
        const len = this.perimeterTrack.length;
        const nextIdx = clockwise ? (idx + 1) % len : (idx - 1 + len) % len;
        return this.perimeterTrack[nextIdx];
    }

    // Get next hole in FastTrack ring (clockwise: ft-0→ft-1→...→ft-5→ft-0)
    getNextFasttrack(ftHoleId, clockwise = true) {
        const idx = parseInt(ftHoleId.replace('ft-', ''));
        if (isNaN(idx)) return null;
        return clockwise ? `ft-${(idx + 1) % 6}` : `ft-${(idx - 1 + 6) % 6}`;
    }

    // Get the section index for a hole (which player's section it's in)
    getSectionForHole(holeId) {
        const idx = this.holeToIndex.get(holeId);
        if (idx === undefined) return -1;
        return Math.floor(idx / 14);
    }
}


// ============================================================
// SMART PEG — Self-aware peg that counts hops
// ============================================================
class SmartPeg {
    /**
     * @param {Object} pegData - The peg object from the game engine
     * @param {number} playerBoardPos - The player's board position (0-5)
     * @param {Array} allPlayerPegs - All pegs belonging to this player
     * @param {BoardAdjacency} adjacency - The pre-computed adjacency map
     */
    constructor(pegData, playerBoardPos, allPlayerPegs, adjacency) {
        this.peg = pegData;
        this.boardPos = playerBoardPos;
        this.teammates = allPlayerPegs;
        this.adj = adjacency;
    }

    // ============================================================
    // CORE: Get the SINGLE next hole from current position
    // This is the heart of the system — ~40 lines instead of ~500
    // ============================================================
    getNextHole(currentHole, clockwise, simState) {
        // SAFE ZONE: forward only within safe zone
        if (currentHole.startsWith('safe-')) {
            if (!clockwise) return null; // Can't go backward in safe zone
            const match = currentHole.match(/safe-(\d+)-(\d+)/);
            if (!match) return null;
            const safePlayer = parseInt(match[1]);
            const safeNum = parseInt(match[2]);

            if (safeNum < 4) {
                return `safe-${safePlayer}-${safeNum + 1}`;
            }

            // At safe-*-4: can only proceed to home if safe zone is completely full
            // (5th peg passing through scenario)
            const otherSafePegs = this.teammates.filter(p =>
                p.holeType === 'safezone' && p.id !== this.peg.id
            ).length;
            // This peg is at safe-4, so total safe pegs = otherSafePegs + 1
            // Need all 4 safe holes occupied (this peg + 3 others)
            if (otherSafePegs >= 3) {
                return `home-${safePlayer}`;
            }
            return null; // End of safe zone, can't proceed
        }

        // FASTTRACK MODE: hop around the ft ring
        if (simState.onFasttrack && currentHole.startsWith('ft-') && !simState.mustExitFasttrack) {
            if (!clockwise) {
                // Backward from FastTrack: exit to perimeter counter-clockwise
                return this.adj.getNextPerimeter(currentHole, false);
            }

            const currentFtIdx = parseInt(currentHole.replace('ft-', ''));

            // If at own exit point AND has traversed (entered from different hole):
            // EXIT TO PERIMETER (side-left track), NOT directly to safe zone!
            // The peg continues on the main circuit: side-left → outer → safe zone entry
            if (currentFtIdx === this.boardPos &&
                simState.fasttrackEntryHole &&
                simState.fasttrackEntryHole !== currentHole) {
                // Exit to side-left-{boardPos}-1 (first hole of perimeter after FastTrack exit)
                return `side-left-${this.boardPos}-1`;
            }

            // Check if NEXT ft-* hole would be blocked by own peg
            // If so, must exit FastTrack here to the perimeter
            const nextFtHole = this.adj.getNextFasttrack(currentHole, true);
            if (nextFtHole && this._isBlockedByOwnPeg(nextFtHole)) {
                console.log(`🚧 [FastTrack] Next hole ${nextFtHole} blocked by own peg - forcing exit to perimeter`);
                // Exit to perimeter at current ft-* hole
                return `side-left-${currentFtIdx}-1`;
            }

            // Continue around FastTrack ring
            return nextFtHole;
        }

        // MUST EXIT FASTTRACK (e.g., 4 card drawn while on FastTrack)
        if (simState.mustExitFasttrack && currentHole.startsWith('ft-')) {
            // Exit to perimeter in the requested direction
            return this.adj.getNextPerimeter(currentHole, clockwise);
        }

        // SAFE ZONE ENTRY: outer-{boardPos}-2 is the entry point for safe zone
        // When eligible for safe zone and reaching this hole, route to safe zone
        if (currentHole === `outer-${this.boardPos}-2` &&
            simState.eligibleForSafeZone && clockwise) {
            return `safe-${this.boardPos}-1`;
        }

        // HOME HOLE with safe zone eligibility: route to safe zone
        // (This is for 5th peg scenario when safe zone is full)
        if (currentHole === `home-${this.boardPos}` &&
            simState.eligibleForSafeZone && clockwise) {
            return `safe-${this.boardPos}-1`;
        }

        // DEFAULT: perimeter track
        return this.adj.getNextPerimeter(currentHole, clockwise);
    }

    // ============================================================
    // Calculate the full path for N hops
    // Returns: { path, destination, hopsCompleted, blocked, blockedAt, blockedBy }
    // simOverrides: optional object to override initial sim state (e.g. {onFasttrack: false})
    // ============================================================
    calculatePath(hops, direction, simOverrides = {}) {
        const clockwise = direction !== 'backward';
        const path = [this.peg.holeId];
        let currentHole = this.peg.holeId;

        // Simulated state — COPY so we never mutate the real peg
        const sim = {
            eligibleForSafeZone: this.peg.eligibleForSafeZone || false,
            lockedToSafeZone: this.peg.lockedToSafeZone || false,
            onFasttrack: this.peg.onFasttrack || false,
            fasttrackEntryHole: this.peg.fasttrackEntryHole || null,
            mustExitFasttrack: this.peg.mustExitFasttrack || false,
            inBullseye: this.peg.inBullseye || false,
            ...simOverrides  // Apply overrides (e.g. {onFasttrack: false} for leave-FT)
        };

        let blocked = false;
        let blockedAt = null;
        let blockedBy = null;

        for (let hop = 0; hop < hops; hop++) {
            const nextHole = this.getNextHole(currentHole, clockwise, sim);

            // No next hole (end of safe zone, etc.)
            if (!nextHole) {
                blocked = true;
                blockedAt = currentHole;
                break;
            }

            // BACKWARD RESTRICTIONS (4 card)
            // Cannot enter bullseye (center) or safe zone going backward.
            // ft-* holes CAN be traversed on perimeter going backward (they're just corners)
            // but FastTrack MODE is never entered backward (getNextHole handles that).
            if (!clockwise) {
                if (nextHole === 'center') { blocked = true; blockedAt = nextHole; break; }
                if (nextHole.startsWith('safe-')) { blocked = true; blockedAt = nextHole; break; }
            }

            // BLOCKING by own peg (can't pass or land on own non-bullseye, non-finished pegs)
            if (this._isBlockedByOwnPeg(nextHole)) {
                const blocker = this.teammates.find(p =>
                    p.holeId === nextHole && p.id !== this.peg.id &&
                    p.holeType !== 'holding' && !p.inBullseye && !p.completedCircuit
                );
                blocked = true;
                blockedAt = nextHole;
                blockedBy = blocker ? blocker.id : 'unknown';
                break;
            }

            // EXACT LANDING: home-{boardPos} from safe zone requires exact landing
            // (this is the final winning position)
            if (nextHole === `home-${this.boardPos}` &&
                currentHole.startsWith('safe-') &&
                hop < hops - 1) {
                // Can land on home only as the LAST hop
                // If there are more hops remaining, can't overshoot
                blocked = true;
                blockedAt = nextHole;
                break;
            }

            path.push(nextHole);

            // ── Update simulated state mid-path ──

            // Passing through own home clockwise = lap complete → eligible for safe zone
            // KEY FIX: This allows safe zone entry in the SAME move that completes the lap
            if (nextHole === `home-${this.boardPos}` && clockwise && !sim.eligibleForSafeZone) {
                sim.eligibleForSafeZone = true;
                sim.lockedToSafeZone = true;
            }

            // Track FastTrack state: if entering ft-* intentionally, sim knows
            if (sim.onFasttrack && !nextHole.startsWith('ft-') && nextHole !== 'center') {
                sim.onFasttrack = false;
                sim.fasttrackEntryHole = null;
            }

            // If on FastTrack and reached own exit, EXIT FASTTRACK and mark for safe zone
            // They've "left FastTrack" - now on perimeter heading to safe zone
            if (sim.onFasttrack && nextHole === `ft-${this.boardPos}` &&
                sim.fasttrackEntryHole && sim.fasttrackEntryHole !== `ft-${this.boardPos}`) {
                sim.eligibleForSafeZone = true;
                sim.lockedToSafeZone = true;
                sim.onFasttrack = false;  // EXIT FastTrack - they're now on perimeter
                sim.fasttrackEntryHole = null;
            }

            currentHole = nextHole;
        }

        const destination = blocked ? null : (path.length > 1 ? path[path.length - 1] : null);

        // Final landing check: can't land on own peg at destination
        if (destination && this._isBlockedByOwnPeg(destination)) {
            return {
                path, destination: null, hopsCompleted: path.length - 1,
                blocked: true, blockedAt: destination, blockedBy: 'own peg at destination',
                expectedHops: hops
            };
        }

        return {
            path,
            destination,
            hopsCompleted: path.length - 1,
            blocked,
            blockedAt,
            blockedBy,
            expectedHops: hops
        };
    }

    // ============================================================
    // Get ALL possible moves for a card (including FastTrack/bullseye options)
    // Returns array matching the format of calculateDestinations()
    // ============================================================
    getAllMoves(card) {
        const destinations = [];
        const direction = card.direction || 'clockwise';
        const hops = card.movement;

        // ── Standard path ──
        const result = this.calculatePath(hops, direction);

        if (result.destination) {
            // Primary destination (FT traverse if on FT, or normal perimeter move)
            const isFTPeg = this.peg.onFasttrack && this.peg.holeId.startsWith('ft-');
            destinations.push({
                holeId: result.destination,
                steps: hops,
                path: [...result.path],
                description: isFTPeg
                    ? `⚡ Continue on FastTrack → ${result.destination}`
                    : `Move ${hops} to ${result.destination}`
            });

            // OPTION: FastTrack entry (landing exactly on ft-* from perimeter)
            if (result.destination.startsWith('ft-') && !this.peg.onFasttrack) {
                destinations.push({
                    holeId: result.destination,
                    steps: hops,
                    path: [...result.path],
                    isFastTrackEntry: true,
                    description: `Enter FastTrack at ${result.destination}`
                });
            }

            // OPTION: Bullseye from FastTrack (1 step past ft-*)
            this._addBullseyeOptions(result, destinations, hops);
        }

        // ════════════════════════════════════════════════════════
        // OPTION: Leave FastTrack → continue on outer perimeter
        // RULE: A peg on ANY ft-* hole in FT mode can choose to leave
        // FastTrack and continue on the outer perimeter track instead.
        // This calculates where the peg would land if it left FT immediately.
        // ════════════════════════════════════════════════════════
        if (this.peg.onFasttrack && this.peg.holeId.startsWith('ft-') && !this.peg.inHomeStretch) {
            const perimeterResult = this.calculatePath(hops, direction, {
                onFasttrack: false,
                fasttrackEntryHole: null,
                mustExitFasttrack: false
            });

            if (perimeterResult.destination) {
                // Only add if destination differs from the FT traverse destination
                // (avoids duplicates when both paths converge)
                const alreadyHasThis = destinations.some(d =>
                    d.holeId === perimeterResult.destination && !d.isCenterOption && !d.isFastTrackEntry
                );
                if (!alreadyHasThis) {
                    destinations.push({
                        holeId: perimeterResult.destination,
                        steps: hops,
                        path: [...perimeterResult.path],
                        isLeaveFastTrack: true,
                        description: `🔄 Leave FastTrack → ${perimeterResult.destination}`
                    });
                    console.log(`🔄 [SmartPeg] Offering leave-FT option: ${this.peg.holeId} → perimeter → ${perimeterResult.destination}`);
                }
            }
        }

        // OPTION: FastTrack peg with 1-hop card → bullseye
        // RULE: A peg on FastTrack can enter bullseye with a 1-step card from any ft-* hole
        // EXCEPT their own color's FastTrack hole (ft-{boardPos}). Moving to center
        // from your own FT entry point is considered a backwards move.
        // Cards with movement=1: A, Joker, J, Q, K.
        const ownFtHole = `ft-${this.boardPos}`;
        if (this.peg.onFasttrack && this.peg.holeId.startsWith('ft-') && hops === 1
            && this.peg.holeId !== ownFtHole) {
            if (!this._ownPegInCenter()) {
                const already = destinations.some(d => d.isCenterOption);
                if (!already) {
                    destinations.push({
                        holeId: 'center',
                        steps: 1,
                        path: [this.peg.holeId, 'center'],
                        isCenterOption: true,
                        description: `🎯 Enter Bullseye from ${this.peg.holeId}`
                    });
                    console.log(`🎯 [SmartPeg] Offering bullseye option - FT peg at ${this.peg.holeId} with 1-step card`);
                }
            }
        } else if (this.peg.onFasttrack && this.peg.holeId === ownFtHole && hops === 1) {
            console.log(`🚫 [SmartPeg] Bullseye blocked - peg is on own FT hole ${ownFtHole} (backwards move)`);
        }

        // ── lockedToSafeZone filter ──
        // If peg is locked, only allow safe zone or home destinations
        if (this.peg.lockedToSafeZone) {
            const filtered = destinations.filter(d =>
                d.holeId.startsWith('safe-') || d.holeId.startsWith('home-')
            );
            if (filtered.length < destinations.length) {
                console.log(`🔒 [SmartPeg] ${this.peg.id} locked to safe zone: ${destinations.length} → ${filtered.length} destinations`);
            }
            return filtered;
        }

        return destinations;
    }

    // ── Bullseye option detection ──
    _addBullseyeOptions(result, destinations, hops) {
        const path = result.path;
        if (path.length < 3) return;

        const prevHole = path[path.length - 2];

        // On FastTrack, 1 step past any ft-* → bullseye option
        // RULE: Bullseye is reachable from any ft-* hole EXCEPT the player's own
        // color FT hole (ft-{boardPos}). From own hole, bullseye is backwards.
        const ownFtHole = `ft-${this.boardPos}`;
        if (this.peg.onFasttrack && prevHole.startsWith('ft-') && prevHole !== ownFtHole) {
            if (!this._ownPegInCenter()) {
                destinations.push({
                    holeId: 'center',
                    steps: hops,
                    path: [...path.slice(0, -1), 'center'],
                    isCenterOption: true,
                    description: `Enter bullseye from ${prevHole}`
                });
            }
        }

        // On perimeter, passing through ft-* with 1 step remaining → bullseye option
        // Same restriction: cannot enter bullseye via own color FT hole
        if (!this.peg.onFasttrack) {
            for (let i = 0; i < path.length - 1; i++) {
                if (path[i].startsWith('ft-')) {
                    const stepsAfterFt = path.length - 1 - i;
                    if (stepsAfterFt === 1 && path[i] !== ownFtHole && !this._ownPegInCenter()) {
                        destinations.push({
                            holeId: 'center',
                            steps: hops,
                            path: [...path.slice(0, i + 1), 'center'],
                            isCenterOption: true,
                            isFastTrackEntry: true,
                            description: `Enter bullseye via ${path[i]}`
                        });
                    }
                    break; // Only first ft-* in path
                }
            }
        }
    }

    // ── Blocking helpers ──
    _isBlockedByOwnPeg(holeId) {
        if (holeId === 'center') return false; // Bullseye never blocks
        return this.teammates.some(p =>
            p.holeId === holeId &&
            p.id !== this.peg.id &&
            p.holeType !== 'holding' &&
            !p.inBullseye &&
            !p.completedCircuit
        );
    }

    _ownPegInCenter() {
        return this.teammates.some(p =>
            p.holeId === 'center' && p.id !== this.peg.id
        );
    }
}


// ============================================================
// SMART PEG MANAGER — Central authority, validates & broadcasts
// ============================================================
class SmartPegManager {
    constructor() {
        this.adjacency = new BoardAdjacency();
        this.moveLog = [];
        this.listeners = new Set();
        this.stateVersion = 0;
        this.errorCount = 0;

        console.log('🎮 [SmartPegManager] Initialized — Smart Peg hop-counting system active');
    }

    // ── SmartPeg factory ──
    createSmartPeg(peg, playerBoardPos, allPlayerPegs) {
        return new SmartPeg(peg, playerBoardPos, allPlayerPegs, this.adjacency);
    }

    // ── Main calculation entry point ──
    // Drop-in replacement for GameState.calculateDestinations()
    calculateDestinations(peg, card, player) {
        const smartPeg = this.createSmartPeg(peg, player.boardPosition, player.peg);
        const destinations = smartPeg.getAllMoves(card);

        // Log results
        if (destinations.length > 0) {
            console.log(`🧠 [SmartPeg] ${peg.id} at ${peg.holeId}: ${destinations.length} destinations for ${card.movement} hops → [${destinations.map(d => d.holeId).join(', ')}]`);
        } else {
            console.log(`🧠 [SmartPeg] ${peg.id} at ${peg.holeId}: 0 destinations for ${card.movement} hops (blocked or no path)`);
        }

        return destinations;
    }

    // ── Move validation ──
    validateMove(move, card) {
        if (!move || !card) return { valid: true };

        const pathHops = move.path ? move.path.length - 1 : 0;
        const expectedHops = card.movement;

        // Bullseye/center options may have different path lengths
        if (move.isCenterOption) return { valid: true };

        // Enter moves have 0 hops
        if (move.type === 'enter' || move.type === 'bullseye_exit') return { valid: true };

        if (pathHops !== expectedHops) {
            this.errorCount++;
            console.warn(`⚠️ [SmartPegManager] HOP MISMATCH #${this.errorCount}: path=${pathHops} hops, card=${expectedHops}`);
            console.warn(`⚠️ [SmartPegManager] Move: ${move.fromHoleId} → ${move.toHoleId}, path: ${move.path?.join(' → ')}`);
            return {
                valid: false,
                reason: `Hop count mismatch: ${pathHops} vs ${expectedHops}`,
                pathHops,
                expectedHops
            };
        }

        return { valid: true };
    }

    // ── Record a move and broadcast ──
    recordMove(player, peg, move, card) {
        this.stateVersion++;

        const validation = this.validateMove(move, card);

        const record = {
            version: this.stateVersion,
            timestamp: Date.now(),
            playerIndex: player.index,
            playerName: player.name,
            pegId: peg.id,
            from: move.fromHoleId,
            to: move.toHoleId,
            card: card ? { rank: card.rank, movement: card.movement, direction: card.direction } : null,
            pathLength: move.path ? move.path.length - 1 : 0,
            validation
        };

        this.moveLog.push(record);
        if (this.moveLog.length > 200) this.moveLog.shift();

        if (!validation.valid) {
            console.error(`🚨 [SmartPegManager] INVALID MOVE:`, validation.reason);
        }

        // Broadcast to all listeners
        this._broadcast('move', record);

        return record;
    }

    // ── Get a full board state snapshot ──
    getStateSnapshot(gameState) {
        return {
            version: this.stateVersion,
            timestamp: Date.now(),
            turn: gameState.turnCount,
            currentPlayer: gameState.currentPlayerIndex,
            phase: gameState.phase,
            players: gameState.players.map(p => ({
                index: p.index,
                name: p.name,
                boardPosition: p.boardPosition,
                pegs: p.peg.map(peg => ({
                    id: peg.id,
                    holeId: peg.holeId,
                    holeType: peg.holeType,
                    onFasttrack: peg.onFasttrack,
                    eligibleForSafeZone: peg.eligibleForSafeZone,
                    lockedToSafeZone: peg.lockedToSafeZone,
                    completedCircuit: peg.completedCircuit,
                    inBullseye: peg.inBullseye,
                    mustExitFasttrack: peg.mustExitFasttrack
                }))
            }))
        };
    }

    // ── Compensate for a detected error ──
    compensate(gameState, pegId, correctHoleId) {
        for (const player of gameState.players) {
            const peg = player.peg.find(p => p.id === pegId);
            if (!peg) continue;

            const oldHole = peg.holeId;
            peg.holeId = correctHoleId;

            // Update hole type
            if (typeof getHoleTypeFromId === 'function') {
                const holeType = getHoleTypeFromId(correctHoleId);
                peg.holeType = holeType ? holeType.id : 'unknown';
            }

            // Update flags based on new position
            if (correctHoleId.startsWith('safe-')) {
                peg.eligibleForSafeZone = true;
                peg.lockedToSafeZone = true;
                peg.onFasttrack = false;
            } else if (correctHoleId.startsWith('hold-')) {
                peg.eligibleForSafeZone = false;
                peg.lockedToSafeZone = false;
                peg.onFasttrack = false;
                peg.completedCircuit = false;
                peg.inBullseye = false;
            }

            console.log(`🔧 [SmartPegManager] COMPENSATED: ${pegId} from ${oldHole} → ${correctHoleId}`);

            // Update visual position
            if (window.updatePegPosition) {
                window.updatePegPosition(pegId, correctHoleId);
            }

            this.stateVersion++;
            this._broadcast('compensation', { pegId, from: oldHole, to: correctHoleId });
            return true;
        }
        return false;
    }

    // ── State integrity check ──
    // Call this periodically to detect and fix peg state corruption
    auditState(gameState) {
        let fixes = 0;

        for (const player of gameState.players) {
            for (const peg of player.peg) {
                // Fix 1: Peg on home with inBullseye = true
                if (peg.holeType === 'home' && peg.inBullseye) {
                    console.warn(`🔧 [Audit] ${peg.id}: clearing inBullseye on home`);
                    peg.inBullseye = false;
                    fixes++;
                }

                // Fix 2: Peg in holding with stale flags
                if (peg.holeType === 'holding') {
                    if (peg.eligibleForSafeZone || peg.lockedToSafeZone ||
                        peg.onFasttrack || peg.completedCircuit || peg.inBullseye) {
                        console.warn(`🔧 [Audit] ${peg.id}: clearing stale flags in holding`);
                        peg.eligibleForSafeZone = false;
                        peg.lockedToSafeZone = false;
                        peg.onFasttrack = false;
                        peg.completedCircuit = false;
                        peg.inBullseye = false;
                        peg.mustExitFasttrack = false;
                        fixes++;
                    }
                }

                // Fix 3: lockedToSafeZone without eligibleForSafeZone
                if (peg.lockedToSafeZone && !peg.eligibleForSafeZone) {
                    console.warn(`🔧 [Audit] ${peg.id}: lockedToSafeZone without eligible — clearing lock`);
                    peg.lockedToSafeZone = false;
                    fixes++;
                }

                // Fix 4: Peg on home hole from holding entry with incorrect lockedToSafeZone
                if (peg.holeType === 'home' && peg.lockedToSafeZone && !peg.completedCircuit) {
                    if (!peg.eligibleForSafeZone) {
                        console.warn(`🔧 [Audit] ${peg.id}: home peg locked but not eligible — clearing`);
                        peg.lockedToSafeZone = false;
                        fixes++;
                    }
                }

                // Fix 5: Peg holeType doesn't match holeId
                if (peg.holeId && typeof getHoleTypeFromId === 'function') {
                    const expected = getHoleTypeFromId(peg.holeId);
                    if (expected && expected.id !== peg.holeType) {
                        console.warn(`🔧 [Audit] ${peg.id}: holeType mismatch ${peg.holeType} vs ${expected.id} for ${peg.holeId}`);
                        peg.holeType = expected.id;
                        fixes++;
                    }
                }
            }
        }

        if (fixes > 0) {
            console.log(`🔧 [Audit] Applied ${fixes} fixes`);
        }
        return fixes;
    }

    // ── Listener management ──
    onStateChange(listener) {
        this.listeners.add(listener);
        return () => this.listeners.delete(listener);
    }

    _broadcast(eventType, data) {
        const event = { type: eventType, ...data, version: this.stateVersion };
        for (const listener of this.listeners) {
            try {
                listener(event);
            } catch (e) {
                console.error('[SmartPegManager] Listener error:', e);
            }
        }
    }

    // ── Debug/info ──
    getRecentMoves(count = 10) {
        return this.moveLog.slice(-count);
    }

    getStats() {
        return {
            totalMoves: this.moveLog.length,
            errors: this.errorCount,
            stateVersion: this.stateVersion
        };
    }
}


// ============================================================
// GLOBAL INSTANCE
// ============================================================
window.smartPegManager = new SmartPegManager();

// Also expose classes for testing
window.SmartPeg = SmartPeg;
window.BoardAdjacency = BoardAdjacency;
window.SmartPegManager = SmartPegManager;

// ============================================================
// PEG SUBSTRATE INTEGRATION - Gladiator personalities
// ============================================================
(function integratePegSubstrate() {
    // Wait for PegSubstrate to load
    const checkAndIntegrate = () => {
        if (typeof PegSubstrate === 'undefined') {
            setTimeout(checkAndIntegrate, 100);
            return;
        }
        
        console.log('⚔️ [SmartPeg] Integrating with PegSubstrate for gladiator personalities...');
        
        // Extend SmartPegManager with substrate integration
        const manager = window.smartPegManager;
        
        // Enhanced move recording with capture detection
        const originalRecordMove = manager.recordMove.bind(manager);
        manager.recordMove = function(player, peg, move, card) {
            const result = originalRecordMove(player, peg, move, card);
            
            // If this is a capture move, trigger gladiator combat
            if (move.capturedPeg || move.isCapture) {
                const capturerPegId = peg.id;
                const victimPegId = move.capturedPeg?.id || move.capturedPegId;
                const captureHole = move.toHoleId || move.to;
                
                if (victimPegId) {
                    // Ensure both pegs exist in substrate
                    if (!PegSubstrate.getPeg(capturerPegId)) {
                        PegSubstrate.createPegEntity(capturerPegId, player.index, player.color, peg.holeId);
                    }
                    
                    // Execute gladiator capture
                    PegSubstrate.executeCapture(capturerPegId, victimPegId, captureHole);
                }
            }
            
            return result;
        };
        
        // Hook into destination calculation for capture preference
        const originalCalculateDestinations = manager.calculateDestinations.bind(manager);
        manager.calculateDestinations = function(peg, card, player) {
            const destinations = originalCalculateDestinations(peg, card, player);
            
            // Ensure peg exists in substrate
            if (!PegSubstrate.getPeg(peg.id)) {
                PegSubstrate.createPegEntity(peg.id, player.index, player.color, peg.holeId);
            }
            
            // Sort destinations - captures first if peg has gladiator bloodlust
            if (PegSubstrate.wantsToCapture(peg.id)) {
                destinations.sort((a, b) => {
                    const aCapture = a.isCapture || a.capturedPeg ? 1 : 0;
                    const bCapture = b.isCapture || b.capturedPeg ? 1 : 0;
                    return bCapture - aCapture;  // Captures first
                });
            }
            
            return destinations;
        };
        
        // Add method to get peg personality info
        manager.getPegPersonality = function(pegId) {
            const peg = PegSubstrate.getPeg(pegId);
            if (!peg) return null;
            return {
                name: peg.name,
                personality: peg.personality,
                mood: peg.mood,
                moodEmoji: peg.getMoodEmoji(),
                captures: peg.captureCount,
                captured: peg.capturedCount
            };
        };
        
        // Add gladiator leaderboard
        manager.getGladiatorLeaderboard = function() {
            return PegSubstrate.getCaptureLeaderboard();
        };
        
        // Add method to get capture event for UI display
        manager.getLastCaptureEvent = function() {
            const log = PegSubstrate.getManifoldLog({ type: 'CAPTURE', limit: 1 });
            return log.length > 0 ? log[0].data : null;
        };
        
        console.log('⚔️ [SmartPeg] Gladiator integration complete! Pegs now have personalities.');
    };
    
    // Start integration check
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAndIntegrate);
    } else {
        checkAndIntegrate();
    }
})();

console.log('🧠 Smart Peg System loaded — hop-counting movement engine active');
