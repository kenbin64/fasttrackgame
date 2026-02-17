/**
 * Fast Track Game - ButterflyFX Kernel Integration
 * A 2-6 player board game with online multiplayer and AI support
 */

// ===========================================
// GAME CONSTANTS
// ===========================================
const COLORS = {
    0: { name: 'Orange', hex: '#FF6B00', light: '#FF9944' },
    1: { name: 'Brown', hex: '#8B4513', light: '#A0522D' },
    2: { name: 'Red', hex: '#DC143C', light: '#FF4466' },
    3: { name: 'Yellow', hex: '#FFD700', light: '#FFEB3B' },
    4: { name: 'Green', hex: '#228B22', light: '#32CD32' },
    5: { name: 'Blue', hex: '#1E90FF', light: '#4DA6FF' }
};

const PLAYER_POSITIONS = [0, 1, 2, 3, 4, 5]; // Clockwise from top-left

// Board geometry
const BOARD_CENTER_X = 350;
const BOARD_CENTER_Y = 350;
const BOARD_RADIUS = 300;
const TRACK_RADIUS = 220;
const SAFE_ZONE_RADIUS = 100;
const HOME_RADIUS = 60;

// Track: 6 sections, each with entry points and main track
const TRACK_HOLES_PER_SECTION = 10;
const TOTAL_TRACK_HOLES = TRACK_HOLES_PER_SECTION * 6;

// ===========================================
// GAME STATE
// ===========================================
class FastTrackGame {
    constructor() {
        this.canvas = document.getElementById('gameBoard');
        this.ctx = this.canvas.getContext('2d');
        this.players = [];
        this.currentPlayerIndex = 0;
        this.diceValue = null;
        this.gamePhase = 'lobby'; // lobby, playing, finished
        this.selectedPeg = null;
        this.validMoves = [];
        this.gameLog = [];
        this.socket = null;
        this.roomCode = null;
        this.isOnline = false;
        this.isHost = false;
        
        // Board structure
        this.buildBoardGeometry();
        
        // Event listeners
        this.setupEventListeners();
        this.setupLobby();
        
        // Initial render
        this.render();
    }
    
    buildBoardGeometry() {
        // Build all hole positions on the board
        this.holes = {
            track: [],      // Main track around the board (60 holes)
            fastTrack: [],  // Inner fast track (6 holes)
            safeZones: {},  // Safe zones for each color (4 holes each)
            homes: {},      // Home circles for each color (4 peg slots each)
            homeEntry: {},  // Entry point to home for each color
            bullseye: { x: BOARD_CENTER_X, y: BOARD_CENTER_Y }
        };
        
        // Build main track (60 holes in a hexagonal pattern)
        for (let section = 0; section < 6; section++) {
            const startAngle = (section * 60 - 90) * Math.PI / 180;
            const endAngle = ((section + 1) * 60 - 90) * Math.PI / 180;
            
            for (let i = 0; i < TRACK_HOLES_PER_SECTION; i++) {
                const t = i / TRACK_HOLES_PER_SECTION;
                const angle = startAngle + t * (endAngle - startAngle);
                const x = BOARD_CENTER_X + Math.cos(angle) * TRACK_RADIUS;
                const y = BOARD_CENTER_Y + Math.sin(angle) * TRACK_RADIUS;
                this.holes.track.push({
                    x, y,
                    index: section * TRACK_HOLES_PER_SECTION + i,
                    section,
                    isEntry: i === 0 // First hole of each section is entry point
                });
            }
        }
        
        // Build fast track (6 holes in inner circle)
        for (let i = 0; i < 6; i++) {
            const angle = (i * 60 - 90) * Math.PI / 180;
            const x = BOARD_CENTER_X + Math.cos(angle) * 80;
            const y = BOARD_CENTER_Y + Math.sin(angle) * 80;
            this.holes.fastTrack.push({ x, y, index: i });
        }
        
        // Build safe zones and homes for each player color
        for (let player = 0; player < 6; player++) {
            const angle = (player * 60 - 90) * Math.PI / 180;
            const homeX = BOARD_CENTER_X + Math.cos(angle) * 250;
            const homeY = BOARD_CENTER_Y + Math.sin(angle) * 250;
            
            // Home circle (where pegs start)
            this.holes.homes[player] = [];
            for (let p = 0; p < 4; p++) {
                const pegAngle = (p * 90) * Math.PI / 180;
                const px = homeX + Math.cos(pegAngle) * 20;
                const py = homeY + Math.sin(pegAngle) * 20;
                this.holes.homes[player].push({ x: px, y: py, index: p });
            }
            
            // Safe zone (4 holes leading to center)
            this.holes.safeZones[player] = [];
            for (let s = 0; s < 4; s++) {
                const safeRadius = 140 - s * 25;
                const sx = BOARD_CENTER_X + Math.cos(angle) * safeRadius;
                const sy = BOARD_CENTER_Y + Math.sin(angle) * safeRadius;
                this.holes.safeZones[player].push({ x: sx, y: sy, index: s });
            }
            
            // Home entry (final destination)
            this.holes.homeEntry[player] = {
                x: BOARD_CENTER_X + Math.cos(angle) * 170,
                y: BOARD_CENTER_Y + Math.sin(angle) * 170
            };
        }
    }
    
