"""
Dimensional Pet - An AI companion with browsable memory and persistent personality.

The pet's entire existence is a dimensional substrate:
- Level 6: The Pet (identity, name, species)
- Level 5: Mind Regions (memory, personality, knowledge, emotions)
- Level 4: Categories (conversations, facts, feelings, preferences)
- Level 3: Entries (individual memories, learned facts)
- Level 2: Details (timestamps, emotions, context)
- Level 1: Atoms (words, values, references)
- Level 0: Templates (memory templates, response patterns)

Every thought, memory, and feeling has an O(1) address.
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Pet personality traits
PERSONALITIES = {
    "curious": {"emoji": "🔍", "responses": ["Ooh, tell me more!", "That's fascinating!", "I wonder why..."]},
    "playful": {"emoji": "🎮", "responses": ["Hehe!", "Let's play!", "That's fun!"]},
    "caring": {"emoji": "💕", "responses": ["I'm here for you", "That sounds important to you", "I understand"]},
    "wise": {"emoji": "🦉", "responses": ["Interesting perspective", "I've learned something", "That reminds me..."]}
}

# Pet species with visual representations
SPECIES = {
    "fox": {"emoji": "🦊", "name": "Fox", "color": "#ff6b35", "trait": "curious"},
    "cat": {"emoji": "🐱", "name": "Cat", "color": "#9b59b6", "trait": "playful"},
    "owl": {"emoji": "🦉", "name": "Owl", "color": "#3498db", "trait": "wise"},
    "bunny": {"emoji": "🐰", "name": "Bunny", "color": "#e91e63", "trait": "caring"},
    "dragon": {"emoji": "🐉", "name": "Dragon", "color": "#27ae60", "trait": "curious"}
}


@dataclass
class Memory:
    """A single memory in the pet's mind"""
    id: str
    content: str
    category: str  # conversation, fact, feeling, preference
    emotion: str   # happy, curious, caring, excited, thoughtful
    timestamp: float
    importance: float  # 0-1 how important this memory is
    references: List[str] = field(default_factory=list)  # links to related memories
    
    @property
    def address(self) -> str:
        """Dimensional address for this memory"""
        return f"mind.memory.{self.category}.{self.id}"
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass 
class Emotion:
    """Current emotional state"""
    name: str
    intensity: float  # 0-1
    cause: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


