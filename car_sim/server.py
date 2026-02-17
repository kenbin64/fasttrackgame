#!/usr/bin/env python3
"""
ButterflyFX Car Simulator Server

Serves the car simulator and optionally fetches real car specs via NHTSA API.
Pure substrate transformations - no AI.
"""

import http.server
import socketserver
import json
import os
from pathlib import Path

# Try to import car API for real specs
try:
    from car_api import fetch_car_specs
    HAS_API = True
except ImportError:
    HAS_API = False

PORT = 8088
DIRECTORY = Path(__file__).parent


class CarSimHandler(http.server.SimpleHTTPRequestHandler):
    """Handles requests for the car simulator."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def do_GET(self):
        # API endpoint for car specs
        if self.path.startswith('/api/car'):
            self.handle_car_api()
        elif self.path == '/' or self.path == '':
            # Serve the dimensional car simulator (proper paradigm)
            self.path = '/dimensional_car.html'
            super().do_GET()
        elif self.path == '/classic':
            self.path = '/simulator.html'
            super().do_GET()
        else:
            super().do_GET()
    
    def handle_car_api(self):
        """Fetch car specs from NHTSA API or return defaults."""
        from urllib.parse import parse_qs, urlparse
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        specs = None
        
        if HAS_API:
            if 'vin' in params:
                specs = fetch_car_specs(vin=params['vin'][0])
            elif 'make' in params and 'model' in params:
                year = int(params.get('year', [2024])[0])
                specs = fetch_car_specs(
                    make=params['make'][0],
                    model=params['model'][0],
                    year=year
                )
        
        if specs is None:
            # Default specs
            specs = {
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2024,
                'horsepower': 180,
                'torque': 170,
                'weight_lbs': 3400,
                'mpg_combined': 28,
                'fuel_capacity': 14,
                'top_speed': 140,
                'zero_to_sixty': 7.8
            }
        else:
            # Convert dataclass to dict
            specs = {
                'make': specs.make,
                'model': specs.model,
                'year': specs.year,
                'horsepower': specs.horsepower,
                'torque': specs.torque,
                'weight_lbs': specs.weight_lbs,
                'mpg_combined': specs.mpg_combined,
                'fuel_capacity': specs.fuel_capacity_gallons,
                'top_speed': 140,  # Estimated
                'zero_to_sixty': round(6.0 * (3500 / specs.weight_lbs) * (200 / specs.horsepower), 1)
            }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(specs).encode())
    
    def log_message(self, format, *args):
        print(f"[CarSim] {args[0]}")


def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║         🦋 ButterflyFX Car Simulator Server 🦋               ║
╠══════════════════════════════════════════════════════════════╣
║  Pure Substrate Transformations - No AI                      ║
╟──────────────────────────────────────────────────────────────╢
║  Server running on: http://localhost:{PORT}                    ║
║                                                              ║
║  Controls:                                                   ║
║    • Right Click (Hold): Accelerate                          ║
║    • Left Click (Hold):  Brake                               ║
║    • Mouse Position:     Steering                            ║
║    • P / R / D:          Park / Reverse / Drive              ║
║    • T:                  Reset Trip                          ║
╟──────────────────────────────────────────────────────────────╢
║  API Endpoints:                                              ║
║    GET /api/car                     - Default specs          ║
║    GET /api/car?make=X&model=Y      - Fetch by make/model    ║
║    GET /api/car?vin=XXX             - Fetch by VIN           ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    with socketserver.TCPServer(("", PORT), CarSimHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[CarSim] Server stopped.")


if __name__ == '__main__':
    main()