    setupEventListeners() {
        // Canvas click for selecting/moving pegs
        this.canvas.addEventListener('click', (e) => this.handleBoardClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleBoardHover(e));
        
        // Roll dice button
        document.getElementById('rollBtn').addEventListener('click', () => this.rollDice());
        
        // New game button
        document.getElementById('newGameBtn').addEventListener('click', () => this.showLobby());
        
        // Rules button
        document.getElementById('rulesBtn').addEventListener('click', () => this.showRules());
    }
    
    setupLobby() {
        const gameModeSelect = document.getElementById('gameMode');
        const playerCountSelect = document.getElementById('playerCount');
        const startBtn = document.getElementById('startGameBtn');
        const roomOption = document.getElementById('roomOption');
        
        gameModeSelect.addEventListener('change', () => {
            roomOption.style.display = gameModeSelect.value === 'online' ? 'flex' : 'none';
            this.updatePlayerSlots();
        });
        
        playerCountSelect.addEventListener('change', () => this.updatePlayerSlots());
        
        startBtn.addEventListener('click', () => this.startGame());
        
        // Initial player slots
        this.updatePlayerSlots();
    }
    
    updatePlayerSlots() {
        const count = parseInt(document.getElementById('playerCount').value);
        const mode = document.getElementById('gameMode').value;
        const container = document.getElementById('playerSlots');
        
        container.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const row = document.createElement('div');
            row.className = 'player-row';
            
            const colorDot = document.createElement('span');
            colorDot.className = 'player-color';
            colorDot.style.background = COLORS[i].hex;
            
            const nameInput = document.createElement('input');
            nameInput.type = 'text';
            nameInput.placeholder = `Player ${i + 1}`;
            nameInput.value = i === 0 ? 'You' : (mode === 'ai' ? 'AI' : `Player ${i + 1}`);
            nameInput.dataset.player = i;
            
            const typeSelect = document.createElement('select');
            typeSelect.dataset.player = i;
            typeSelect.innerHTML = `
                <option value="human" ${i === 0 || mode === 'local' ? 'selected' : ''}>Human</option>
                <option value="ai" ${(mode === 'ai' && i > 0) ? 'selected' : ''}>AI</option>
            `;
            
            row.appendChild(colorDot);
            row.appendChild(nameInput);
            row.appendChild(typeSelect);
            container.appendChild(row);
        }
    }
    
    startGame() {
        const mode = document.getElementById('gameMode').value;
        const count = parseInt(document.getElementById('playerCount').value);
        
        // Build player list
        this.players = [];
        const slots = document.querySelectorAll('#playerSlots .player-row');
        
        slots.forEach((slot, i) => {
            const name = slot.querySelector('input').value || `Player ${i + 1}`;
            const type = slot.querySelector('select').value;
            
            this.players.push({
                id: i,
                name,
                type, // 'human' or 'ai'
                color: COLORS[i],
                pegs: this.initializePlayerPegs(i),
                homeCount: 0, // Pegs in safe zone
                finished: false
            });
        });
        
        // Hide lobby
        document.getElementById('gameLobby').classList.add('hidden');
        
        this.gamePhase = 'playing';
        this.currentPlayerIndex = 0;
        this.diceValue = null;
        this.gameLog = [];
        
        // Connect to server if online
        if (mode === 'online') {
            this.connectToServer();
        } else {
            this.updateConnectionStatus(true);
        }
        
        this.updateUI();
        this.render();
        this.log(`Game started with ${this.players.length} players!`);
        this.log(`${this.getCurrentPlayer().name}'s turn`);
        
        // If first player is AI, trigger their turn
        if (this.getCurrentPlayer().type === 'ai') {
            setTimeout(() => this.playAITurn(), 1000);
        }
    }
    
    initializePlayerPegs(playerId) {
        // Each player starts with 5 pegs in their home
        const pegs = [];
        for (let i = 0; i < 5; i++) {
            pegs.push({
                id: i,
                location: 'home', // home, track, safeZone, finished
                position: i < 4 ? i : 4, // Position within location
                trackIndex: -1 // Position on main track (-1 if not on track)
            });
        }
        return pegs;
    }
    
    showLobby() {
        document.getElementById('gameLobby').classList.remove('hidden');
        this.gamePhase = 'lobby';
    }
    
    getCurrentPlayer() {
        return this.players[this.currentPlayerIndex];
    }
    
    rollDice() {
        if (this.gamePhase !== 'playing') return;
        if (this.diceValue !== null) return; // Already rolled
        if (this.getCurrentPlayer().type === 'ai') return;
        
        // Roll animation
        const diceDisplay = document.getElementById('diceDisplay');
        let rolls = 0;
        const rollInterval = setInterval(() => {
            diceDisplay.textContent = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'][Math.floor(Math.random() * 6)];
            rolls++;
            if (rolls > 10) {
                clearInterval(rollInterval);
                this.diceValue = Math.floor(Math.random() * 6) + 1;
                diceDisplay.textContent = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'][this.diceValue - 1];
                this.log(`${this.getCurrentPlayer().name} rolled ${this.diceValue}`);
                this.calculateValidMoves();
                this.render();
            }
        }, 80);
    }
    
    calculateValidMoves() {
        this.validMoves = [];
        if (!this.diceValue) return;
        
        const player = this.getCurrentPlayer();
        
        player.pegs.forEach((peg, pegIndex) => {
            if (peg.location === 'finished') return;
            
            if (peg.location === 'home') {
                // Can only leave home on 1 or 6
                if (this.diceValue === 1 || this.diceValue === 6) {
                    this.validMoves.push({
                        pegIndex,
                        action: 'enterTrack',
                        targetPosition: player.id * TRACK_HOLES_PER_SECTION
                    });
                }
            } else if (peg.location === 'track') {
                // Calculate new position on track
                let newPos = (peg.trackIndex + this.diceValue) % TOTAL_TRACK_HOLES;
                
                // Check if passing home entry
                const homeEntry = player.id * TRACK_HOLES_PER_SECTION;
                const currentSection = Math.floor(peg.trackIndex / TRACK_HOLES_PER_SECTION);
                const playerSection = player.id;
                
                // If would pass or land on home entry after going around
                if (this.wouldPassHomeEntry(peg.trackIndex, this.diceValue, player.id)) {
                    const stepsToEntry = this.stepsToHomeEntry(peg.trackIndex, player.id);
                    const remaining = this.diceValue - stepsToEntry;
                    
                    if (remaining <= 4) {
                        this.validMoves.push({
                            pegIndex,
                            action: 'enterSafeZone',
                            targetPosition: remaining - 1
                        });
                    }
                } else {
                    this.validMoves.push({
                        pegIndex,
                        action: 'moveTrack',
                        targetPosition: newPos
                    });
                }
            } else if (peg.location === 'safeZone') {
                const newPos = peg.position + this.diceValue;
                if (newPos < 4) {
                    this.validMoves.push({
                        pegIndex,
                        action: 'moveSafeZone',
                        targetPosition: newPos
                    });
                } else if (newPos === 4) {
                    this.validMoves.push({
                        pegIndex,
                        action: 'finish',
                        targetPosition: 4
                    });
                }
            }
        });
        
        // Special: Landing on center (fast track)
        // Special: Bullseye rules
        // TODO: Implement fast track and capture rules
    }
    
    wouldPassHomeEntry(currentPos, steps, playerId) {
        const homeEntry = playerId * TRACK_HOLES_PER_SECTION;
        for (let i = 1; i <= steps; i++) {
            if ((currentPos + i) % TOTAL_TRACK_HOLES === homeEntry) {
                return true;
            }
        }
        return false;
    }
    
    stepsToHomeEntry(currentPos, playerId) {
        const homeEntry = playerId * TRACK_HOLES_PER_SECTION;
        if (currentPos <= homeEntry) {
            return homeEntry - currentPos;
        } else {
            return TOTAL_TRACK_HOLES - currentPos + homeEntry;
        }
    }
    
    handleBoardClick(e) {
        if (this.gamePhase !== 'playing') return;
        if (this.getCurrentPlayer().type === 'ai') return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
        
        // Check if clicked on a valid move
        if (this.validMoves.length > 0) {
            for (const move of this.validMoves) {
                const peg = this.getCurrentPlayer().pegs[move.pegIndex];
                const pegPos = this.getPegPosition(peg, this.currentPlayerIndex);
                
                if (this.distance(x, y, pegPos.x, pegPos.y) < 20) {
                    this.executeMove(move);
                    return;
                }
            }
        }
    }
    
    handleBoardHover(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = (e.clientX - rect.left) * (this.canvas.width / rect.width);
        const y = (e.clientY - rect.top) * (this.canvas.height / rect.height);
        
        // Update cursor if hovering over valid move
        let isOverMove = false;
        for (const move of this.validMoves) {
            const peg = this.getCurrentPlayer().pegs[move.pegIndex];
            const pegPos = this.getPegPosition(peg, this.currentPlayerIndex);
            
            if (this.distance(x, y, pegPos.x, pegPos.y) < 20) {
                isOverMove = true;
                break;
            }
        }
        
        this.canvas.style.cursor = isOverMove ? 'pointer' : 'default';
    }
    
    executeMove(move) {
        const player = this.getCurrentPlayer();
        const peg = player.pegs[move.pegIndex];
        
        switch (move.action) {
            case 'enterTrack':
                peg.location = 'track';
                peg.trackIndex = move.targetPosition;
                this.log(`${player.name} entered the track`);
                break;
                
            case 'moveTrack':
                // Check for captures
                this.checkCapture(move.targetPosition);
                peg.trackIndex = move.targetPosition;
                this.log(`${player.name} moved on track`);
                break;
                
            case 'enterSafeZone':
                peg.location = 'safeZone';
                peg.position = move.targetPosition;
                peg.trackIndex = -1;
                this.log(`${player.name} entered safe zone!`);
                break;
                
            case 'moveSafeZone':
                peg.position = move.targetPosition;
                this.log(`${player.name} advanced in safe zone`);
                break;
                
            case 'finish':
                peg.location = 'finished';
                peg.position = 4;
                player.homeCount++;
                this.log(`${player.name} got a peg home! (${player.homeCount}/5)`);
                
                if (player.homeCount >= 5) {
                    this.log(`🏆 ${player.name} WINS!`);
                    player.finished = true;
                    this.gamePhase = 'finished';
                }
                break;
        }
        
        this.validMoves = [];
        this.diceValue = null;
        document.getElementById('diceDisplay').textContent = '🎲';
        
        // Extra turn on 6
        if (this.diceValue !== 6 && this.gamePhase === 'playing') {
            this.nextTurn();
        } else if (this.diceValue === 6) {
            this.log(`${player.name} rolled 6 - extra turn!`);
        }
        
        this.updateUI();
        this.render();
    }
    
    checkCapture(targetPosition) {
        // Check if any opponent peg is on this position
        this.players.forEach((player, playerIndex) => {
            if (playerIndex === this.currentPlayerIndex) return;
            
            player.pegs.forEach(peg => {
                if (peg.location === 'track' && peg.trackIndex === targetPosition) {
                    // Capture! Send peg back home
                    peg.location = 'home';
                    peg.trackIndex = -1;
                    peg.position = this.getFirstEmptyHome(playerIndex);
                    this.log(`${this.getCurrentPlayer().name} captured ${player.name}'s peg!`);
                }
            });
        });
    }
    
    getFirstEmptyHome(playerId) {
        const occupied = this.players[playerId].pegs
            .filter(p => p.location === 'home')
            .map(p => p.position);
        
        for (let i = 0; i < 4; i++) {
            if (!occupied.includes(i)) return i;
        }
        return 4; // Overflow
    }
    
    nextTurn() {
        do {
            this.currentPlayerIndex = (this.currentPlayerIndex + 1) % this.players.length;
        } while (this.players[this.currentPlayerIndex].finished);
        
        this.log(`${this.getCurrentPlayer().name}'s turn`);
        
        if (this.getCurrentPlayer().type === 'ai') {
            setTimeout(() => this.playAITurn(), 1000);
        }
    }
    
    playAITurn() {
        if (this.gamePhase !== 'playing') return;
        if (this.getCurrentPlayer().type !== 'ai') return;
        
        // Roll dice
        this.diceValue = Math.floor(Math.random() * 6) + 1;
        document.getElementById('diceDisplay').textContent = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'][this.diceValue - 1];
        this.log(`${this.getCurrentPlayer().name} (AI) rolled ${this.diceValue}`);
        
        this.calculateValidMoves();
        this.render();
        
        // AI decision making
        setTimeout(() => {
            if (this.validMoves.length > 0) {
                // Simple AI: prioritize finishing, then captures, then random
                const finishMoves = this.validMoves.filter(m => m.action === 'finish');
                const safeZoneMoves = this.validMoves.filter(m => m.action === 'enterSafeZone' || m.action === 'moveSafeZone');
                const enterMoves = this.validMoves.filter(m => m.action === 'enterTrack');
                
                let chosenMove;
                if (finishMoves.length > 0) {
                    chosenMove = finishMoves[0];
                } else if (safeZoneMoves.length > 0) {
                    chosenMove = safeZoneMoves[Math.floor(Math.random() * safeZoneMoves.length)];
                } else if (enterMoves.length > 0 && Math.random() > 0.3) {
                    chosenMove = enterMoves[0];
                } else {
                    chosenMove = this.validMoves[Math.floor(Math.random() * this.validMoves.length)];
                }
                
                this.executeMove(chosenMove);
            } else {
                this.log(`${this.getCurrentPlayer().name} (AI) has no valid moves`);
                this.validMoves = [];
                this.diceValue = null;
                document.getElementById('diceDisplay').textContent = '🎲';
                this.nextTurn();
                this.updateUI();
                this.render();
            }
        }, 800);
    }
    
    getPegPosition(peg, playerId) {
        if (peg.location === 'home') {
            const home = this.holes.homes[playerId][Math.min(peg.position, 3)];
            return { x: home.x, y: home.y };
        } else if (peg.location === 'track') {
            const hole = this.holes.track[peg.trackIndex];
            return { x: hole.x, y: hole.y };
        } else if (peg.location === 'safeZone') {
            const safe = this.holes.safeZones[playerId][peg.position];
            return { x: safe.x, y: safe.y };
        } else if (peg.location === 'finished') {
            return this.holes.homeEntry[playerId];
        }
        return { x: 0, y: 0 };
    }
    
    distance(x1, y1, x2, y2) {
        return Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
    }
    
    log(message) {
        this.gameLog.unshift(message);
        if (this.gameLog.length > 50) this.gameLog.pop();
        
        const logEl = document.getElementById('gameLog');
        logEl.innerHTML = this.gameLog.map(m => `<div class="log-entry">${m}</div>`).join('');
    }
    
    updateUI() {
        // Update player list
        const playerList = document.getElementById('playerList');
        playerList.innerHTML = this.players.map((player, i) => `
            <li class="player-item ${i === this.currentPlayerIndex ? 'active' : ''} ${player.finished ? 'winner' : ''}">
                <span class="player-color" style="background: ${player.color.hex}"></span>
                <span class="player-name">${player.name}${player.type === 'ai' ? ' 🤖' : ''}</span>
                <span class="player-pegs">${player.homeCount}/5</span>
            </li>
        `).join('');
        
        // Update roll button
        const rollBtn = document.getElementById('rollBtn');
        const isHumanTurn = this.getCurrentPlayer()?.type === 'human';
        rollBtn.disabled = !isHumanTurn || this.diceValue !== null || this.gamePhase !== 'playing';
    }
    
    updateConnectionStatus(connected) {
        const status = document.getElementById('connectionStatus');
        const text = document.getElementById('statusText');
        
        if (connected) {
            status.classList.remove('disconnected');
            status.classList.add('connected');
            text.textContent = this.isOnline ? 'Online' : 'Local';
        } else {
            status.classList.remove('connected');
            status.classList.add('disconnected');
            text.textContent = 'Offline';
        }
    }
    
    connectToServer() {
        const roomCode = document.getElementById('roomCode').value || this.generateRoomCode();
        this.roomCode = roomCode;
        this.isOnline = true;
        
        // WebSocket connection - use dedicated WS server port
        const wsHost = location.hostname;
        const wsPort = 8765; // Fast Track WebSocket server port
        const wsUrl = `ws://${wsHost}:${wsPort}/ws/fasttrack/${roomCode}`;
        
        this.log(`Connecting to room: ${roomCode}...`);
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                this.updateConnectionStatus(true);
                this.log(`Connected to room: ${roomCode}`);
                
                // Send join message
                this.socket.send(JSON.stringify({
                    type: 'join',
                    name: this.players[0]?.name || 'Player'
                }));
            };
            
            this.socket.onmessage = (e) => this.handleServerMessage(JSON.parse(e.data));
            
            this.socket.onclose = () => {
                this.updateConnectionStatus(false);
                this.log('Disconnected from server');
            };
            
            this.socket.onerror = (err) => {
                console.error('WebSocket error:', err);
                this.updateConnectionStatus(false);
                this.log('Connection failed - playing locally');
                this.isOnline = false;
            };
        } catch (err) {
            console.error('Failed to connect:', err);
            this.updateConnectionStatus(false);
            this.isOnline = false;
        }
    }
    
    generateRoomCode() {
        return Math.random().toString(36).substring(2, 8).toUpperCase();
    }
    
    handleServerMessage(data) {
        switch (data.type) {
            case 'gameState':
                this.syncGameState(data.state);
                break;
            case 'move':
                this.executeMove(data.move);
                break;
            case 'playerJoined':
                this.log(`${data.playerName} joined the game`);
                break;
            case 'playerLeft':
                this.log(`${data.playerName} left the game`);
                break;
        }
    }
    
    sendToServer(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }
    
    syncGameState(state) {
        this.players = state.players;
        this.currentPlayerIndex = state.currentPlayerIndex;
        this.diceValue = state.diceValue;
        this.gamePhase = state.gamePhase;
        this.updateUI();
        this.render();
    }
    
    showRules() {
        alert(`
FAST TRACK RULES

🎯 OBJECTIVE:
Get all 5 of your pegs "home" before your opponents.

🎲 GAMEPLAY:
1. Roll the dice on your turn
2. Move one peg the number shown
3. Roll 1 or 6 to move a peg from home to the track
4. Roll 6 = bonus turn!

⚡ SPECIAL MOVES:
• Land on opponent's peg = capture (send them home)
• Enter the center star = Fast Track shortcut
• Land on Bullseye = teleport to any outer position

🏠 WINNING:
• Move 4 pegs to your safe zone (colored strip)
• Move your 5th peg to the home entry space
• First player to complete this wins!
        `);
    }
    
    // ===========================================
    // RENDERING
    // ===========================================
    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw board background (hexagon)
        this.drawBoardBackground();
        
        // Draw track holes
        this.drawTrack();
        
        // Draw fast track (center star)
        this.drawFastTrack();
        
        // Draw player homes and safe zones
        this.drawPlayerAreas();
        
        // Draw all pegs
        this.drawPegs();
        
        // Draw valid move highlights
        this.drawValidMoveHighlights();
    }
    
    drawBoardBackground() {
        const ctx = this.ctx;
        
        // Wood texture hexagon
        ctx.save();
        ctx.beginPath();
        for (let i = 0; i < 6; i++) {
            const angle = (i * 60 - 30) * Math.PI / 180;
            const x = BOARD_CENTER_X + Math.cos(angle) * BOARD_RADIUS;
            const y = BOARD_CENTER_Y + Math.sin(angle) * BOARD_RADIUS;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        
        // Wood gradient
        const gradient = ctx.createRadialGradient(
            BOARD_CENTER_X, BOARD_CENTER_Y, 0,
            BOARD_CENTER_X, BOARD_CENTER_Y, BOARD_RADIUS
        );
        gradient.addColorStop(0, '#D4A574');
        gradient.addColorStop(1, '#B8956E');
        ctx.fillStyle = gradient;
        ctx.fill();
        
        // Border
        ctx.strokeStyle = '#8B6914';
        ctx.lineWidth = 4;
        ctx.stroke();
        ctx.restore();
    }
    
    drawTrack() {
        const ctx = this.ctx;
        
        // Draw main track holes
        this.holes.track.forEach(hole => {
            ctx.beginPath();
            ctx.arc(hole.x, hole.y, 8, 0, Math.PI * 2);
            ctx.fillStyle = '#3D2914';
            ctx.fill();
            ctx.strokeStyle = '#2D1D0A';
            ctx.lineWidth = 1;
            ctx.stroke();
        });
    }
    
    drawFastTrack() {
        const ctx = this.ctx;
        
        // Draw center star
        ctx.save();
        ctx.beginPath();
        for (let i = 0; i < 12; i++) {
            const angle = (i * 30 - 90) * Math.PI / 180;
            const radius = i % 2 === 0 ? 50 : 25;
            const x = BOARD_CENTER_X + Math.cos(angle) * radius;
            const y = BOARD_CENTER_Y + Math.sin(angle) * radius;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fillStyle = '#1a1a2e';
        ctx.fill();
        ctx.strokeStyle = '#0a0a14';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Bullseye center
        ctx.beginPath();
        ctx.arc(BOARD_CENTER_X, BOARD_CENTER_Y, 12, 0, Math.PI * 2);
        ctx.fillStyle = '#D4A574';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(BOARD_CENTER_X, BOARD_CENTER_Y, 6, 0, Math.PI * 2);
        ctx.fillStyle = '#3D2914';
        ctx.fill();
        
        // Fast track holes
        this.holes.fastTrack.forEach(hole => {
            ctx.beginPath();
            ctx.arc(hole.x, hole.y, 8, 0, Math.PI * 2);
            ctx.fillStyle = '#3D2914';
            ctx.fill();
        });
        
        ctx.restore();
    }
    
    drawPlayerAreas() {
        const ctx = this.ctx;
        
        for (let p = 0; p < 6; p++) {
            const color = COLORS[p];
            const angle = (p * 60 - 90) * Math.PI / 180;
            
            // Home circle
            const homeX = BOARD_CENTER_X + Math.cos(angle) * 250;
            const homeY = BOARD_CENTER_Y + Math.sin(angle) * 250;
            
            ctx.beginPath();
            ctx.arc(homeX, homeY, 35, 0, Math.PI * 2);
            ctx.fillStyle = color.hex;
            ctx.fill();
            ctx.strokeStyle = '#2D1D0A';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Home peg slots
            this.holes.homes[p].forEach(slot => {
                ctx.beginPath();
                ctx.arc(slot.x, slot.y, 10, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                ctx.fill();
            });
            
            // Safe zone (oval)
            const safeX = BOARD_CENTER_X + Math.cos(angle) * 160;
            const safeY = BOARD_CENTER_Y + Math.sin(angle) * 160;
            
            ctx.save();
            ctx.translate(safeX, safeY);
            ctx.rotate(angle + Math.PI / 2);
            ctx.beginPath();
            ctx.ellipse(0, 0, 15, 50, 0, 0, Math.PI * 2);
            ctx.fillStyle = color.hex;
            ctx.fill();
            ctx.strokeStyle = '#2D1D0A';
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.restore();
            
            // Safe zone holes
            this.holes.safeZones[p].forEach(hole => {
                ctx.beginPath();
                ctx.arc(hole.x, hole.y, 6, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                ctx.fill();
            });
            
            // Home entry diamond
            const entryX = BOARD_CENTER_X + Math.cos(angle) * 200;
            const entryY = BOARD_CENTER_Y + Math.sin(angle) * 200;
            
            ctx.save();
            ctx.translate(entryX, entryY);
            ctx.rotate(Math.PI / 4);
            ctx.fillStyle = color.hex;
            ctx.fillRect(-8, -8, 16, 16);
            ctx.strokeStyle = '#2D1D0A';
            ctx.lineWidth = 1;
            ctx.strokeRect(-8, -8, 16, 16);
            ctx.restore();
        }
    }
    
    drawPegs() {
        const ctx = this.ctx;
        
        this.players.forEach((player, playerIndex) => {
            player.pegs.forEach(peg => {
                const pos = this.getPegPosition(peg, playerIndex);
                
                // Peg shadow
                ctx.beginPath();
                ctx.arc(pos.x + 2, pos.y + 2, 12, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0,0,0,0.3)';
                ctx.fill();
                
                // Peg body
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 12, 0, Math.PI * 2);
                
                const gradient = ctx.createRadialGradient(
                    pos.x - 4, pos.y - 4, 0,
                    pos.x, pos.y, 12
                );
                gradient.addColorStop(0, player.color.light);
                gradient.addColorStop(1, player.color.hex);
                ctx.fillStyle = gradient;
                ctx.fill();
                
                ctx.strokeStyle = 'rgba(0,0,0,0.5)';
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Highlight shine
                ctx.beginPath();
                ctx.arc(pos.x - 3, pos.y - 3, 4, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255,255,255,0.4)';
                ctx.fill();
            });
        });
    }
    
    drawValidMoveHighlights() {
        if (this.validMoves.length === 0) return;
        
        const ctx = this.ctx;
        const player = this.getCurrentPlayer();
        
        this.validMoves.forEach(move => {
            const peg = player.pegs[move.pegIndex];
            const pos = this.getPegPosition(peg, this.currentPlayerIndex);
            
            // Glowing ring around movable peg
            ctx.save();
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, 18, 0, Math.PI * 2);
            ctx.strokeStyle = '#00ff88';
            ctx.lineWidth = 3;
            ctx.shadowColor = '#00ff88';
            ctx.shadowBlur = 10;
            ctx.stroke();
            ctx.restore();
        });
    }
}

// ===========================================
// INITIALIZE GAME
// ===========================================
document.addEventListener('DOMContentLoaded', () => {
    window.game = new FastTrackGame();
});