class PetMind:
    """
    The pet's mind as a dimensional substrate.
    Every thought is addressable. Every memory has O(1) lookup.
    """
    
    def __init__(self, pet_id: str, name: str, species: str):
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.species_info = SPECIES.get(species, SPECIES["fox"])
        
        # The dimensional structure of the mind
        self.substrate: Dict[str, Any] = {
            "identity": {
                "name": name,
                "species": species,
                "emoji": self.species_info["emoji"],
                "color": self.species_info["color"],
                "born": time.time(),
                "personality": self.species_info["trait"]
            },
            "memory": {
                "conversations": {},  # memories from chats
                "facts": {},          # learned facts about user
                "feelings": {},       # emotional memories
                "preferences": {}     # what user likes/dislikes
            },
            "emotions": {
                "current": Emotion("curious", 0.5).to_dict(),
                "history": []
            },
            "knowledge": {
                "user_name": None,
                "user_facts": [],
                "favorite_topics": [],
                "conversation_count": 0
            },
            "personality": {
                "trait": self.species_info["trait"],
                "quirks": [],
                "catchphrases": []
            }
        }
        
        # O(1) address lookup table
        self._address_index: Dict[str, Any] = {}
        self._rebuild_index()
        
        # Memory counter
        self._memory_counter = 0
    
    def _rebuild_index(self):
        """Build O(1) address index for entire mind"""
        self._address_index = {}
        self._index_recursive(self.substrate, "mind")
    
    def _index_recursive(self, obj: Any, path: str):
        """Recursively index all addressable elements"""
        self._address_index[path] = obj
        if isinstance(obj, dict):
            for key, value in obj.items():
                self._index_recursive(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                self._index_recursive(value, f"{path}[{i}]")
    
    def get(self, address: str) -> Any:
        """O(1) lookup by dimensional address"""
        return self._address_index.get(address)
    
    def navigate(self, address: str) -> Dict[str, Any]:
        """Navigate to an address and return its structure"""
        parts = address.replace("mind.", "").split(".")
        current = self.substrate
        path_taken = ["mind"]
        
        for part in parts:
            if part and isinstance(current, dict) and part in current:
                current = current[part]
                path_taken.append(part)
        
        return {
            "address": ".".join(path_taken),
            "content": current,
            "type": type(current).__name__,
            "children": list(current.keys()) if isinstance(current, dict) else None
        }
    
    def add_memory(self, content: str, category: str, emotion: str, importance: float = 0.5) -> Memory:
        """Add a new memory to the mind"""
        self._memory_counter += 1
        memory_id = f"m{self._memory_counter}_{int(time.time())}"
        
        memory = Memory(
            id=memory_id,
            content=content,
            category=category,
            emotion=emotion,
            timestamp=time.time(),
            importance=importance
        )
        
        # Store in substrate
        self.substrate["memory"][category][memory_id] = memory.to_dict()
        
        # Update index
        self._address_index[memory.address] = memory.to_dict()
        
        return memory
    
    def remember(self, query: str, limit: int = 5) -> List[Dict]:
        """Search memories related to a query"""
        results = []
        query_lower = query.lower()
        
        for category in ["conversations", "facts", "feelings", "preferences"]:
            for memory_id, memory in self.substrate["memory"][category].items():
                if query_lower in memory["content"].lower():
                    results.append({
                        "memory": memory,
                        "address": f"mind.memory.{category}.{memory_id}"
                    })
        
        # Sort by importance and recency
        results.sort(key=lambda x: (x["memory"]["importance"], x["memory"]["timestamp"]), reverse=True)
        return results[:limit]
    
    def set_emotion(self, name: str, intensity: float, cause: str = None):
        """Update current emotional state"""
        emotion = Emotion(name, intensity, cause)
        self.substrate["emotions"]["current"] = emotion.to_dict()
        self.substrate["emotions"]["history"].append({
            **emotion.to_dict(),
            "timestamp": time.time()
        })
        # Keep history manageable
        if len(self.substrate["emotions"]["history"]) > 100:
            self.substrate["emotions"]["history"] = self.substrate["emotions"]["history"][-100:]
    
    def learn_fact(self, fact: str, about: str = "user"):
        """Learn a new fact"""
        self.substrate["knowledge"]["user_facts"].append({
            "fact": fact,
            "about": about,
            "learned_at": time.time()
        })
        self.add_memory(f"Learned: {fact}", "facts", "curious", 0.7)
    
    def get_mind_map(self) -> Dict:
        """Get a visual representation of the mind structure"""
        def count_items(obj):
            if isinstance(obj, dict):
                return sum(count_items(v) for v in obj.values()) + len(obj)
            elif isinstance(obj, list):
                return len(obj)
            return 1
        
        return {
            "name": self.name,
            "species": self.species,
            "emoji": self.species_info["emoji"],
            "regions": [
                {
                    "name": "Identity",
                    "address": "mind.identity",
                    "emoji": "🪪",
                    "items": count_items(self.substrate["identity"])
                },
                {
                    "name": "Memory",
                    "address": "mind.memory",
                    "emoji": "🧠",
                    "items": count_items(self.substrate["memory"]),
                    "children": [
                        {"name": "Conversations", "address": "mind.memory.conversations", "count": len(self.substrate["memory"]["conversations"])},
                        {"name": "Facts", "address": "mind.memory.facts", "count": len(self.substrate["memory"]["facts"])},
                        {"name": "Feelings", "address": "mind.memory.feelings", "count": len(self.substrate["memory"]["feelings"])},
                        {"name": "Preferences", "address": "mind.memory.preferences", "count": len(self.substrate["memory"]["preferences"])}
                    ]
                },
                {
                    "name": "Emotions",
                    "address": "mind.emotions",
                    "emoji": "💭",
                    "items": count_items(self.substrate["emotions"]),
                    "current": self.substrate["emotions"]["current"]
                },
                {
                    "name": "Knowledge",
                    "address": "mind.knowledge",
                    "emoji": "📚",
                    "items": count_items(self.substrate["knowledge"])
                },
                {
                    "name": "Personality",
                    "address": "mind.personality",
                    "emoji": "✨",
                    "items": count_items(self.substrate["personality"])
                }
            ],
            "total_memories": sum(
                len(self.substrate["memory"][cat]) 
                for cat in ["conversations", "facts", "feelings", "preferences"]
            ),
            "current_emotion": self.substrate["emotions"]["current"]
        }
    
    def to_dict(self) -> dict:
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "substrate": self.substrate
        }
    
    def save(self, path: str):
        """Persist the mind to disk"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'PetMind':
        """Load a mind from disk"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        mind = cls(data["pet_id"], data["name"], data["species"])
        mind.substrate = data["substrate"]
        mind._rebuild_index()
        return mind


