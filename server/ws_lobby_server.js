#!/usr/bin/env node
// Simple WebSocket lobby server for FastTrack
// Usage: node ws_lobby_server.js

const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8765;

const app = express();
app.use(express.json());
app.get('/', (req, res) => res.send('FastTrack WS Lobby Server'));

// Simple user/session store
const USERS_FILE = path.join(__dirname, 'users.json');
let usersData = { users: [] };
try { usersData = JSON.parse(fs.readFileSync(USERS_FILE)); } catch (e) { console.warn('No users.json found, starting empty'); }

const sessions = new Map(); // token -> { userId, expires }

function saveUsers(){ fs.writeFileSync(USERS_FILE, JSON.stringify(usersData, null, 2)); }

function findUserByUsername(username){ return usersData.users.find(u => u.username === username); }
function findUserById(id){ return usersData.users.find(u => u.id === id); }

function genToken(){ return 't_' + Math.random().toString(36).slice(2) + Date.now().toString(36); }

// Auth endpoints
app.post('/api/login', (req, res) => {
  const { username, password } = req.body || {};
  if(!username || !password) return res.status(400).json({ error: 'username+password required' });
  const user = findUserByUsername(username);
  if(!user || user.password !== password) return res.status(401).json({ error: 'invalid credentials' });
  if(user.suspendedUntil && Date.now() < user.suspendedUntil) return res.status(403).json({ error: 'user suspended' });
  const token = genToken();
  sessions.set(token, { userId: user.id, expires: Date.now() + 1000*60*60*24 });
  res.json({ token, user: { id: user.id, username: user.username, role: user.role } });
});

app.post('/api/logout', (req, res) => {
  const auth = req.headers['authorization'] || '';
  const token = auth.replace('Bearer ','');
  if(token) sessions.delete(token);
  res.json({ ok:true });
});

app.get('/api/me', (req, res) => {
  const auth = req.headers['authorization'] || '';
  const token = auth.replace('Bearer ','');
  const s = sessions.get(token);
  if(!s) return res.status(401).json({ error: 'not authenticated' });
  const user = findUserById(s.userId);
  if(!user) return res.status(401).json({ error: 'user not found' });
  res.json({ id: user.id, username: user.username, role: user.role });
});

// Admin actions: promote, create admin, kick, suspend
function requireAuth(req){ const auth = req.headers['authorization']||''; const token = auth.replace('Bearer ',''); const s = sessions.get(token); if(!s) return null; return findUserById(s.userId); }

app.post('/api/admin/create_admin', (req, res) => {
  const caller = requireAuth(req); if(!caller || caller.role !== 'superuser') return res.status(403).json({ error: 'forbidden' });
  const { username, password } = req.body || {};
  if(!username||!password) return res.status(400).json({ error: 'username+password required' });
  if(findUserByUsername(username)) return res.status(400).json({ error: 'user exists' });
  const id = 'u_' + Date.now() + '_' + Math.floor(Math.random()*9000);
  const u = { id, username, password, role: 'admin', suspendedUntil: 0 };
  usersData.users.push(u); saveUsers();
  res.json({ ok:true, user: { id: u.id, username: u.username, role: u.role } });
});

app.post('/api/admin/promote', (req, res) => {
  const caller = requireAuth(req); if(!caller || caller.role !== 'superuser') return res.status(403).json({ error: 'forbidden' });
  const { username } = req.body || {}; if(!username) return res.status(400).json({ error: 'username required' });
  const u = findUserByUsername(username); if(!u) return res.status(404).json({ error: 'not found' });
  u.role = 'admin'; saveUsers(); res.json({ ok:true, user: { id:u.id, username:u.username, role:u.role } });
});

app.post('/api/admin/kick', (req, res) => {
  const caller = requireAuth(req); if(!caller) return res.status(403).json({ error: 'forbidden' });
  const { username } = req.body || {}; if(!username) return res.status(400).json({ error: 'username required' });
  const target = findUserByUsername(username); if(!target) return res.status(404).json({ error: 'not found' });
  if(target.role === 'superuser') return res.status(403).json({ error: 'cannot kick superuser' });
  if(target.role === 'admin' && caller.role !== 'superuser') return res.status(403).json({ error: 'cannot kick admin' });
  // Invalidate sessions for target
  for(const [t,s] of sessions.entries()){ if(s.userId === target.id) sessions.delete(t); }
  res.json({ ok:true });
});

