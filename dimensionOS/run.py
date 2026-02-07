#!/usr/bin/env python3
"""
DimensionOS Development Server
Run this for local development with SSL
"""

import os
from app import app

if __name__ == '__main__':
    print("=" * 70)
    print("DimensionOS - The Dimensional Operating System")
    print("=" * 70)
    print("\nStarting development server...")
    print("URL: https://localhost:5000")
    print("\nNote: You'll see a browser warning about the self-signed certificate.")
    print("This is normal for development. Click 'Advanced' and 'Proceed'.")
    print("\nPress Ctrl+C to stop the server.")
    print("=" * 70)
    print()
    
    # Run with SSL (self-signed certificate for development)
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context='adhoc',
        debug=True
    )

