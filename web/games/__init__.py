"""
ButterflyFX Games Package
Dimensional games integrated with the Helix kernel
"""

from .fasttrack import FastTrackKernel, init_fasttrack, get_fasttrack

__all__ = [
    'FastTrackKernel',
    'init_fasttrack',
    'get_fasttrack'
]

# Game registry
GAMES = {
    'fasttrack': {
        'name': 'Fast Track',
        'description': 'A 2-6 player board game with online multiplayer and AI',
        'url': '/games/fasttrack/',
        'players': '2-6',
        'supports_ai': True,
        'supports_multiplayer': True
    }
}

def get_available_games():
    """Return list of available games."""
    return GAMES
