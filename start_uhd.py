#!/usr/bin/env python3
"""Start Universal Hard Drive Server"""

import sys
import os
sys.path.insert(0, '.')

from apps.universal_harddrive import UniversalHardDrive, run_server
from apps.helix_database import HelixDatabase

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    host = sys.argv[2] if len(sys.argv) > 2 else '0.0.0.0'
    
    uhd = UniversalHardDrive()
    
    # Connect API drive (B:)
    uhd.connect_api()
    
    # Connect Database drive (C:)
    db = HelixDatabase("uhd_data")
    # Add some demo collections if empty
    if not db.list_collections():
        db.create_collection("contacts", level=5)
        db.create_collection("notes", level=4)
        db.create_collection("projects", level=5)
        db.insert("contacts", {"name": "Alice", "email": "alice@example.com"})
        db.insert("contacts", {"name": "Bob", "email": "bob@example.com"})
        db.insert("notes", {"title": "Welcome", "content": "Your Universal Hard Drive is ready!"})
        db.insert("projects", {"name": "DimensionOS", "status": "active"})
    uhd.connect_database(db)
    
    # A: drive auto-connects when accessed (real filesystem)
    
    run_server(uhd, host=host, port=port)
