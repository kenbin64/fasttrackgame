"""
ButterflyFX Chat Models
========================

Chat system with:
- Room types: BETA_SECRET, DEV_COLLAB, DIRECT
- Self-moderation with silent blocking
- Universal blocks (superuser only)
- Collaboration designation

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import IntEnum
from datetime import datetime
import secrets


class ChatRoomType(IntEnum):
    """Types of chat rooms"""
    DIRECT = 0           # 1-on-1 private chat
    DEV_COLLAB = 1       # Dev collaboration (collaborators + superuser only)
    BETA_SECRET = 2      # Secret beta tester page chat


class MemberRole(IntEnum):
    """Roles within a chat room"""
    MEMBER = 0           # Regular participant
    MODERATOR = 1        # Can kick/mute (not block)
    OWNER = 2            # Room creator, full control
    COLLABORATOR = 3     # Designated collaborator
    SUPERUSER = 4        # Kenneth - supreme control


class BlockType(IntEnum):
    """Types of blocks"""
    PERSONAL = 0         # User blocks another user (only affects blocker)
    UNIVERSAL = 1        # Superuser blocks globally (affects everyone)


@dataclass
class Block:
    """
    Block record for silent blocking.
    
    - Personal blocks: Only affects the blocker's view
    - Universal blocks: Superuser-only, affects everyone
    - Silent: Blocked user doesn't know they're blocked
    """
    id: str
    blocker_id: str          # Who created the block
    blocked_id: str          # Who is blocked
    block_type: BlockType
    
    created_at: datetime = field(default_factory=datetime.now)
    reason: str = ""         # Optional reason (private)
    
    # For universal blocks
    is_universal: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "blocker_id": self.blocker_id,
            "blocked_id": self.blocked_id,
            "block_type": self.block_type.value,
            "created_at": self.created_at.isoformat(),
            "reason": self.reason,
            "is_universal": self.is_universal,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        return cls(
            id=data["id"],
            blocker_id=data["blocker_id"],
            blocked_id=data["blocked_id"],
            block_type=BlockType(data["block_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            reason=data.get("reason", ""),
            is_universal=data.get("is_universal", False),
        )


@dataclass
class ChatMember:
    """Member of a chat room"""
    user_id: str
    username: str
    role: MemberRole
    
    joined_at: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None
    is_online: bool = False
    
    # Mute settings
    is_muted: bool = False
    muted_until: Optional[datetime] = None
    
    # Notification settings
    notifications_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "is_online": self.is_online,
            "is_muted": self.is_muted,
            "muted_until": self.muted_until.isoformat() if self.muted_until else None,
            "notifications_enabled": self.notifications_enabled,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMember':
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            role=MemberRole(data["role"]),
            joined_at=datetime.fromisoformat(data["joined_at"]),
            last_seen=datetime.fromisoformat(data["last_seen"]) if data.get("last_seen") else None,
            is_online=data.get("is_online", False),
            is_muted=data.get("is_muted", False),
            muted_until=datetime.fromisoformat(data["muted_until"]) if data.get("muted_until") else None,
            notifications_enabled=data.get("notifications_enabled", True),
        )


@dataclass
class ChatMessage:
    """A chat message"""
    id: str
    room_id: str
    sender_id: str
    sender_username: str
    
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    
    # Edit tracking
    edited_at: Optional[datetime] = None
    is_edited: bool = False
    
    # Deletion (soft delete)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: str = ""
    
    # Message type
    is_system: bool = False       # System messages (join/leave)
    
    # Attachments/metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def edit(self, new_content: str) -> None:
        """Edit message content"""
        self.content = new_content
        self.edited_at = datetime.now()
        self.is_edited = True
    
    def delete(self, by_user_id: str) -> None:
        """Soft delete message"""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.deleted_by = by_user_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "room_id": self.room_id,
            "sender_id": self.sender_id,
            "sender_username": self.sender_username,
            "content": self.content if not self.is_deleted else "[deleted]",
            "created_at": self.created_at.isoformat(),
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "is_edited": self.is_edited,
            "is_deleted": self.is_deleted,
            "is_system": self.is_system,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        return cls(
            id=data["id"],
            room_id=data["room_id"],
            sender_id=data["sender_id"],
            sender_username=data["sender_username"],
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"]),
            edited_at=datetime.fromisoformat(data["edited_at"]) if data.get("edited_at") else None,
            is_edited=data.get("is_edited", False),
            is_deleted=data.get("is_deleted", False),
            deleted_at=datetime.fromisoformat(data["deleted_at"]) if data.get("deleted_at") else None,
            deleted_by=data.get("deleted_by", ""),
            is_system=data.get("is_system", False),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ChatRoom:
    """
    Chat room for collaboration.
    
    Types:
    - DIRECT: 1-on-1 private chat between two users
    - DEV_COLLAB: Developer collaboration room (collaborators + superuser only)
    - BETA_SECRET: Secret beta tester chat room
    """
    id: str
    name: str
    room_type: ChatRoomType
    
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""         # User ID of creator
    
    # Members
    members: Dict[str, ChatMember] = field(default_factory=dict)
    
    # For DIRECT rooms, track the two participants
    participant_ids: List[str] = field(default_factory=list)
    
    # Collaborator designation
    collaborators: Set[str] = field(default_factory=set)
    
    # Room settings
    is_active: bool = True
    is_archived: bool = False
    
    # Access control
    is_secret: bool = False      # Only visible to members
    invite_only: bool = True     # Must be invited to join
    
    # Metadata
    description: str = ""
    topic: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_direct(cls, user1_id: str, user1_name: str,
                      user2_id: str, user2_name: str) -> 'ChatRoom':
        """Create a direct message room between two users"""
        room = cls(
            id=f"dm-{secrets.token_hex(8)}",
            name=f"DM: {user1_name} & {user2_name}",
            room_type=ChatRoomType.DIRECT,
            participant_ids=[user1_id, user2_id],
            is_secret=True,
            invite_only=True,
        )
        
        # Add both as members
        room.members[user1_id] = ChatMember(
            user_id=user1_id,
            username=user1_name,
            role=MemberRole.MEMBER,
        )
        room.members[user2_id] = ChatMember(
            user_id=user2_id,
            username=user2_name,
            role=MemberRole.MEMBER,
        )
        
        return room
    
    @classmethod
    def create_dev_collab(cls, creator_id: str, creator_name: str,
                          name: str, collaborator_ids: List[str] = None) -> 'ChatRoom':
        """
        Create a developer collaboration room.
        
        Only collaborators + superuser can participate.
        No general chat - strictly for collaboration.
        """
        room = cls(
            id=f"dev-collab-{secrets.token_hex(8)}",
            name=name,
            room_type=ChatRoomType.DEV_COLLAB,
            created_by=creator_id,
            is_secret=True,
            invite_only=True,
            description="Developer collaboration room - collaborators only",
        )
        
        # Creator is owner
        room.members[creator_id] = ChatMember(
            user_id=creator_id,
            username=creator_name,
            role=MemberRole.OWNER,
        )
        
        # Add collaborators
        if collaborator_ids:
            room.collaborators = set(collaborator_ids)
        
        return room
    
    @classmethod
    def create_beta_secret(cls, name: str = "Beta Testers Lounge") -> 'ChatRoom':
        """
        Create the secret beta tester chat room.
        
        Only beta testers and superuser can access.
        """
        return cls(
            id=f"beta-secret-{secrets.token_hex(8)}",
            name=name,
            room_type=ChatRoomType.BETA_SECRET,
            created_by="superuser",
            is_secret=True,
            invite_only=False,  # All beta testers can join
            description="Secret beta tester chat - collaboration with Kenneth",
        )
    
    def add_member(self, user_id: str, username: str, 
                   role: MemberRole = MemberRole.MEMBER) -> ChatMember:
        """Add a member to the room"""
        member = ChatMember(
            user_id=user_id,
            username=username,
            role=role,
        )
        self.members[user_id] = member
        return member
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the room"""
        if user_id in self.members:
            del self.members[user_id]
            return True
        return False
    
    def designate_collaborator(self, user_id: str) -> None:
        """Designate a user as collaborator"""
        self.collaborators.add(user_id)
        if user_id in self.members:
            self.members[user_id].role = MemberRole.COLLABORATOR
    
    def remove_collaborator(self, user_id: str) -> None:
        """Remove collaborator designation"""
        self.collaborators.discard(user_id)
        if user_id in self.members:
            self.members[user_id].role = MemberRole.MEMBER
    
    def is_member(self, user_id: str) -> bool:
        """Check if user is a member"""
        return user_id in self.members
    
    def is_collaborator(self, user_id: str) -> bool:
        """Check if user is a designated collaborator"""
        return user_id in self.collaborators
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "room_type": self.room_type.value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "members": {uid: m.to_dict() for uid, m in self.members.items()},
            "participant_ids": self.participant_ids,
            "collaborators": list(self.collaborators),
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "is_secret": self.is_secret,
            "invite_only": self.invite_only,
            "description": self.description,
            "topic": self.topic,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatRoom':
        room = cls(
            id=data["id"],
            name=data["name"],
            room_type=ChatRoomType(data["room_type"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data.get("created_by", ""),
            participant_ids=data.get("participant_ids", []),
            collaborators=set(data.get("collaborators", [])),
            is_active=data.get("is_active", True),
            is_archived=data.get("is_archived", False),
            is_secret=data.get("is_secret", False),
            invite_only=data.get("invite_only", True),
            description=data.get("description", ""),
            topic=data.get("topic", ""),
            metadata=data.get("metadata", {}),
        )
        
        # Load members
        for uid, mdata in data.get("members", {}).items():
            room.members[uid] = ChatMember.from_dict(mdata)
        
        return room
