// Lightweight preview server for serving the /web directory
// Usage: node server/preview_server.js

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;

const webRoot = path.join(__dirname, '..', 'web');

// Basic request logging
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// Serve static files from /web
app.use(express.static(webRoot, {
  extensions: ['html', 'htm'],
  fallthrough: true,
  etag: false,
  lastModified: false,
  maxAge: 0,
}));

// Convenience route to demo BrickBreaker3D
app.get('/play/brickbreaker3d', (req, res) => {
  // Append demo params to trigger auto-start (handled by index.html patch)
  const params = new URLSearchParams({ mode: 'single', demo: '1' }).toString();
  res.redirect(`/kensgames/brickbreaker3d/index.html?${params}`);
});

// Fallback to index for arbitrary routes under play/
app.get('/play/*', (req, res) => {
  res.redirect('/');
});

app.listen(PORT, () => {
  console.log(`Preview server running at http://localhost:${PORT}`);
  console.log(`BrickBreaker3D demo: http://localhost:${PORT}/play/brickbreaker3d`);
});
