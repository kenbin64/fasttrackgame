#!/usr/bin/env node
// FastTrack WebSocket Lobby Server v2
// Speaks the full lobby_client.js protocol
// Usage: node ws_lobby_server.js

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8765;

const app = express();
app.use(express.json());
app.get('/', (req, res) => res.send('FastTrack WS Lobby Server OK'));

// Persistent user store
const USERS_FILE = path.join(__dirname, 'users.json');
let usersData = { users: [] };
try { usersData = JSON.parse(fs.readFileSync(USERS_FILE)); } catch (e) { console.warn('[Lobby] No users.json, starting fresh'); }

function saveUsers() { fs.writeFileSync(USERS_FILE, JSON.stringify(usersData, null, 2)); }
function findUserByUsername(u) { return usersData.users.find(x => x.username === u); }
function findUserById(id) { return usersData.users.find(x => x.id === id); }

// HTTP auth token store
const httpSessions = new Map();
function genToken() { return 't_' + Math.random().toString(36).slice(2) + Date.now().toString(36); }

// In-memory WS state
const clients = new Map();
const gameSessions = new Map();

function genId(prefix) { return prefix + '_' + Date.now() + '_' + Math.floor(Math.random() * 9000 + 1000); }
function genCode() { return Math.random().toString(36).slice(2, 6).toUpperCase(); }

function send(ws, obj) { try { ws.send(JSON.stringify(obj)); } catch (e) {} }

function broadcastToSession(sessionId, obj, excludeWs) {
    for (const [ws, info] of clients.entries()) {
        if (info.session_id === sessionId && ws !== excludeWs && ws.readyState === WebSocket.OPEN) {
            send(ws, obj);
        }
    }
}

function broadcastAll(obj, excludeWs) {
    for (const [ws] of clients.entries()) {
        if (ws !== excludeWs && ws.readyState === WebSocket.OPEN) send(ws, obj);
    }
}

function makeUserObj(info) {
    return {
        user_id:         info.user_id,
        id:              info.user_id,
        username:        info.username,
        is_guest:        info.is_guest,
        avatar_id:       info.avatar_id       || 'person_smile',
        prestige_level:  info.prestige_level  || 'bronze',
        prestige_points: info.prestige_points || 0,
        games_played:    info.games_played    || 0,
        games_won:       info.games_won       || 0,
    };
}

function makePlayerSlot(info, slot, isHost) {
    return {
        user_id:   info.user_id,
        username:  info.username,
        avatar_id: info.avatar_id || 'person_smile',
        is_host:   !!isHost,
        is_ai:     false,
        is_bot:    false,
        slot,
    };
}

function makeAiSlot(slot, level) {
    return {
        user_id:  genId('bot'),
        username: 'AI Player',
        avatar_id:'robot',
        is_host:  false,
        is_ai:    true,
        is_bot:   true,
        ai_level: level || 'medium',
        slot,
    };
}

function publicSessions() {
    const list = [];
    for (const s of gameSessions.values()) {
        if (!s.is_private && s.status === 'waiting') {
            list.push({
                session_id:   s.session_id,
                session_code: s.session_code,
                host_name:    s.host_name,
                player_count: s.players.length,
                max_players:  s.max_players,
                is_private:   false,
            });
        }
    }
    return list;
}

// HTTP Auth endpoints
app.post('/api/login', (req, res) => {
    const { username, password } = req.body || {};
    if (!username || !password) return res.status(400).json({ error: 'username+password required' });
    const user = findUserByUsername(username);
    if (!user || user.password !== password) return res.status(401).json({ error: 'invalid credentials' });
    if (user.suspendedUntil && Date.now() < user.suspendedUntil) return res.status(403).json({ error: 'user suspended' });
    const token = genToken();
    httpSessions.set(token, { userId: user.id, expires: Date.now() + 86400000 });
    res.json({ token, user: { id: user.id, username: user.username, role: user.role } });
});

app.post('/api/logout', (req, res) => {
    const token = (req.headers['authorization'] || '').replace('Bearer ', '');
    if (token) httpSessions.delete(token);
    res.json({ ok: true });
});

app.get('/api/me', (req, res) => {
    const token = (req.headers['authorization'] || '').replace('Bearer ', '');
    const s = httpSessions.get(token);
    if (!s) return res.status(401).json({ error: 'not authenticated' });
    const user = findUserById(s.userId);
    if (!user) return res.status(401).json({ error: 'user not found' });
    res.json({ id: user.id, username: user.username, role: user.role });
});

