# Universal Dimensional Drive (UDD) - AI Instructions

## Purpose

The Universal Dimensional Drive (UDD) is a **standalone application** that:

- Treats all SRLs (from Universal Connector) as if they were **local hard drive content**
- Provides a **Windows Explorer–like** UI that's actually better than Windows
- Offers multiple views: folder, tile, dimensional, tabular, reports
- Shows **metrics that prove superiority** over standard file systems

UDD is **what Windows Explorer should have been**.

---

## Core Philosophy

### Everything is Local

With UDD, users never think about:
- "Is this file local or remote?"
- "Do I need to download this?"
- "Which app do I use for this data source?"

Instead:
- **All data appears as local files/folders**
- **Drill down through dimensions, not queries**
- **Connect once, data is native forever**

### SRL-First

UDD consumes SRLs from Universal Connector:

```
┌────────────────────┐
│ Universal Connector│ ─── SRLs ───▶ ┌─────────────────┐
└────────────────────┘               │ Universal HDD   │
                                     │  ┌───────────┐  │
                                     │  │ A: Local  │  │
                                     │  │ B: API    │  │
                                     │  │ C: DB     │  │
                                     │  │ D: Cloud  │  │
                                     │  │ F: GitHub │  │
                                     │  │ G: Gmail  │  │
                                     │  └───────────┘  │
                                     └─────────────────┘
```

---

## Layout

### Windows Explorer Pattern

UDD looks familiar but is fundamentally better:

```
┌─────────────────────────────────────────────────────────────────┐
│ 🦋 Universal Dimensional Drive              ─ □ ✕              │
├─────────────────────────────────────────────────────────────────┤
│ [📁 Files][🔲 Tiles][📊 Tabular][🔮 7D][🎯 Native][🔍 Query][📈 Reports] │
│ Path: F:/repos/butterflyfx/                    [🪟][🌌][📺][🌙][◐][🎉]  │
├───────────────┬─────────────────────────────────┬───────────────┤
│ Drives        │                                 │ Preview       │
│               │   [File Grid / Tile Grid /      │               │
│ 💾 A: Local   │    Dimensional View /           │ Select a file │
│ 🌐 B: API     │    Tabular View /               │ to preview    │
│ 🗄️ C: Database│    Reports View]                │               │
│ ☁️ D: Cloud   │                                 │               │
│ 🐙 F: GitHub  │                                 │               │
│ 📧 G: Gmail   │                                 │               │
│               │                                 │               │
│ ─────────────│                                 │               │
│ Connectors   │                                 │               │
│ [🤖 OpenAI]🟢│                                 │               │
│ [💳 Stripe]🟢│                                 │               │
│ [💬 Slack ]🔴│                                 │               │
├───────────────┴─────────────────────────────────┴───────────────┤
│ SRLs: 1,247 │ Materialized: 23 │ Saved: 5 │ Efficiency: 78% │ Bits: 1.2Mb │
└─────────────────────────────────────────────────────────────────┘
```

### Left Pane: Drives & Connectors

- **Hierarchical tree** (like Windows Explorer)
- Built-in drives: A: Local, B: API, C: Database, D: Cloud, E: Cache, Z: Saved
- Dynamic drives: F-Y assigned to connected services
- Connector panel with status dots (green/red/black)

### Right Pane: Main Content

Multiple views (user switches between them):

| View | Purpose |
|------|---------|
| **Files** | Classic Explorer grid with icons |
| **Tiles** | Large cards with metadata |
| **Tabular** | Spreadsheet with dimensional columns |
| **7D Dimensional** | Full substrate breakdown (Levels 0-7) |
| **Native** | Original source format preserved |
| **Query** | Natural language search |
| **Reports** | Analytics dashboard with charts |

### Top Bar: Tools & Themes

- View mode switcher
- Path breadcrumb
- Theme selector (7 themes)

### Bottom Bar: Metrics

