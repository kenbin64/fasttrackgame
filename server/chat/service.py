"""
ButterflyFX Chat Service
=========================

Chat service with:
- Secret beta tester page
- Dev collaboration chat (collaborators + superuser only)
- Self-moderation with silent blocking
- Universal blocks (superuser only)

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import secrets
import json
import os

from .models import (
    ChatRoom, ChatRoomType, ChatMessage, ChatMember, 
    MemberRole, Block, BlockType
)

# Import auth to check user tiers
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from server.auth.models import User, UserTier


class ChatError(Exception):
    """Base chat error"""
    pass


class NotInRoomError(ChatError):
    """User is not in the room"""
    pass


class BlockedError(ChatError):
    """Action blocked (but silent to blocked user)"""
    pass


class InsufficientChatPermissionsError(ChatError):
    """User doesn't have permission for this action"""
    pass


class ChatService:
    """
    Chat service with self-moderation and silent blocking.
    
    Features:
    - Beta secret chat room
    - Dev collaboration rooms
    - Direct messages
    - Silent blocking (blocked user doesn't know)
    - Universal blocks (superuser only)
    """
    
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chat")
    ROOMS_FILE = "rooms.json"
    MESSAGES_FILE = "messages.json"
    BLOCKS_FILE = "blocks.json"
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.rooms: Dict[str, ChatRoom] = {}
        self.messages: Dict[str, List[ChatMessage]] = {}  # room_id -> messages
        self.blocks: Dict[str, Block] = {}  # block_id -> Block
        
        # Index for fast block lookups
        self._personal_blocks: Dict[str, Set[str]] = {}  # blocker_id -> set of blocked_ids
        self._universal_blocks: Set[str] = set()  # Set of universally blocked user_ids
        
        os.makedirs(self.DATA_DIR, exist_ok=True)
        
        self._load_data()
        self._ensure_beta_room()
        
        self._initialized = True
    
    def _ensure_beta_room(self):
        """Ensure the secret beta tester room exists"""
        for room in self.rooms.values():
            if room.room_type == ChatRoomType.BETA_SECRET:
                return
        
        # Create secret beta room
        beta_room = ChatRoom.create_beta_secret("🧪 Beta Testers Lounge")
        self.rooms[beta_room.id] = beta_room
        self.messages[beta_room.id] = []
        
        # Add welcome message
        welcome = ChatMessage(
            id=f"msg-{secrets.token_hex(8)}",
            room_id=beta_room.id,
            sender_id="system",
            sender_username="ButterflyFX",
            content="Welcome to the secret Beta Testers Lounge! 🧪\n\nThis is a private space for beta testers to collaborate with Kenneth and each other.",
            is_system=True,
        )
        self.messages[beta_room.id].append(welcome)
        
        self._save_rooms()
        self._save_messages()
        print("✓ Secret Beta Testers Lounge created")
    
    # =========================================================================
    # BLOCKING (Self-Moderation)
    # =========================================================================
    
    def block_user(self, blocker: User, blocked_id: str, reason: str = "") -> Block:
        """
        Block a user (personal block - silent).
        
        - Anyone can block anyone EXCEPT superuser
        - Blocked user doesn't know they're blocked
        - Only affects the blocker's view
        """
        # Cannot block superuser
        if self._is_superuser(blocked_id):
            raise InsufficientChatPermissionsError("Cannot block superuser")
        
        # Cannot block yourself
        if blocker.id == blocked_id:
            raise ChatError("Cannot block yourself")
        
        # Check if already blocked
        if self._is_personally_blocked(blocker.id, blocked_id):
            raise ChatError("User is already blocked")
        
        block = Block(
            id=f"block-{secrets.token_hex(8)}",
            blocker_id=blocker.id,
            blocked_id=blocked_id,
            block_type=BlockType.PERSONAL,
            reason=reason,
            is_universal=False,
        )
        
        self.blocks[block.id] = block
        
        # Update index
        if blocker.id not in self._personal_blocks:
            self._personal_blocks[blocker.id] = set()
        self._personal_blocks[blocker.id].add(blocked_id)
        
        self._save_blocks()
        return block
    
    def unblock_user(self, blocker: User, blocked_id: str) -> bool:
        """Unblock a user (personal block)"""
        if blocker.id not in self._personal_blocks:
            return False
        
        if blocked_id not in self._personal_blocks[blocker.id]:
            return False
        
        # Find and remove the block
        for block_id, block in list(self.blocks.items()):
            if (block.blocker_id == blocker.id and 
                block.blocked_id == blocked_id and 
                block.block_type == BlockType.PERSONAL):
                del self.blocks[block_id]
                break
        
        self._personal_blocks[blocker.id].discard(blocked_id)
        self._save_blocks()
        return True
    
    def universal_block(self, superuser: User, blocked_id: str, reason: str = "") -> Block:
        """
        Universal block (SUPERUSER ONLY).
        
        Blocks user for EVERYONE, not just the superuser.
        """
        if not superuser.is_superuser:
            raise InsufficientChatPermissionsError("Only superuser can create universal blocks")
        
        # Cannot block yourself
        if superuser.id == blocked_id:
            raise ChatError("Cannot block yourself")
        
        block = Block(
            id=f"ublock-{secrets.token_hex(8)}",
            blocker_id=superuser.id,
            blocked_id=blocked_id,
            block_type=BlockType.UNIVERSAL,
            reason=reason,
            is_universal=True,
        )
        
        self.blocks[block.id] = block
        self._universal_blocks.add(blocked_id)
        
        self._save_blocks()
        print(f"⚠️ Universal block applied to user {blocked_id} by {superuser.username}")
        return block
    
    def universal_unblock(self, superuser: User, blocked_id: str) -> bool:
        """Remove universal block (SUPERUSER ONLY)"""
        if not superuser.is_superuser:
            raise InsufficientChatPermissionsError("Only superuser can remove universal blocks")
        
        if blocked_id not in self._universal_blocks:
            return False
        
        # Find and remove the block
        for block_id, block in list(self.blocks.items()):
            if block.blocked_id == blocked_id and block.block_type == BlockType.UNIVERSAL:
                del self.blocks[block_id]
                break
        
        self._universal_blocks.discard(blocked_id)
        self._save_blocks()
        return True
    
    def _is_personally_blocked(self, blocker_id: str, blocked_id: str) -> bool:
        """Check if blocker has personally blocked blocked_id"""
        if blocker_id not in self._personal_blocks:
            return False
        return blocked_id in self._personal_blocks[blocker_id]
    
    def _is_universally_blocked(self, user_id: str) -> bool:
        """Check if user is universally blocked"""
        return user_id in self._universal_blocks
    
    def _is_superuser(self, user_id: str) -> bool:
        """Check if user_id belongs to superuser"""
        # Import here to avoid circular imports
        from server.auth import get_auth_service
        auth = get_auth_service()
        user = auth.users.get(user_id)
        return user and user.is_superuser
    
    def is_blocked_for_viewer(self, viewer_id: str, sender_id: str) -> bool:
        """
        Check if sender is blocked for viewer.
        
        Silent blocking: Sender doesn't know they're blocked.
        """
        # Universal blocks affect everyone
        if self._is_universally_blocked(sender_id):
            return True
        
        # Personal blocks only affect the blocker
        return self._is_personally_blocked(viewer_id, sender_id)
    
    def get_blocked_users(self, user: User) -> List[str]:
        """Get list of users blocked by this user"""
        return list(self._personal_blocks.get(user.id, set()))
    
    def get_universal_blocks(self, superuser: User) -> List[str]:
        """Get universal block list (SUPERUSER ONLY)"""
        if not superuser.is_superuser:
            raise InsufficientChatPermissionsError("Only superuser can view universal blocks")
        return list(self._universal_blocks)
    
    # =========================================================================
    # ROOM MANAGEMENT
    # =========================================================================
    
    def get_beta_room(self) -> ChatRoom:
        """Get the secret beta tester room"""
        for room in self.rooms.values():
            if room.room_type == ChatRoomType.BETA_SECRET:
                return room
        
        # Shouldn't happen but create if missing
        self._ensure_beta_room()
        return self.get_beta_room()
    
    def create_dev_collab_room(self, creator: User, name: str, 
                                collaborator_ids: List[str] = None) -> ChatRoom:
        """
        Create a developer collaboration room.
        
        Only collaborators + superuser can participate.
        """
        if not creator.is_dev:
            raise InsufficientChatPermissionsError("Only developers can create collaboration rooms")
        
        room = ChatRoom.create_dev_collab(
            creator_id=creator.id,
            creator_name=creator.username,
            name=name,
            collaborator_ids=collaborator_ids,
        )
        
        self.rooms[room.id] = room
        self.messages[room.id] = []
        self._save_rooms()
        
        return room
    
    def create_direct_chat(self, user1: User, user2: User) -> ChatRoom:
        """Create or get direct message room between two users"""
        # Check for existing DM room
        for room in self.rooms.values():
            if room.room_type == ChatRoomType.DIRECT:
                if set(room.participant_ids) == {user1.id, user2.id}:
                    return room
        
        # Create new DM room
        room = ChatRoom.create_direct(
            user1_id=user1.id,
            user1_name=user1.username,
            user2_id=user2.id,
            user2_name=user2.username,
        )
        
        self.rooms[room.id] = room
        self.messages[room.id] = []
        self._save_rooms()
        
        return room
    
    def join_beta_room(self, user: User) -> ChatMember:
        """Join the beta room (beta testers and superuser only)"""
        if not user.is_beta:
            raise InsufficientChatPermissionsError("Only beta testers can join the beta room")
        
        beta_room = self.get_beta_room()
        
        if user.id in beta_room.members:
            return beta_room.members[user.id]
        
        role = MemberRole.SUPERUSER if user.is_superuser else MemberRole.MEMBER
        member = beta_room.add_member(user.id, user.username, role)
        
        # System message
        self._add_system_message(beta_room.id, f"👋 {user.username} joined the chat")
        
        self._save_rooms()
        return member
    
    def add_collaborator_to_room(self, room_id: str, owner: User, 
                                  collaborator: User) -> ChatMember:
        """Add a collaborator to a dev room"""
        room = self.rooms.get(room_id)
        if not room:
            raise ChatError(f"Room {room_id} not found")
        
        if room.room_type != ChatRoomType.DEV_COLLAB:
            raise ChatError("Can only add collaborators to dev collaboration rooms")
        
        # Must be room owner or superuser
        if room.created_by != owner.id and not owner.is_superuser:
            raise InsufficientChatPermissionsError("Only room owner can add collaborators")
        
        room.designate_collaborator(collaborator.id)
        member = room.add_member(
            collaborator.id, 
            collaborator.username, 
            MemberRole.COLLABORATOR
        )
        
        self._add_system_message(room_id, f"🤝 {collaborator.username} joined as collaborator")
        
        self._save_rooms()
        return member
    
    def get_rooms_for_user(self, user: User) -> List[ChatRoom]:
        """Get all rooms a user can access"""
        accessible = []
        
        for room in self.rooms.values():
            if room.room_type == ChatRoomType.BETA_SECRET:
                # Beta room: beta testers and superuser
                if user.is_beta:
                    accessible.append(room)
            
            elif room.room_type == ChatRoomType.DEV_COLLAB:
                # Dev collab: owner, collaborators, superuser
                if (room.created_by == user.id or 
                    user.id in room.collaborators or 
                    user.is_superuser):
                    accessible.append(room)
            
            elif room.room_type == ChatRoomType.DIRECT:
                # Direct: only participants
                if user.id in room.participant_ids:
                    accessible.append(room)
        
        return accessible
    
    # =========================================================================
    # MESSAGING
    # =========================================================================
    
    def send_message(self, room_id: str, sender: User, content: str) -> ChatMessage:
        """Send a message to a room"""
        room = self.rooms.get(room_id)
        if not room:
            raise ChatError(f"Room {room_id} not found")
        
        # Check access
        if not self._can_access_room(sender, room):
            raise NotInRoomError("You don't have access to this room")
        
        # Check universal block
        if self._is_universally_blocked(sender.id):
            raise BlockedError("You cannot send messages")
        
        message = ChatMessage(
            id=f"msg-{secrets.token_hex(8)}",
            room_id=room_id,
            sender_id=sender.id,
            sender_username=sender.username,
            content=content,
        )
        
        if room_id not in self.messages:
            self.messages[room_id] = []
        self.messages[room_id].append(message)
        
        self._save_messages()
        return message
    
    def get_messages(self, room_id: str, viewer: User, 
                     limit: int = 50, before: datetime = None) -> List[ChatMessage]:
        """
        Get messages for a room, filtered by viewer's blocks.
        
        Silent blocking: Blocked users' messages are hidden.
        """
        room = self.rooms.get(room_id)
        if not room:
            raise ChatError(f"Room {room_id} not found")
        
        if not self._can_access_room(viewer, room):
            raise NotInRoomError("You don't have access to this room")
        
        messages = self.messages.get(room_id, [])
        
        # Filter by date
        if before:
            messages = [m for m in messages if m.created_at < before]
        
        # Silent blocking: filter out blocked users' messages
        # Blocked user doesn't know their messages are hidden
        filtered = []
        for msg in messages:
            # System messages always shown
            if msg.is_system:
                filtered.append(msg)
                continue
            
            # Skip messages from blocked users (silent)
            if self.is_blocked_for_viewer(viewer.id, msg.sender_id):
                continue
            
            filtered.append(msg)
        
        # Return last N messages
        return filtered[-limit:]
    
    def _add_system_message(self, room_id: str, content: str) -> ChatMessage:
        """Add a system message"""
        msg = ChatMessage(
            id=f"sys-{secrets.token_hex(8)}",
            room_id=room_id,
            sender_id="system",
            sender_username="ButterflyFX",
            content=content,
            is_system=True,
        )
        
        if room_id not in self.messages:
            self.messages[room_id] = []
        self.messages[room_id].append(msg)
        
        self._save_messages()
        return msg
    
    def _can_access_room(self, user: User, room: ChatRoom) -> bool:
        """Check if user can access a room"""
        # Superuser can access everything
        if user.is_superuser:
            return True
        
        if room.room_type == ChatRoomType.BETA_SECRET:
            return user.is_beta
        
        if room.room_type == ChatRoomType.DEV_COLLAB:
            return (room.created_by == user.id or 
                    user.id in room.collaborators)
        
        if room.room_type == ChatRoomType.DIRECT:
            return user.id in room.participant_ids
        
        return False
    
    # =========================================================================
    # DATA PERSISTENCE
    # =========================================================================
    
    def _load_data(self):
        """Load all chat data"""
        self._load_rooms()
        self._load_messages()
        self._load_blocks()
    
    def _load_rooms(self):
        """Load rooms from file"""
        filepath = os.path.join(self.DATA_DIR, self.ROOMS_FILE)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                for room_data in data:
                    room = ChatRoom.from_dict(room_data)
                    self.rooms[room.id] = room
            except Exception as e:
                print(f"Error loading rooms: {e}")
    
    def _save_rooms(self):
        """Save rooms to file"""
        filepath = os.path.join(self.DATA_DIR, self.ROOMS_FILE)
        with open(filepath, 'w') as f:
            json.dump([r.to_dict() for r in self.rooms.values()], f, indent=2)
    
    def _load_messages(self):
        """Load messages from file"""
        filepath = os.path.join(self.DATA_DIR, self.MESSAGES_FILE)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                for room_id, msgs in data.items():
                    self.messages[room_id] = [ChatMessage.from_dict(m) for m in msgs]
            except Exception as e:
                print(f"Error loading messages: {e}")
    
    def _save_messages(self):
        """Save messages to file"""
        filepath = os.path.join(self.DATA_DIR, self.MESSAGES_FILE)
        data = {}
        for room_id, msgs in self.messages.items():
            data[room_id] = [m.to_dict() for m in msgs]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_blocks(self):
        """Load blocks from file"""
        filepath = os.path.join(self.DATA_DIR, self.BLOCKS_FILE)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                for block_data in data:
                    block = Block.from_dict(block_data)
                    self.blocks[block.id] = block
                    
                    # Build indexes
                    if block.is_universal:
                        self._universal_blocks.add(block.blocked_id)
                    else:
                        if block.blocker_id not in self._personal_blocks:
                            self._personal_blocks[block.blocker_id] = set()
                        self._personal_blocks[block.blocker_id].add(block.blocked_id)
            except Exception as e:
                print(f"Error loading blocks: {e}")
    
    def _save_blocks(self):
        """Save blocks to file"""
        filepath = os.path.join(self.DATA_DIR, self.BLOCKS_FILE)
        with open(filepath, 'w') as f:
            json.dump([b.to_dict() for b in self.blocks.values()], f, indent=2)


# Singleton accessor
_chat_service = None

def get_chat_service() -> ChatService:
    """Get the chat service singleton"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
