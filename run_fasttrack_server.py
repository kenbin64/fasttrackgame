#!/usr/bin/env python3
"""
Fast Track WebSocket Server
Run this alongside the main server for multiplayer support

Usage: python run_fasttrack_server.py [--port 8765]
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Please install websockets: pip install websockets")

from web.games.fasttrack.server import fasttrack_server, handle_fasttrack_ws


async def handler(websocket, path):
    """Handle incoming WebSocket connections."""
    print(f"New connection: {path}")
    
    # Extract room code from path
    # Expected path: /ws/fasttrack/{room_code}
    parts = path.strip('/').split('/')
    
    if len(parts) >= 3 and parts[0] == 'ws' and parts[1] == 'fasttrack':
        room_code = parts[2]
    else:
        room_code = fasttrack_server.generate_room_code()
    
    await fasttrack_server.handle_websocket(websocket, room_code)


async def main(host: str, port: int):
    """Start the WebSocket server."""
    print(f"🎮 Fast Track WebSocket Server starting on ws://{host}:{port}")
    print(f"   Connect with: ws://{host}:{port}/ws/fasttrack/{{room_code}}")
    print()
    
    async with websockets.serve(handler, host, port):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    if not WEBSOCKETS_AVAILABLE:
        print("Error: websockets library required")
        print("Install with: pip install websockets")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Fast Track WebSocket Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on")
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.host, args.port))
    except KeyboardInterrupt:
        print("\nServer stopped")
