# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this project adheres to Semantic Versioning where applicable.

## [Unreleased]

### Removed
- Retired Klassics3D Breakout demo located at `web/games/klassics3d/breakout3d/` (HTML, JS, CSS). See Deprecation Notice below for rationale and alternatives.

### Deprecated
- Any links or bookmarks to `/games/klassics3d/breakout3d/index.html` are deprecated and will return 404/410 in upcoming deployments.

---

## Deprecation Notice: Klassics3D Breakout (Mar 2026)

The minimal Three.js prototype "3D Breakout" has been removed from the repository as part of a broader cleanup to focus on production-quality demos that align with the Dimensional Computing roadmap.

Rationale:
- Prototype quality: The demo used ad-hoc collision logic and no test coverage.
- Maintenance cost: The Three.js dependency and bespoke input/event handling added surface area without core value to the platform.
- Focus shift: We are consolidating examples around dimensional primitives, manifolds, and Universal Substrate integrations.

Alternatives and migration:
- Active game demo: FastTrack (2D) remains available under `web/games/fasttrack/` with documented rules and assets.
- Manifold demos: Explore `web/manifold/` and the interactive demos on the landing pages for up-to-date examples.
- If you need a 3D Breakout sample, use the archived reference under `web/_archive/klassics3d/` and port to your own project. Note that `/web/assets/js/three.min.js` remains available for other use cases.

Operational notes:
- Update any internal or external references to the removed path. Service workers or asset manifests should be purged of Breakout entries.
- Recommended server behavior: Return HTTP 410 (Gone) for `/games/klassics3d/breakout3d/*` for a release or two, then transition to 404.

## [1.0.0] - Feb 2026
- Initial public documentation set and web assets layout.
