# Deprecation: Klassics3D Breakout

Date: March 2026

The Klassics3D Breakout prototype (web/games/klassics3d/breakout3d) has been removed from the main web bundle.

Why we removed it
- Prototype-level physics and collision logic, not representative of current standards
- No tests or documentation beyond inline comments
- Focus move to demos that exercise dimensional primitives, manifolds, and the Universal Substrate

What to use instead
- FastTrack demo (2D) at `web/games/fasttrack/` with maintained assets and documentation
- Manifold and substrate demos at `web/manifold/` and the root landing pages under `web/`

Migration or self-hosting
- A minimal archival note is kept at `web/_archive/klassics3d/README.md`
- If you need a copy, restore the deleted files from version control into your own app namespace and include `web/assets/js/three.min.js`

Operator guidance
- Remove any route entries and navigation links to `/games/klassics3d/breakout3d/index.html`
- If you run a service worker or asset pre-cache, purge the breakout3d assets to avoid 404s
- Consider returning HTTP 410 (Gone) for the removed path for a limited period
