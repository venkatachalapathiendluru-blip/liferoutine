# Simple Node.js server for routing

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import urllib.parse

class LifeRoutineHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Route /summary/ to summary.html
        if path == '/summary/' or path == '/summary':
            self.path = '/summary.html'
        # Route /admin/ to admin.html
        elif path == '/admin/' or path == '/admin':
            self.path = '/admin.html'
        # Route /water/ to water-tracker.html
        elif path == '/water/' or path == '/water':
            self.path = '/water-tracker.html'
        # Route / to index.html
        elif path == '/' or path == '':
            self.path = '/index.html'
        
        # Serve the file
        return super().do_GET()
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), LifeRoutineHandler)
    print(f"Server running at http://localhost:{port}")
    print("Routes:")
    print("  http://localhost:8000/ - Meal Planner")
    print("  http://localhost:8000/summary/ - Daily Summary")
    print("  http://localhost:8000/admin/ - Food Admin")
    print("  http://localhost:8000/water/ - Water Tracker")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
        server.shutdown()