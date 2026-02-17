# Universal Connector (UC) - AI Instructions

## Purpose

The Universal Connector is a **separate, standalone application + background service**.
It is the **source of all connections** and **SRLs** for the ButterflyFx / DimensionOS ecosystem.
It is **not app-specific**; multiple apps (like Universal HDD) consume it.

---

## Core Responsibilities

### Connection Management

UC manages connections to ALL external systems:

| Category | Services |
|----------|----------|
| **Local** | Drives, network shares, mounted volumes |
| **Cloud Storage** | Google Drive, OneDrive, Dropbox, S3, Backblaze |
| **Email** | Gmail, Outlook, Yahoo, IMAP, Exchange |
| **Databases** | PostgreSQL, MySQL, MongoDB, Redis, Supabase, Firebase |
| **APIs** | REST, GraphQL, custom endpoints |
| **Social** | Twitter/X, Facebook, LinkedIn |
| **E-Commerce** | Amazon, eBay, Shopify, Stripe |
| **Developer** | GitHub, GitLab, Vercel, Docker |
| **Analytics** | Google Analytics, Mixpanel, Amplitude |
| **Communication** | Slack, Discord, Twilio |
| **AI/ML** | OpenAI, Anthropic, Hugging Face, Replicate |
| **Feeds** | RSS, Atom, webhooks |

### SRL Generation

UC generates SRLs (Substrate Reference Links) for:

- Connections themselves
- Folders and directories
- Database tables and collections
- Individual rows/documents
- Email mailboxes and messages
- API endpoints and responses
- Cloud documents
- Feed items

### Credential Management

- Store credentials **once**, securely
- Never expose raw credentials to consuming apps
- Auto-refresh tokens when needed
- Support OAuth, API keys, username/password, certificates

---

## Architecture

### Background Daemon

UC runs as a **persistent background service**:

```
┌─────────────────────────────────────────────────────────┐
│                  Universal Connector                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Credential  │  │ Connection  │  │    SRL      │      │
│  │   Vault     │  │   Manager   │  │   Registry  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
│                          │                               │
│                    ┌─────▼─────┐                        │
│                    │   Local   │                        │
│                    │    API    │                        │
│                    └─────┬─────┘                        │
└──────────────────────────┼──────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────────┐
        │                  │                      │
   ┌────▼────┐       ┌─────▼─────┐         ┌─────▼─────┐
   │ UDD App │       │ Other App │         │ D-DOM UI  │
   └─────────┘       └───────────┘         └───────────┘
```

### Daemon Responsibilities

1. **Monitor connections** - Track health and status
2. **Refresh tokens** - Keep OAuth/API tokens valid
3. **Update SRLs** - Sync metadata when sources change
4. **Cache metadata** - Store lightweight indices locally
5. **Notify apps** - Push updates to consuming applications

---

## UI Design

### Main Screen

Grid of **logo buttons**, each representing a connector:

```
┌────────────────────────────────────────────────────┐
│  Universal Connector                    ⚙️  ─  □  ✕ │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐ │
│  │🐙 🟢 │  │📧 🟢 │  │🐘 🔴 │  │☁️ 🟡 │  │🤖 🟢 │ │
│  │GitHub│  │Gmail │  │Postgr│  │OneDr│  │OpenAI│ │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘ │
│                                                    │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐ │
│  │💳 🟢 │  │💬 🔴 │  │📁 🟢 │  │🍃 ⚫ │  │⚡ 🟢 │ │
│  │Stripe│  │Slack │  │Dropbx│  │Mongo │  │Supabs│ │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘ │
│                                                    │
│  [ + Add Custom Connector ]                        │
│                                                    │
├────────────────────────────────────────────────────┤
│  Connected: 7  │  Disconnected: 2  │  Syncing: 1  │
└────────────────────────────────────────────────────┘
```

### Status Dots

