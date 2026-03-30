from flask import Flask, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db_connection():
    db_url = os.environ.get('POSTGRES_URL')
    if not db_url:
        raise Exception("POSTGRES_URL environment variable is not set. Please configure Vercel Postgres.")
    
    # Vercel's POSTGRES_URL already includes ?sslmode=require
    conn = psycopg2.connect(db_url)
    return conn

@app.route('/api/memo', methods=['GET'])
def get_memos():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT id, content, timestamp FROM memos ORDER BY id DESC')
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"message": "success", "data": rows}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memo', methods=['POST'])
def save_memo():
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({"error": "Content cannot be empty"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO memos (content) VALUES (%s)', (content,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Memo saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memo/<int:memo_id>', methods=['DELETE'])
def delete_memo(memo_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM memos WHERE id = %s", (memo_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Memo deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
