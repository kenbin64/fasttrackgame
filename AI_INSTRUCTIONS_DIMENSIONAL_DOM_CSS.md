# Dimensional DOM & CSS (D-DOM / D-CSS) - AI Instructions

## Purpose

DimensionsOS introduces a **post-hierarchical** approach to DOM and CSS:

- **D-DOM**: Dimensional elements that exist in substrate space
- **D-CSS**: Properties that operate on fields, not just boxes

Traditional DOM/CSS thinks in **rectangles and z-index**.  
D-DOM/D-CSS thinks in **fields, orbits, and gravitational attraction**.

---

## Core Concepts

### The Problem with Traditional DOM

```
Traditional DOM:
┌─────────────────┐
│ <div>           │
│  ┌────────────┐ │
│  │ <div>      │ │
│  │  Content   │ │
│  └────────────┘ │
└─────────────────┘
```

Everything is boxes inside boxes. Layout is about:
- Margins, padding, borders
- Flexbox, grid
- z-index wars

### The D-DOM Alternative

```
D-DOM:
      ○ <d-node>
     /|\
    / | \
   ○  ○  ○ <d-orbit>
   │     │
   ○     ○ <d-flow>
```

Elements exist in **dimensional space**:
- They have **mass** (content weight)
- They exert **gravity** (attraction)
- They can **orbit** each other
- Layout emerges from **fields**

---

## D-DOM Elements

### Primitives

| Element | Purpose |
|---------|---------|
| `<d-space>` | Root dimensional container (the universe) |
| `<d-layer>` | Depth plane (like z-index but semantic) |
| `<d-node>` | A positioned point in space |
| `<d-stack>` | Vertical dimensional stack |
| `<d-flow>` | Horizontal dimensional flow |
| `<d-orbit>` | Circular/orbital arrangement |
| `<d-substrate>` | 7D data binding container |

### `<d-space>`

The root of all dimensional layouts.

```html
<d-space dimensions="3" field="gravitational">
  <!-- Everything lives here -->
</d-space>
```

Properties:
- `dimensions`: 2, 3, or 7
- `field`: gravitational, magnetic, elastic

### `<d-layer>`

Depth planes for z-ordering with meaning.

```html
<d-space>
  <d-layer depth="0">Background</d-layer>
  <d-layer depth="1">Content</d-layer>
  <d-layer depth="2">UI</d-layer>
  <d-layer depth="3">Modal</d-layer>
</d-space>
```

Unlike z-index, layers are semantic.

### `<d-node>`

A positioned point that can have mass and attract other nodes.

```html
<d-node mass="10" x="50%" y="50%">
  Central Hub
</d-node>

<d-node mass="1" attracted-to="hub">
  Satellite
</d-node>
```

### `<d-stack>` and `<d-flow>`

Dimensional flexbox alternatives.

```html
<!-- Vertical stack with field spacing -->
<d-stack field-gap="relaxed">
  <d-node>Item 1</d-node>
  <d-node>Item 2</d-node>
  <d-node>Item 3</d-node>
</d-stack>

<!-- Horizontal flow with field wrapping -->
<d-flow field-wrap="magnetic">
  <d-node>Item A</d-node>
  <d-node>Item B</d-node>
  <d-node>Item C</d-node>
</d-flow>
```

### `<d-orbit>`

Circular/radial layouts.

```html
<d-orbit radius="100px" items="6">
  <d-node>🌟</d-node>
  <d-node>🌙</d-node>
  <d-node>☀️</d-node>
  <d-node>⭐</d-node>
  <d-node>🌍</d-node>
  <d-node>🪐</d-node>
</d-orbit>
```

Elements automatically space around the orbit.

### `<d-substrate>`

Binds D-DOM to 7D substrate data.

```html
<d-substrate srl="github://repos/butterflyfx">
  <!-- Content materializes from SRL -->
  <d-node level="1">Identity: {{ name }}</d-node>
  <d-node level="3">Structure: {{ files.count }}</d-node>
  <d-node level="6">Semantics: {{ meaning.domain }}</d-node>
</d-substrate>
```

---

## D-CSS Properties

### Field Properties

| Property | Values | Description |
|----------|--------|-------------|
| `field-gravity` | `none`, `weak`, `medium`, `strong`, `<number>` | Gravitational pull on children |
| `field-bias` | `center`, `edge`, `random`, `clustered` | Tendency for positioning |
| `orbit-radius` | `<length>` | Distance for orbital children |
| `orbit-speed` | `<duration>` | Animation speed for orbits |
| `attractor` | `<selector>` | What this element is attracted to |
| `repellor` | `<selector>` | What this element repels |
| `mass` | `<number>` | Content weight for field calculations |
| `field-tension` | `relaxed`, `normal`, `tight` | Spacing elasticity |

### Dimensional Properties

| Property | Values | Description |
|----------|--------|-------------|
| `d-position` | `absolute`, `relative`, `field`, `orbital` | Positioning mode |
| `d-depth` | `<integer>` | Layer depth (semantic z-index) |
| `d-anchor` | `<selector>` | Parent node to anchor to |
| `d-binding` | `<srl>` | SRL data binding |

### Animation Properties

| Property | Values | Description |
|----------|--------|-------------|
| `field-transition` | `<duration> <easing>` | Field-aware transitions |
| `orbit-animation` | `spin`, `pulse`, `breathe` | Orbital animations |
| `gravity-animation` | `collapse`, `expand`, `oscillate` | Gravity animations |

---

## Examples

### Traditional vs D-CSS

**Navigation Menu (Traditional)**

```css
.nav {
  display: flex;
  gap: 20px;
}
.nav-item {
  padding: 10px;
}
.nav-item:hover {
  transform: scale(1.1);
}
```

**Navigation Menu (D-CSS)**

