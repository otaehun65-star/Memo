import http.server
import socketserver
import json
import sqlite3
import os
import urllib.parse

PORT = 3000
DB_FILE = 'memo.db'

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class MemoHandler(http.server.SimpleHTTPRequestHandler):
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS, POST, DELETE')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-type")
        self.end_headers()
        
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/memo':
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute('SELECT id, content, timestamp FROM memos ORDER BY id DESC')
            rows = c.fetchall()
            conn.close()
            
            self._set_headers()
            data = [{"id": row[0], "content": row[1], "timestamp": row[2]} for row in rows]
            self.wfile.write(json.dumps({"message": "success", "data": data}).encode('utf-8'))
        else:
            # Serve static files from 'public' directory
            if self.path == '/':
                self.path = '/public/index.html'
            elif not self.path.startswith('/public/'):
                self.path = '/public' + self.path
            return super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/api/memo':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                content = data.get('content', '').strip()
                
                if not content:
                    raise ValueError("Content cannot be empty")

                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute('INSERT INTO memos (content) VALUES (?)', (content,))
                conn.commit()
                conn.close()
                
                self._set_headers()
                self.wfile.write(json.dumps({"message": "Memo saved successfully"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_error(404)

    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path.startswith('/api/memo/'):
            try:
                memo_id = int(parsed_path.path.split('/')[-1])
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute("DELETE FROM memos WHERE id = ?", (memo_id,))
                conn.commit()
                conn.close()
                
                self._set_headers()
                self.wfile.write(json.dumps({"message": "Memo deleted successfully"}).encode('utf-8'))
            except ValueError:
                self.send_error(400, "Invalid memo ID")
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

with socketserver.TCPServer(("", PORT), MemoHandler) as httpd:
    print(f"Serving at port {PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