| Dot | Color | Meaning |
|-----|-------|---------|
| 🟢 | Green | Connected and ready |
| 🔴 | Red | Disconnected |
| ⚫ | Black | Unavailable / not configured |
| 🟡 | Yellow | Connecting / syncing |

### Button Behavior

- **Click on unconfigured** → Launch connection wizard
- **Click on configured but disconnected** → Offer to reconnect
- **Click on connected** → Show details, usage, SRL count

---

## Connection Wizards

### Design Principle

Wizards are **preconfigured per service**:
- Only ask for what the user **must** supply
- Pre-fill defaults where possible
- Validate credentials before accepting
- Ingest as SRL substrates on success

### Example: GitHub Wizard

```
┌────────────────────────────────────────┐
│  Connect to GitHub              🐙     │
├────────────────────────────────────────┤
│                                        │
│  Personal Access Token:                │
│  ┌──────────────────────────────────┐  │
│  │ ghp_xxxxxxxxxxxxxxxxxxxx         │  │
│  └──────────────────────────────────┘  │
│                                        │
│  ☐ Include private repositories        │
│  ☑ Include organizations               │
│                                        │
│  What will be ingested:                │
│  • Repositories                        │
│  • Issues                              │
│  • Pull Requests                       │
│  • Gists                               │
│  • Organizations                       │
│                                        │
│  [ Test Connection ]    [ Connect ]    │
│                                        │
└────────────────────────────────────────┘
```

---

## API for Consuming Apps

UC exposes a **local API** that apps use to access connections:

### Endpoints

```
GET  /api/connections        → List all connections with status
GET  /api/connections/:id    → Get specific connection details
GET  /api/srls               → List all SRLs
GET  /api/srls/:path         → Get specific SRL
POST /api/connect            → Create new connection
POST /api/disconnect/:id     → Disconnect a service
GET  /api/materialize/:path  → Fetch actual data through SRL
GET  /api/status             → Overall health and metrics
```

### Example Response

```json
{
  "connections": [
    {
      "id": "github_main",
      "provider": "github",
      "name": "My GitHub",
      "status": "connected",
      "status_dot": "🟢",
      "srl_count": 247,
      "last_sync": "2026-02-16T08:00:00Z",
      "drive_letter": "F"
    }
  ]
}
```

---

## Key Rules for AI

1. **Apps never connect directly** - All external access goes through UC
2. **SRLs are the interface** - Apps work with SRLs, not raw connections
3. **Credentials stay in UC** - Never expose secrets to consuming apps
4. **Status is always visible** - Green/red/black dots everywhere
5. **Wizards are pre-built** - Each service has a curated connection flow
6. **Background sync** - UC keeps everything fresh automatically

---

## Code Style

When generating UC code:

```python
# Good: Modular, SRL-first
class Connector:
    """Abstract connector interface"""
    def connect(self, credentials: Dict) -> bool: ...
    def disconnect(self) -> bool: ...
    def list_srls(self) -> List[SRL]: ...
    def materialize(self, srl: SRL) -> Any: ...
    def status(self) -> ConnectorStatus: ...

# Good: Status tracking
class ConnectorStatus(Enum):
    CONNECTED = 'connected'      # 🟢
    DISCONNECTED = 'disconnected'  # 🔴
    UNAVAILABLE = 'unavailable'   # ⚫
    PENDING = 'pending'           # 🟡
```

```python
# Bad: Direct connection without SRL
def get_github_repos():
    # ❌ Don't do this - bypasses UC
    return requests.get("https://api.github.com/repos")

# Good: Through UC/SRL
def get_github_repos():
    # ✅ Always through UC
    return uc.materialize("F:/repos/")
```

---

## Summary

The Universal Connector is:

- **The single source of truth** for all external connections
- **A background service** that keeps everything synced
- **An SRL generator** that makes all data feel local
- **A credential vault** that keeps secrets safe
- **A status dashboard** that makes connection health visible

Apps built on ButterflyFx / DimensionOS never talk to external systems directly.
They talk to UC, which talks to everything else.