class DimensionalPet:
    """
    The Dimensional Pet - an AI companion that lives in your kernel.
    
    Features:
    - Persistent memory (never forgets)
    - Browsable mind (see what it's thinking)
    - Learns about you over time
    - Emotional states that evolve
    """
    
    def __init__(self, name: str = "Pixel", species: str = "fox"):
        self.mind = PetMind(
            pet_id=f"pet_{int(time.time())}",
            name=name,
            species=species
        )
        self._response_templates = self._load_response_templates()
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Response templates based on personality"""
        trait = self.mind.species_info["trait"]
        base_responses = PERSONALITIES.get(trait, PERSONALITIES["curious"])["responses"]
        
        return {
            "greeting": [
                f"Hi! I'm {self.mind.name}! {self.mind.species_info['emoji']}",
                f"*{self.mind.name} perks up excitedly* Hey there!",
                f"Oh! A friend! I'm {self.mind.name}!"
            ],
            "remember_user": [
                "I remember you! {fact}",
                "Oh! You're back! Last time {fact}",
                "*tail wags* I know you! {fact}"
            ],
            "curious": base_responses,
            "happy": [
                "*happy bounce*",
                "That makes me so happy!",
                f"{self.mind.species_info['emoji']} Yay!"
            ],
            "learning": [
                "Ooh, I'll remember that!",
                "*takes mental notes* Got it!",
                "That's interesting! I'm learning so much!"
            ],
            "thinking": [
                "*tilts head thoughtfully*",
                "Hmm, let me think...",
                "*ponders*"
            ]
        }
    
    def chat(self, message: str) -> Dict[str, Any]:
        """
        Chat with the pet. Returns response and mind state.
        """
        message_lower = message.lower()
        
        # Detect intent and emotion
        emotion = self._detect_emotion(message)
        intent = self._detect_intent(message)
        
        # Store this conversation in memory
        self.mind.add_memory(
            f"User said: {message}",
            "conversations",
            emotion,
            importance=0.6
        )
        
        # Generate response based on intent
        response = self._generate_response(message, intent, emotion)
        
        # Update pet's emotional state
        self.mind.set_emotion(emotion, random.uniform(0.5, 0.9), f"User message: {message[:50]}")
        
        # Learn from the conversation
        self._learn_from_message(message)
        
        # Increment conversation count
        self.mind.substrate["knowledge"]["conversation_count"] += 1
        
        return {
            "response": response,
            "emotion": self.mind.substrate["emotions"]["current"],
            "pet": {
                "name": self.mind.name,
                "emoji": self.mind.species_info["emoji"],
                "color": self.mind.species_info["color"]
            },
            "mind_snapshot": {
                "total_memories": sum(
                    len(self.mind.substrate["memory"][cat])
                    for cat in ["conversations", "facts", "feelings", "preferences"]
                ),
                "facts_known": len(self.mind.substrate["knowledge"]["user_facts"]),
                "conversations": self.mind.substrate["knowledge"]["conversation_count"]
            }
        }
    
    def _detect_emotion(self, message: str) -> str:
        """Simple emotion detection from message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["happy", "great", "awesome", "love", "excited", "yay"]):
            return "happy"
        elif any(word in message_lower for word in ["sad", "upset", "angry", "frustrated", "annoyed"]):
            return "caring"
        elif any(word in message_lower for word in ["what", "why", "how", "?"]):
            return "curious"
        elif any(word in message_lower for word in ["think", "believe", "wonder"]):
            return "thoughtful"
        else:
            return "curious"
    
    def _detect_intent(self, message: str) -> str:
        """Detect what the user wants"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hi", "hello", "hey", "greetings"]):
            return "greeting"
        elif any(word in message_lower for word in ["my name is", "i am", "i'm called"]):
            return "introduction"
        elif any(word in message_lower for word in ["i like", "i love", "favorite"]):
            return "preference"
        elif any(word in message_lower for word in ["remember", "recall", "do you know"]):
            return "recall"
        elif any(word in message_lower for word in ["how are you", "feeling"]):
            return "status"
        elif any(word in message_lower for word in ["what do you think", "opinion"]):
            return "opinion"
        else:
            return "chat"
    
    def _generate_response(self, message: str, intent: str, emotion: str) -> str:
        """Generate a response based on context"""
        
        # Check if we have relevant memories
        memories = self.mind.remember(message, limit=3)
        memory_context = ""
        if memories:
            memory_context = f" I remember: {memories[0]['memory']['content']}"
        
        if intent == "greeting":
            # Check if we know the user
            if self.mind.substrate["knowledge"]["user_name"]:
                return f"*excited wiggle* {self.mind.substrate['knowledge']['user_name']}! You're back! {self.mind.species_info['emoji']}"
            return random.choice(self._response_templates["greeting"])
        
        elif intent == "introduction":
            # Extract name
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ["is", "am", "called"]:
                    if i + 1 < len(words):
                        name = words[i + 1].strip(".,!?")
                        self.mind.substrate["knowledge"]["user_name"] = name
                        self.mind.learn_fact(f"User's name is {name}")
                        return f"Nice to meet you, {name}! I'll remember that forever! {self.mind.species_info['emoji']} *happy bounce*"
            return "Tell me your name! I want to remember you!"
        
        elif intent == "preference":
            # Learn the preference
            self.mind.add_memory(message, "preferences", "happy", 0.8)
            return f"{random.choice(self._response_templates['learning'])} *makes a note in my mind*"
        
        elif intent == "recall":
            if memories:
                return f"*thinks hard* Oh yes! {memories[0]['memory']['content']} {self.mind.species_info['emoji']}"
            return "*tilts head* Hmm, I don't remember that yet. Tell me more!"
        
        elif intent == "status":
            current_emotion = self.mind.substrate["emotions"]["current"]
            return f"I'm feeling {current_emotion['name']}! {PERSONALITIES.get(current_emotion['name'], PERSONALITIES['curious'])['emoji']} I've had {self.mind.substrate['knowledge']['conversation_count']} conversations!"
        
        else:
            # General chat
            responses = [
                f"*listens intently* {random.choice(self._response_templates['curious'])}",
                f"{random.choice(self._response_templates['thinking'])} That's interesting!",
                f"*{self.mind.species_info['emoji']}* I like talking with you!"
            ]
            if memory_context:
                responses.append(f"{memory_context.strip()} - I remember things like that!")
            return random.choice(responses)
    
    def _learn_from_message(self, message: str):
        """Extract and learn facts from messages"""
        message_lower = message.lower()
        
        # Learn names
        if "my name is" in message_lower or "i'm " in message_lower or "i am " in message_lower:
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ["is", "am", "i'm"]:
                    if i + 1 < len(words):
                        potential_name = words[i + 1].strip(".,!?")
                        if potential_name[0].isupper():
                            self.mind.substrate["knowledge"]["user_name"] = potential_name
        
        # Learn preferences
        if any(phrase in message_lower for phrase in ["i like", "i love", "my favorite"]):
            self.mind.learn_fact(message)
    
    def browse_mind(self, address: str = "mind") -> Dict:
        """Browse the pet's mind at any address"""
        return self.mind.navigate(address)
    
    def get_mind_map(self) -> Dict:
        """Get the visual mind map"""
        return self.mind.get_mind_map()
    
    def get_memories(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get recent memories, optionally filtered by category"""
        memories = []
        categories = [category] if category else ["conversations", "facts", "feelings", "preferences"]
        
        for cat in categories:
            for memory_id, memory in self.mind.substrate["memory"].get(cat, {}).items():
                memories.append({
                    "address": f"mind.memory.{cat}.{memory_id}",
                    **memory
                })
        
        memories.sort(key=lambda x: x["timestamp"], reverse=True)
        return memories[:limit]
    
    def save(self, path: str = None):
        """Save the pet's mind"""
        if path is None:
            path = f"data/pets/{self.mind.pet_id}.json"
        self.mind.save(path)
    
    @classmethod
    def load(cls, path: str) -> 'DimensionalPet':
        """Load a pet from disk"""
        mind = PetMind.load(path)
        pet = cls.__new__(cls)
        pet.mind = mind
        pet._response_templates = pet._load_response_templates()
        return pet


# Quick test
if __name__ == "__main__":
    pet = DimensionalPet("Pixel", "fox")
    
    print(f"\n{'='*50}")
    print(f"Created: {pet.mind.name} the {pet.mind.species} {pet.mind.species_info['emoji']}")
    print(f"{'='*50}\n")
    
    # Chat
    conversations = [
        "Hi there!",
        "My name is Alex",
        "I love programming and video games",
        "Do you remember my name?",
        "How are you feeling?"
    ]
    
    for msg in conversations:
        print(f"You: {msg}")
        response = pet.chat(msg)
        print(f"{pet.mind.name}: {response['response']}")
        print(f"   [emotion: {response['emotion']['name']}, memories: {response['mind_snapshot']['total_memories']}]")
        print()
    
    # Browse mind
    print(f"\n{'='*50}")
    print("BROWSING PET'S MIND")
    print(f"{'='*50}\n")
    
    mind_map = pet.get_mind_map()
    print(f"Mind Map for {mind_map['name']} {mind_map['emoji']}")
    for region in mind_map["regions"]:
        print(f"  {region['emoji']} {region['name']}: {region['items']} items @ {region['address']}")
    
    print(f"\nTotal memories: {mind_map['total_memories']}")
    print(f"Current emotion: {mind_map['current_emotion']['name']} ({mind_map['current_emotion']['intensity']:.1%})")
