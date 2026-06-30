#!/usr/bin/env python3
"""
BIODISC Dashboard Server
Serves the BIODISC Live dashboard on port 8789
"""

import http.server
import socketserver
import os
import json
import threading
import time
from pathlib import Path

# Configuration
PORT = 8789
DASHBOARD_DIR = Path(__file__).parent


class BIODISCDashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for BIODISC dashboard"""

    # BIODISC state
    cycle_count = 0
    discoveries = []
    corpus_stats = {
        'total_papers': 1300,
        'domains': 10,
        'arxiv_papers': 800,
        'openalex_papers': 500
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        # Serve the dashboard
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Increment cycle count to simulate activity
            BIODISCDashboardHandler.cycle_count += 1

            status_data = {
                'engine': {
                    'cycle_count': BIODISCDashboardHandler.cycle_count,
                    'system_confidence': 0.85 + (0.01 * (BIODISCDashboardHandler.cycle_count % 10)),
                    'status': 'running'
                },
                'corpus': BIODISCDashboardHandler.corpus_stats,
                'timestamp': time.time()
            }
            self.wfile.write(json.dumps(status_data).encode())
            return

        elif self.path == '/api/discoveries':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Generate mock discoveries
            if len(BIODISCDashboardHandler.discoveries) < 5:
                domains = ['Molecular Biology', 'Biochemistry', 'Genetics', 'Cell Biology',
                          'Biophysics', 'Bioinformatics', 'Computational Biology', 'Genomics']
                import random
                discovery = {
                    'id': len(BIODISCDashboardHandler.discoveries) + 1,
                    'title': f'Novel {random.choice(domains)} insight discovered',
                    'domain': random.choice(domains),
                    'confidence': round(0.85 + random.random() * 0.14, 2),
                    'timestamp': time.time()
                }
                BIODISCDashboardHandler.discoveries.insert(0, discovery)

            discoveries_data = {
                'discoveries': BIODISCDashboardHandler.discoveries[:10],
                'total': len(BIODISCDashboardHandler.discoveries)
            }
            self.wfile.write(json.dumps(discoveries_data).encode())
            return

        return super().do_GET()

    def log_message(self, format, *args):
        """Custom log messages"""
        print(f"[BIODISC Dashboard] {args[0]}")


class BIODISCDashboardServer:
    """BIODISC Dashboard Server"""

    def __init__(self, port=PORT):
        self.port = port
        self.handler = BIODISCDashboardHandler
        self.server = None
        self.server_thread = None

    def start(self):
        """Start the dashboard server"""
        try:
            # Create server
            self.server = socketserver.TCPServer(("", self.port), self.handler)
            self.server.allow_reuse_address = True

            # Start in background thread
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()

            print(f"✓ BIODISC Dashboard started successfully!")
            print(f"  Dashboard: http://localhost:{self.port}")
            print(f"  API: http://localhost:{self.port}/api/status")
            return True

        except Exception as e:
            print(f"✗ Failed to start dashboard: {e}")
            return False

    def stop(self):
        """Stop the dashboard server"""
        if self.server:
            self.server.shutdown()
            print("Dashboard stopped")


def start_dashboard(port=PORT):
    """Start the BIODISC dashboard server"""
    server = BIODISCDashboardServer(port)
    return server.start()


if __name__ == '__main__':
    import sys

    port = PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
            print(f"Using default port: {PORT}")

    print("Starting BIODISC Dashboard Server...")
    print("-" * 50)

    server = BIODISCDashboardServer(port)
    if server.start():
        print("-" * 50)
        print("Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping dashboard...")
            server.stop()
    else:
        print("Failed to start dashboard")
        sys.exit(1)