function requireAuth(req) {
    const token = (req.headers['authorization'] || '').replace('Bearer ', '');
    const s = httpSessions.get(token);
    if (!s) return null;
    return findUserById(s.userId);
}

app.post('/api/admin/create_admin', (req, res) => {
    const caller = requireAuth(req);
    if (!caller || caller.role !== 'superuser') return res.status(403).json({ error: 'forbidden' });
    const { username, password } = req.body || {};
    if (!username || !password) return res.status(400).json({ error: 'username+password required' });
    if (findUserByUsername(username)) return res.status(400).json({ error: 'user exists' });
    const id = 'u_' + Date.now() + '_' + Math.floor(Math.random() * 9000);
    const u = { id, username, password, role: 'admin', suspendedUntil: 0 };
    usersData.users.push(u); saveUsers();
    res.json({ ok: true, user: { id: u.id, username: u.username, role: u.role } });
});

app.post('/api/admin/promote', (req, res) => {
    const caller = requireAuth(req);
    if (!caller || caller.role !== 'superuser') return res.status(403).json({ error: 'forbidden' });
    const { username } = req.body || {};
    if (!username) return res.status(400).json({ error: 'username required' });
    const u = findUserByUsername(username);
    if (!u) return res.status(404).json({ error: 'not found' });
    u.role = 'admin'; saveUsers();
    res.json({ ok: true, user: { id: u.id, username: u.username, role: u.role } });
});

app.post('/api/admin/kick', (req, res) => {
    const caller = requireAuth(req);
    if (!caller) return res.status(403).json({ error: 'forbidden' });
    const { username } = req.body || {};
    if (!username) return res.status(400).json({ error: 'username required' });
    const target = findUserByUsername(username);
    if (!target) return res.status(404).json({ error: 'not found' });
    if (target.role === 'superuser') return res.status(403).json({ error: 'cannot kick superuser' });
    if (target.role === 'admin' && caller.role !== 'superuser') return res.status(403).json({ error: 'cannot kick admin' });
    for (const [t, s] of httpSessions.entries()) { if (s.userId === target.id) httpSessions.delete(t); }
    res.json({ ok: true });
});

app.post('/api/admin/suspend', (req, res) => {
    const caller = requireAuth(req);
    if (!caller) return res.status(403).json({ error: 'forbidden' });
    const { username, seconds } = req.body || {};
    if (!username || !seconds) return res.status(400).json({ error: 'username+seconds required' });
    const target = findUserByUsername(username);
    if (!target) return res.status(404).json({ error: 'not found' });
    if (target.role === 'superuser') return res.status(403).json({ error: 'cannot suspend superuser' });
    if (target.role === 'admin' && caller.role !== 'superuser') return res.status(403).json({ error: 'cannot suspend admin' });
    target.suspendedUntil = Date.now() + (parseInt(seconds, 10) || 0) * 1000; saveUsers();
    for (const [t, s] of httpSessions.entries()) { if (s.userId === target.id) httpSessions.delete(t); }
    res.json({ ok: true });
});

app.get('/api/admin/users', (req, res) => {
    const caller = requireAuth(req);
    if (!caller || !['admin', 'superuser'].includes(caller.role)) return res.status(403).json({ error: 'forbidden' });
    res.json({ users: usersData.users.map(u => ({ id: u.id, username: u.username, role: u.role, suspendedUntil: u.suspendedUntil || 0 })) });
});

// WebSocket server
const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/ws' });

wss.on('connection', (ws) => {
    const tempId = genId('guest');
    clients.set(ws, {
        user_id: tempId, username: tempId, is_guest: true,
        avatar_id: 'person_smile', prestige_level: 'bronze',
        prestige_points: 0, games_played: 0, games_won: 0, session_id: null
    });
    console.log('[Lobby] New connection:', tempId);
    send(ws, { type: 'connected', user_id: tempId });

    ws.on('message', (msg) => {
        let data;
        try { data = JSON.parse(msg); } catch (e) { return; }
        const info = clients.get(ws);
        if (!info) return;
        handleMessage(ws, info, data);
    });

    ws.on('close', () => {
        const info = clients.get(ws) || {};
        console.log('[Lobby] Disconnected:', info.username || info.user_id);
        handleDisconnect(info);
        clients.delete(ws);
    });
});