**Always visible metrics** showing UDD superiority:
- SRL count
- Materialized items
- Saved items
- Efficiency percentage
- Bit savings
- Compression ratio
- Connection count

---

## View Details

### Files View

Classic Windows Explorer style:
- Icons, names, sizes, modified dates
- Folders appear as folders
- APIs appear as JSON files
- Database tables appear as folders containing records

Supports:
- Rename, delete, move, copy
- Bulk rename with numbering (.001, .002, .003)
- Dedupe (find and remove duplicates)
- Organize by type/date/extension

### Tiles View

Large tiles/cards showing:
- Big icon
- Name
- Type badge
- Source indicator
- Key metrics (row count, message count, etc.)
- Materialization status

Good for touch interfaces and casual browsing.

### Tabular View

Spreadsheet-like grid for:
- Database tables
- CSV files
- Email lists
- API responses (flattened)
- Search results

Features:
- Sort any column
- Filter rows
- Group by values
- Add/remove columns
- Export to CSV
- Quick charts from selected data

### Dimensional View (7D)

Visual representation of substrate dimensions:

```
┌─────────────────────────────────────────────────────────────┐
│ Level 0: Potential                                          │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ⚡ SRLs (unmaterialized): 1,224                         │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ Level 1: Identity                   Level 2: Relationship   │
│ ┌─────────────────────────────┐    ┌─────────────────────┐  │
│ │ 🔹 Items: 47                │    │ 🔗 api: 12          │  │
│ │    → README.md              │    │ 🔗 database: 15     │  │
│ │    → package.json           │    │ 🔗 local: 20        │  │
│ └─────────────────────────────┘    └─────────────────────┘  │
│                                                             │
│ Level 3: Structure                  Level 4: Environment    │
│ ┌─────────────────────────────┐    ┌─────────────────────┐  │
│ │ 📐 Folders: 8               │    │ 🌐 Drive: F:        │  │
│ │ 📐 Files: 39                │    │ 🌐 Path: /repos/    │  │
│ └─────────────────────────────┘    └─────────────────────┘  │
│                                                             │
│ Level 5: Multiplicity               Level 6: Semantics      │
│ ┌─────────────────────────────┐    ┌─────────────────────┐  │
│ │ 🔄 Versions: 1 (live)       │    │ 💡 Domain: code     │  │
│ └─────────────────────────────┘    │ 💡 Traversal: O(1)  │  │
│                                    └─────────────────────┘  │
│                                                             │
│ Level 7: Completion                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ✨ Materialized: 23  │  Pending: 24                     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Native View

Shows data in its **original format**:
- JSON displayed as JSON
- XML as XML
- Images as images
- PDFs rendered

Preserves source fidelity for inspection.

### Query View

Natural language search that **SRL already knows where to look**:

```
┌────────────────────────────────────────────────────┐
│ 🔍 Find all emails from Michaela about coupons     │
└────────────────────────────────────────────────────┘

Searched: 📧 email, 📝 notes, 🏷️ bookmarks
Confidence: 87%

┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ 📧     │  │ 📧     │  │ 📧     │  │ 🏷️     │
│Michaela│  │Discount│  │ Black  │  │Coupon  │
│ Coupon │  │  Code  │  │ Friday │  │ List   │
│   92%  │  │   88%  │  │   85%  │  │   71%  │
└────────┘  └────────┘  └────────┘  └────────┘
```

### Reports View

Analytics dashboard with:
- Total SRLs, materialized, saved
- Storage savings vs naive duplication
- Efficiency by file type
- Bit savings visualization
- Compression ratios
- Charts (line, bar, pie, trend)

---

## Themes

UDD supports **7 themes**:

| Theme | Description |
|-------|-------------|
| **Windows Native** | Familiar Win10/11 look (default) |
| **Cyberpunk** | Neon + animated stars |
| **TV Sci-Fi** | CRT scanlines, green glow |
| **Dark Mode** | Modern dark, subtle accents |
| **High Contrast** | Accessibility, large fonts |
| **Confetti** | Fun/kids, playful colors |

Switch anytime via theme buttons in top bar.

---

## Metrics Philosophy

UDD constantly tracks and displays metrics that **prove its superiority**:

### Efficiency Metrics

| Metric | What It Shows |
|--------|---------------|
| **Efficiency %** | Space saved through dimensional compression |
| **Bit Savings** | Actual bits saved (formatted: Kb, Mb, Gb) |
| **Compression Ratio** | Original:Ingested size |
| **Ingestion Rate** | Files processed per second |

### Query Metrics

| Metric | What It Shows |
|--------|---------------|
| **SRL Hits** | Queries served from SRL without fetch |
| **Materializations** | How many times data was actually fetched |
| **Cache Hits** | Requests served from cache |

### The Point

**Every interaction should remind users** that UDD is better than Windows Explorer:
- "You just saved 1.2 MB by using dimensional storage"
- "This query was O(1) instead of scanning 47,000 files"
- "Your 5 connected services appear as 3 local drives"

---

## File Operations

UDD supports power-user file operations:

### Basic
- Open, rename, delete, move, copy
- Create folder
- Properties/info

### Advanced
- **Find All**: Search by type, extension, content
- **Dedupe**: Find duplicates by content hash
- **Batch Rename**: Add prefix/suffix/numbering
- **Organize**: Sort into folders by type/date/extension
- **Save to Z:**: Persist SRL data locally

---

## Code Patterns

### SRL Materialization

```python
# Good: Lazy materialization through SRL
def read(path: str) -> Any:
    srl = self._srls.get(path)
    if not srl:
        return {"error": "Not found"}
    
    # Materialize on demand - this is when data is fetched
    data = srl.materialize()
    
    # Record metrics
    GLOBAL_METRICS.record_ingestion(srl.substrated)
    
    return data
```

### SubstratedItem (7D Wrapper)

```python
@dataclass
class SubstratedItem:
    """All data passes through this 7D wrapper"""
    
    # Level 1: Identity
    id: str
    name: str
    
    # Level 2: Relationship
    source_type: str
    source_ref: str
    
    # Level 3: Structure
    data_type: str
    schema: Dict
    
    # Level 4: Environment
    drive: str
    path: str
    
    # Level 5: Multiplicity
    version: int
    
    # Level 6: Semantics
    meaning: Dict
    tags: List[str]
    
    # Level 7: Completion
    materialized: bool
    
    # Metrics
    original_size: int
    ingested_size: int
    efficiency_pct: float
```

### Virtual Drives

```python
# Drives are just views into SRLs
self._drives = {
    'A': VirtualDrive('A', 'Local', '💾', 'local'),
    'B': VirtualDrive('B', 'API', '🌐', 'api'),
    'C': VirtualDrive('C', 'Database', '🗄️', 'database'),
    'D': VirtualDrive('D', 'Cloud', '☁️', 'cloud'),
    'E': VirtualDrive('E', 'Cache', '⚡', 'cache'),
    'Z': VirtualDrive('Z', 'Saved', '💎', 'saved'),
    # F-Y assigned dynamically to connected services
}
```

---

## Key Rules for AI

1. **SRL-first**: All data access goes through SRLs
2. **Metrics everywhere**: Always show efficiency gains
3. **Multiple views**: Same data, many presentations
4. **Windows familiar**: Users should feel at home
5. **But better**: Show them what they're gaining
6. **Lazy materialization**: Don't fetch until needed
7. **7D structure**: All data has dimensional coordinates

---

## Summary

The Universal Dimensional Drive is:

- **Windows Explorer, but universal** - All sources, one interface
- **SRL-powered** - Lazy materialization, efficient access
- **Metrics-driven** - Always proving its superiority
- **Multi-view** - Files, tiles, tables, dimensions, reports
- **Themed** - 7 visual themes for every preference
- **Power-user ready** - Find, dedupe, batch rename, organize

UDD is **what Windows should have been**.