app.post('/api/admin/suspend', (req, res) => {
  const caller = requireAuth(req); if(!caller) return res.status(403).json({ error: 'forbidden' });
  const { username, seconds } = req.body || {};
  if(!username||!seconds) return res.status(400).json({ error: 'username+seconds required' });
  const target = findUserByUsername(username); if(!target) return res.status(404).json({ error: 'not found' });
  if(target.role === 'superuser') return res.status(403).json({ error: 'cannot suspend superuser' });
  if(target.role === 'admin' && caller.role !== 'superuser') return res.status(403).json({ error: 'cannot suspend admin' });
  target.suspendedUntil = Date.now() + (parseInt(seconds,10)||0)*1000; saveUsers();
  // invalidate sessions
  for(const [t,s] of sessions.entries()){ if(s.userId === target.id) sessions.delete(t); }
  res.json({ ok:true });
});

const server = http.createServer(app);
const wss = new WebSocket.Server({ server, path: '/ws' });

// In-memory state (simple, non-persistent)
const clients = new Map(); // ws -> { id, name }
const rooms = new Map(); // roomId -> { id, hostId, players: [clientId], meta }

function send(ws, obj) {
  try { ws.send(JSON.stringify(obj)); } catch (e) {}
}

function broadcastToRoom(roomId, obj) {
  const room = rooms.get(roomId);
  if (!room) return;
  for (const clientId of room.players) {
    for (const [ws, info] of clients.entries()) {
      if (info.id === clientId && ws.readyState === WebSocket.OPEN) {
        send(ws, obj);
      }
    }
  }
}

wss.on('connection', (ws, req) => {
  const clientId = 'guest_' + Date.now() + '_' + Math.floor(Math.random()*10000);
  clients.set(ws, { id: clientId, name: clientId });
  console.log('[Lobby] New connection:', clientId);

  send(ws, { type: 'connected', user_id: clientId });

  ws.on('message', (msg) => {
    let data = null;
    try { data = JSON.parse(msg); } catch (e) { return; }
    const info = clients.get(ws) || {};

    switch (data.type) {
      case 'guest_login':
        info.name = data.name || info.id;
        clients.set(ws, info);
        send(ws, { type: 'login_ok', user_id: info.id, username: info.name });
        break;

      case 'create_room': {
        const roomId = 'room_' + Math.floor(Math.random()*9000 + 1000);
        const room = { id: roomId, hostId: info.id, players: [info.id], meta: data.meta || {} };
        rooms.set(roomId, room);
        send(ws, { type: 'room_created', room });
        console.log('[Lobby] Room created', roomId, 'by', info.id);
        break;
      }

      case 'join_room': {
        const room = rooms.get(data.roomId);
        if (!room) { send(ws, { type: 'error', message: 'Room not found' }); break; }
        if (!room.players.includes(info.id)) room.players.push(info.id);
        send(ws, { type: 'joined_room', room });
        broadcastToRoom(room.id, { type: 'player_joined', player: { id: info.id, name: info.name } });
        console.log('[Lobby] Player', info.id, 'joined', room.id);
        break;
      }

      case 'leave_room': {
        const room = rooms.get(data.roomId);
        if (!room) break;
        room.players = room.players.filter(p => p !== info.id);
        rooms.set(room.id, room);
        broadcastToRoom(room.id, { type: 'player_left', playerId: info.id });
        break;
      }

      case 'start_game': {
        const room = rooms.get(data.roomId);
        if (!room) { send(ws, { type: 'error', message: 'Room not found' }); break; }
        broadcastToRoom(room.id, { type: 'game_started', roomId: room.id });
        console.log('[Lobby] Game started in', room.id);
        break;
      }

      case 'relay': {
        // Generic relay: { type: 'relay', roomId, payload }
        broadcastToRoom(data.roomId, { type: 'relay', from: info.id, payload: data.payload });
        break;
      }

      default:
        // Unknown message
        console.log('[Lobby] Unknown message', data.type);
        break;
    }
  });

  ws.on('close', () => {
    const info = clients.get(ws) || {};
    console.log('[Lobby] Disconnected:', info.id);
    // Remove from rooms
    for (const [id, room] of rooms.entries()) {
      if (room.players.includes(info.id)) {
        room.players = room.players.filter(p => p !== info.id);
        broadcastToRoom(id, { type: 'player_left', playerId: info.id });
      }
    }
    clients.delete(ws);
  });
});

server.listen(PORT, () => {
  console.log(`[Lobby] WebSocket lobby server listening on http://localhost:${PORT}`);
});
