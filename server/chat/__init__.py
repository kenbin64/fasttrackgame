"""
ButterflyFX Chat System
========================

Private chat system for Beta testers and Developers.

Features:
- Beta Tester secret page with collaboration chat
- Dev chat (collaborators + superuser only, no general chat)
- User can designate who to chat with
- Self-moderation: anyone can block anyone (except superuser)
- Silent blocking (blocked user doesn't know they're blocked)
- Only superuser can do universal blocks

Copyright (c) 2024-2026 Kenneth Bingham
All Rights Reserved
"""

from .models import (
    ChatRoom,
    ChatRoomType,
    ChatMessage,
    ChatMember,
    MemberRole,
    Block,
    BlockType,
)

from .service import (
    ChatService,
    get_chat_service,
    ChatError,
    NotInRoomError,
    BlockedError,
    InsufficientChatPermissionsError,
)

__all__ = [
    # Models
    'ChatRoom',
    'ChatRoomType',
    'ChatMessage',
    'ChatMember',
    'MemberRole',
    'Block',
    'BlockType',
    
    # Service
    'ChatService',
    'get_chat_service',
    'ChatError',
    'NotInRoomError',
    'BlockedError',
    'InsufficientChatPermissionsError',
]
