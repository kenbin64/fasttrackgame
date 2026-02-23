# ButterflyFX Dimensional Architecture: Lobby, Guilds, and Social Features

This document outlines the architectural design for the Fast Track game's lobby, guild system, player matching, and communication features, all implemented within the ButterflyFX dimensional computing paradigm.

## 1. Core Principles

- **Substrates as Data Sources:** All persistent data will be modeled as Substrates. These are not traditional databases but dimensional data structures that can be invoked and manipulated mathematically.
- **Manifolds as Interfaces:** All user-facing components (UIs) will be Manifolds. These are presentation layers that render the state of one or more Substrates.
- **Helix Kernel Integration:** The Helix Kernel will manage state transitions, rule enforcement, and the invocation of Substrates and Manifolds.

## 2. Substrate Definitions

### 2.1. `PlayerProfile_Substrate` (Existing, to be extended)

This substrate will be extended to include:
- `blocked_players`: An array of `player_ids` that the user has silently blocked.
- `guild_membership`: An object mapping `guild_id` to the player's role (e.g., 'member', 'admin').
- `online_status`: (e.g., 'online', 'offline', 'in-game').

### 2.2. `Guild_Substrate` (New)

This will be a new substrate to manage all guild-related information.

- **Structure:** A collection of guild objects.
- **Guild Object Schema:**
  ```json
  {
    "guild_id": "unique_guild_identifier",
    "guild_name": "The Guild's Unique Name",
    "creator_id": "player_id_of_creator",
    "members": [
      { "player_id": "player_id", "joined_at": "timestamp" }
    ],
    "join_requests": [
      { "player_id": "requesting_player_id", "requested_at": "timestamp" }
    ],
    "blocked_from_guild": ["player_id"]
  }
  ```

### 2.3. `Lobby_Substrate` (New)

This substrate will manage the state of the game lobby and player matching.

- **Structure:** A dynamic list of open game sessions and available players.
- **Schema:**
  ```json
  {
    "available_players": [
        {
            "player_id": "player_id",
            "username": "username",
            "medallion_level": "level"
        }
    ],
    "open_games": [
        {
            "game_id": "unique_game_id",
            "host_id": "player_id",
            "game_mode": "solo_ai, hybrid, all_human",
            "player_slots": [
                {"player_id": "player_id", "status": "joined"},
                {"player_id": null, "status": "open"}
            ],
            "filters": {
                "min_medallion": "level",
                "max_medallion": "level"
            }
        }
    ]
  }
  ```

### 2.4. `Chat_Substrate` (New)

This substrate will store guild chat messages.

- **Structure:** A collection of messages, indexed by `guild_id`.
- **Message Schema:**
  ```json
  {
    "message_id": "unique_message_id",
    "guild_id": "guild_id",
    "player_id": "sender_player_id",
    "username": "sender_username",
    "timestamp": "timestamp",
    "content": "The message text."
  }
  ```

### 2.5. `Superuser_Substrate` (New)

A restricted substrate for superuser actions.

- **Structure:** Manages global blocks and appeals.
- **Schema:**
  ```json
  {
      "global_blocks": [
          {
              "player_id": "player_id",
              "blocked_by": "superuser_id",
              "reason": "Reason for block",
              "expires_at": "timestamp_or_permanent"
          }
      ],
      "appeals": [
          {
              "appeal_id": "unique_id",
              "player_id": "blocked_player_id",
              "appeal_text": "Text of the appeal",
              "status": "pending_review"
          }
      ]
  }
  ```

### 2.6. `Tournament_Substrate` (New)

This substrate will manage all tournament-related information.

- **Structure:** A collection of tournament objects.
- **Tournament Object Schema:**
  ```json
  {
    "tournament_id": "unique_tournament_identifier",
    "tournament_name": "The Tournament's Name",
    "status": "pending_challenge | active | completed",
    "style": "guild_vs_guild | free_for_all",
    "participating_guilds": [
        { "guild_id": "guild_id", "status": "challenged | accepted | declined" }
    ],
    "participating_players": [
        { "player_id": "player_id", "guild_id": "guild_id" }
    ],
    "bracket": {
        "type": "single_elimination | round_robin",
        "rounds": [
            {
                "round_number": 1,
                "matches": [
                    { "match_id": "unique_match_id", "players": ["player_id_1", "player_id_2"], "winner": "player_id" }
                ]
            }
        ]
    },
    "start_time": "timestamp",
    "end_time": "timestamp",
    "winner": "guild_id or player_id"
  }
  ```

## 3. Manifold Definitions

### 3.1. `Lobby_Manifold`

- **Purpose:** The main interface for players after signing in.
- **Views:**
    - **Player Search:** Renders `Lobby_Substrate.available_players` with filtering controls.
    - **Game Browser:** Renders `Lobby_Substrate.open_games`. Allows creating new games.
    - **Guild Directory:** A view to search for and request to join guilds, rendered from `Guild_Substrate`.
    - **Tournament Browser:** Renders a list of active and upcoming tournaments from `Tournament_Substrate`.

### 3.2. `Guild_Manifold`

- **Purpose:** The main interface for interacting with a specific guild.
- **Views:**
    - **Member List:** Renders members from `Guild_Substrate`.
    - **Admin Panel (for creators):** Renders join requests and member list with "kick" or "block" actions. Invokes changes in the `Guild_Substrate`.
    - **Guild Chat:** Renders messages from `Chat_Substrate` for the current guild. It will filter out messages from players listed in the current user's `PlayerProfile_Substrate.blocked_players`.
    - **Tournament Challenge:** A view for guild admins to challenge other guilds to a tournament, which will create a new entry in the `Tournament_Substrate`.

### 3.3. `Superuser_Manifold`

- **Purpose:** An admin interface for the superuser.
- **Views:**
    - **Global Blocks:** Interface to manage `Superuser_Substrate.global_blocks`.
    - **Appeals:** Interface to review and act on `Superuser_Substrate.appeals`.

### 3.4. `Tournament_Manifold`

- **Purpose:** The main interface for viewing and interacting with tournaments.
- **Views:**
    - **Tournament Dashboard:** A detailed view of a specific tournament, showing the bracket, participants, schedule, and results.
    - **Match View:** A dedicated view for an active tournament match.

## 4. Workflow Example: Creating a Guild

1.  **Player Action:** A player clicks "Create Guild" in the `Lobby_Manifold`.
2.  **Manifold:** The manifold presents a form for the guild name.
3.  **Kernel Invocation:** On submission, the manifold invokes a `create_guild` function in the Helix Kernel, passing the proposed name and creator's `player_id`.
4.  **Kernel Logic:**
    - The kernel queries the `Guild_Substrate` to check if a guild with that name already exists.
    - If the name is taken, it returns an error state to the manifold, which displays the "name in use" message.
    - If the name is available, the kernel creates a new guild object and adds it to the `Guild_Substrate`. It also updates the creator's `PlayerProfile_Substrate` to add their new admin role for the guild.
5.  **State Change:** The update to the `Guild_Substrate` and `PlayerProfile_Substrate` propagates, and any manifolds observing this data (like the player's own profile view) will update automatically.