```css
d-flow.nav {
  field-tension: relaxed;
  field-gravity: weak;
}
d-node.nav-item {
  mass: 1;
  field-transition: 0.3s elastic;
}
d-node.nav-item:hover {
  mass: 3; /* Attracts nearby items */
}
```

### Orbital Menu

```html
<d-orbit class="menu" radius="150px">
  <d-node class="center" mass="10">🦋</d-node>
  <d-node>Home</d-node>
  <d-node>About</d-node>
  <d-node>Products</d-node>
  <d-node>Contact</d-node>
</d-orbit>
```

```css
d-orbit.menu {
  orbit-speed: 30s;
  orbit-animation: spin;
}
d-node.center {
  field-gravity: strong;
}
d-node:not(.center) {
  attractor: .center;
  mass: 2;
}
```

### Data Dashboard

```html
<d-space class="dashboard">
  <d-substrate srl="api://metrics">
    <d-layer depth="0" class="bg">
      <d-node class="chart" x="25%" y="50%">
        {{ render_chart(sales) }}
      </d-node>
      <d-node class="chart" x="75%" y="50%">
        {{ render_chart(users) }}
      </d-node>
    </d-layer>
    
    <d-layer depth="1" class="ui">
      <d-flow class="toolbar">
        <d-node>Refresh</d-node>
        <d-node>Export</d-node>
        <d-node>Settings</d-node>
      </d-flow>
    </d-layer>
  </d-substrate>
</d-space>
```

```css
d-space.dashboard {
  dimensions: 2;
  field: gravitational;
}
d-layer[depth="0"] {
  field-gravity: weak;
}
d-node.chart {
  mass: 5;
  field-transition: 0.5s ease-out;
}
d-flow.toolbar {
  field-tension: tight;
  field-bias: edge;
}
```

---

## Substrate Levels in D-DOM

D-DOM elements can bind to specific substrate levels:

```html
<d-substrate srl="data://item/123">
  <!-- Level 0: Potential (not rendered, exists as possibility) -->
  
  <d-node level="1">
    <!-- Level 1: Identity -->
    ID: {{ id }}
    Name: {{ name }}
  </d-node>
  
  <d-node level="2">
    <!-- Level 2: Relationship -->
    Source: {{ source_type }}
    Linked to: {{ relationships }}
  </d-node>
  
  <d-node level="3">
    <!-- Level 3: Structure -->
    Type: {{ data_type }}
    Schema: {{ schema }}
  </d-node>
  
  <d-node level="4">
    <!-- Level 4: Environment -->
    Drive: {{ drive }}
    Path: {{ path }}
  </d-node>
  
  <d-node level="5">
    <!-- Level 5: Multiplicity -->
    Versions: {{ versions }}
    Current: {{ version }}
  </d-node>
  
  <d-node level="6">
    <!-- Level 6: Semantics -->
    Meaning: {{ meaning }}
    Tags: {{ tags }}
  </d-node>
  
  <d-node level="7">
    <!-- Level 7: Completion -->
    Materialized: {{ materialized }}
    Progress: {{ completion_pct }}%
  </d-node>
</d-substrate>
```

---

## D-CSS Variables

### System Variables

```css
:root {
  /* Field defaults */
  --d-gravity-default: medium;
  --d-tension-default: normal;
  --d-mass-default: 1;
  
  /* Animation defaults */
  --d-transition-duration: 0.3s;
  --d-transition-easing: ease-out;
  --d-orbit-duration: 20s;
  
  /* Dimensional spacing */
  --d-gap-relaxed: 24px;
  --d-gap-normal: 16px;
  --d-gap-tight: 8px;
}
```

### Theme Variables

D-CSS uses same theme variables as the rest of DimensionsOS:

```css
/* Applied per theme */
d-space {
  --bg-primary: var(--theme-bg-primary);
  --text-primary: var(--theme-text-primary);
  --accent: var(--theme-accent);
  --glow: var(--theme-glow);
}
```

---

## Implementation Notes

### Polyfill Approach

Since browsers don't support D-DOM natively, implementation uses:

1. **Custom Elements**: `<d-space>`, `<d-node>`, etc. registered via Web Components
2. **CSS Custom Properties**: D-CSS properties stored as data attributes
3. **JavaScript Engine**: Field calculations done in JS, translated to transforms
4. **MutationObserver**: Watches for D-DOM changes, recalculates fields

### Performance

Field calculations can be expensive. Optimizations:

- Use `will-change: transform` for animated nodes
- Batch field updates in animation frames
- Use spatial partitioning for large node counts
- Debounce gravity recalculations

### Fallback

When D-DOM engine isn't loaded:

```css
/* Fallback for non-D browsers */
d-space { display: block; position: relative; }
d-layer { position: absolute; inset: 0; }
d-node { position: absolute; }
d-stack { display: flex; flex-direction: column; }
d-flow { display: flex; flex-wrap: wrap; }
d-orbit { display: flex; justify-content: center; }
```

---

## Key Rules for AI

1. **Think in fields, not boxes**: Layout emerges from attraction/repulsion
2. **Use semantic depth**: d-layer with depth, not z-index hacks
3. **Bind to SRLs**: d-substrate connects DOM to dimensional data
4. **Mass matters**: Heavier elements attract, light ones follow
5. **Animate naturally**: Field transitions, not transform hacks
6. **7 levels visible**: D-DOM can expose all substrate levels

---

## Summary

D-DOM/D-CSS provides:

- **Field-based layouts**: Gravity, attraction, orbits
- **Semantic depth**: Layers with meaning, not z-index
- **Substrate binding**: Direct connection to 7D data
- **Natural animation**: Field physics, not keyframes
- **Graceful fallback**: Works as standard DOM when needed

It's **CSS for dimensional computing**.