function handleMessage(ws, info, data) {
    switch (data.type) {

        case 'guest_login': {
            info.username  = data.name || data.username || ('Guest_' + Math.random().toString(36).slice(2, 6));
            info.is_guest  = true;
            info.avatar_id = data.avatar_id || 'person_smile';
            clients.set(ws, info);
            send(ws, { type: 'auth_success', action: 'guest_login', user: makeUserObj(info) });
            break;
        }

        case 'login': {
            const user = findUserByUsername(data.username);
            if (!user || user.password !== data.password) { send(ws, { type: 'error', message: 'Invalid username or password' }); break; }
            if (user.suspendedUntil && Date.now() < user.suspendedUntil) { send(ws, { type: 'error', message: 'Account suspended' }); break; }
            Object.assign(info, {
                user_id: user.id, username: user.username, is_guest: false,
                avatar_id: user.avatar_id || 'person_smile',
                prestige_level: user.prestige_level || 'bronze',
                prestige_points: user.prestige_points || 0,
                games_played: user.games_played || 0,
                games_won: user.games_won || 0,
            });
            clients.set(ws, info);
            send(ws, { type: 'auth_success', action: 'login', user: makeUserObj(info) });
            break;
        }

        case 'register': {
            if (findUserByUsername(data.username)) { send(ws, { type: 'error', message: 'Username already taken' }); break; }
            const newUser = {
                id: genId('u'), username: data.username, password: data.password,
                email: data.email || '', role: 'user',
                avatar_id: 'person_smile', prestige_level: 'bronze',
                prestige_points: 0, games_played: 0, games_won: 0, suspendedUntil: 0,
            };
            usersData.users.push(newUser); saveUsers();
            Object.assign(info, { user_id: newUser.id, username: newUser.username, is_guest: false, avatar_id: 'person_smile', prestige_level: 'bronze', prestige_points: 0 });
            clients.set(ws, info);
            send(ws, { type: 'auth_success', action: 'register', user: makeUserObj(info) });
            break;
        }

        case 'logout':
            send(ws, { type: 'logged_out' });
            break;

        case 'ping':
            send(ws, { type: 'pong' });
            break;

        case 'get_profile':
            send(ws, { type: 'profile', user: makeUserObj(info) });
            break;

        case 'update_profile': {
            if (data.avatar_id) info.avatar_id = data.avatar_id;
            if (data.username && !info.is_guest) info.username = data.username;
            clients.set(ws, info);
            if (!info.is_guest) {
                const u = findUserById(info.user_id);
                if (u) { u.avatar_id = info.avatar_id; u.username = info.username; saveUsers(); }
            }
            send(ws, { type: 'profile_updated', user: makeUserObj(info) });
            break;
        }

        case 'update_player_info': {
            if (data.username) info.username = data.username;
            if (data.avatar_id) info.avatar_id = data.avatar_id;
            clients.set(ws, info);
            if (info.session_id) {
                const sess = gameSessions.get(info.session_id);
                if (sess) {
                    const slot = sess.players.find(p => p.user_id === info.user_id);
                    if (slot) { slot.username = info.username; slot.avatar_id = info.avatar_id; }
                }
            }
            break;
        }

        case 'list_sessions':
            send(ws, { type: 'session_list', sessions: publicSessions() });
            break;

        case 'create_session': {
            const code = genCode();
            const sessId = genId('sess');
            const hostSlot = makePlayerSlot(info, 0, true);
            const sess = {
                session_id:   sessId,
                session_code: code,
                host_id:      info.user_id,
                host_name:    info.username,
                is_private:   data.private !== false,
                max_players:  data.max_players || 4,
                status:       'waiting',
                players:      [hostSlot],
                settings:     data.settings || {},
            };
            gameSessions.set(sessId, sess);
            info.session_id = sessId;
            clients.set(ws, info);
            const shareUrl = (data.origin || 'https://kensgames.com') + '/fasttrack/join.html?code=' + code;
            send(ws, { type: 'session_created', session: sess, share_code: code, share_url: shareUrl });
            broadcastAll({ type: 'lobby_update', action: 'session_created' }, ws);
            console.log('[Lobby] Session created', sessId, 'by', info.username);
            break;
        }

        case 'join_session': {
            const sess = gameSessions.get(data.session_id);
            if (!sess) { send(ws, { type: 'error', message: 'Session not found' }); break; }
            if (sess.players.length >= sess.max_players) { send(ws, { type: 'error', message: 'Session full' }); break; }
            const slot = makePlayerSlot(info, sess.players.length, false);
            sess.players.push(slot);
            info.session_id = sess.session_id;
            clients.set(ws, info);
            send(ws, { type: 'session_joined', session: sess });
            broadcastToSession(sess.session_id, { type: 'player_joined', player: slot, players: sess.players }, ws);
            break;
        }

        case 'join_by_code': {
            let found = null;
            for (const s of gameSessions.values()) {
                if (s.session_code === (data.code || '').toUpperCase()) { found = s; break; }
            }
            if (!found) { send(ws, { type: 'error', message: 'Game code not found' }); break; }
            if (found.players.length >= found.max_players) { send(ws, { type: 'error', message: 'Game is full' }); break; }
            const slot = makePlayerSlot(info, found.players.length, false);
            found.players.push(slot);
            info.session_id = found.session_id;
            clients.set(ws, info);
            send(ws, { type: 'session_joined', session: found });
            broadcastToSession(found.session_id, { type: 'player_joined', player: slot, players: found.players }, ws);
            break;
        }

        case 'leave_session': {
            const sess = gameSessions.get(info.session_id);
            if (sess) {
                sess.players = sess.players.filter(p => p.user_id !== info.user_id);
                broadcastToSession(sess.session_id, { type: 'player_left', username: info.username, players: sess.players });
                if (sess.players.filter(p => !p.is_ai).length === 0) {
                    gameSessions.delete(sess.session_id);
                    broadcastAll({ type: 'lobby_update', action: 'session_removed' });
                }
            }
            info.session_id = null;
            clients.set(ws, info);
            send(ws, { type: 'left_session' });
            break;
        }

        case 'add_ai_player': {
            const sess = gameSessions.get(info.session_id);
            if (!sess) { send(ws, { type: 'error', message: 'Not in a session' }); break; }
            if (sess.players.length >= sess.max_players) { send(ws, { type: 'error', message: 'Session full' }); break; }
            const bot = makeAiSlot(sess.players.length, data.level);
            sess.players.push(bot);
            broadcastToSession(sess.session_id, { type: 'player_joined', player: bot, players: sess.players });
            send(ws, { type: 'player_joined', player: bot, players: sess.players });
            break;
        }

        case 'remove_ai_player': {
            const sess = gameSessions.get(info.session_id);
            if (!sess) break;
            const aiWithIndex = sess.players.map((p, i) => ({ p, i })).filter(x => x.p.is_ai);
            if (aiWithIndex.length === 0) break;
            const tgt = data.player_id
                ? aiWithIndex.find(x => x.p.user_id === data.player_id)
                : aiWithIndex[aiWithIndex.length - 1];
            if (!tgt) break;
            const removed = sess.players.splice(tgt.i, 1)[0];
            broadcastToSession(sess.session_id, { type: 'player_left', username: removed.username, players: sess.players });
            send(ws, { type: 'player_left', username: removed.username, players: sess.players });
            break;
        }

        case 'update_session_settings': {
            const sess = gameSessions.get(info.session_id);
            if (sess && sess.host_id === info.user_id) {
                Object.assign(sess.settings, data.settings || {});
                if (data.max_players) sess.max_players = data.max_players;
            }
            break;
        }

        case 'start_game': {
            const sess = gameSessions.get(info.session_id);
            if (!sess) { send(ws, { type: 'error', message: 'Not in a session' }); break; }
            sess.status = 'playing';
            broadcastToSession(sess.session_id, { type: 'game_started', session: sess });
            send(ws, { type: 'game_started', session: sess });
            console.log('[Lobby] Game started in session', sess.session_id);
            break;
        }

        case 'chat': {
            const chatMsg = { type: 'chat', username: info.username, message: data.message, ts: Date.now() };
            if (info.session_id) {
                broadcastToSession(info.session_id, chatMsg);
                send(ws, chatMsg);
            }
            break;
        }

        default:
            // Silently ignore unknown messages (guild, leaderboard, etc.)
            break;
    }
}

function handleDisconnect(info) {
    if (!info.session_id) return;
    const sess = gameSessions.get(info.session_id);
    if (!sess) return;
    sess.players = sess.players.filter(p => p.user_id !== info.user_id);
    broadcastToSession(sess.session_id, { type: 'player_left', username: info.username, players: sess.players });
    if (sess.players.filter(p => !p.is_ai).length === 0) {
        gameSessions.delete(sess.session_id);
        broadcastAll({ type: 'lobby_update', action: 'session_removed' });
    }
}

server.listen(PORT, () => {
    console.log('[Lobby] WebSocket lobby server listening on http://localhost:' + PORT);
});
