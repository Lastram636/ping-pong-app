import os
import datetime
import mysql.connector
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Configuration
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'pingpongdb')

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            created_at DATETIME
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            score INT,
            created_at DATETIME
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ping')
def ping():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now()
        cursor.execute("INSERT INTO pings (created_at) VALUES (%s)", (now,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "pong", "timestamp": now.isoformat(), "status": "saved"})
    except Exception as e:
        return jsonify({"message": "pong", "error": str(e), "status": "failed_to_save"}), 500

@app.route('/api/save_score', methods=['POST'])
def save_score():
    try:
        data = request.json
        score = data.get('score', 0)
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now()
        cursor.execute("INSERT INTO scores (score, created_at) VALUES (%s, %s)", (score, now))
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"status": "saved", "id": last_id, "score": score})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    # Try to init table on start
    try:
        init_db()
    except Exception as e:
        print("DB Connection failed at startup:", e)
    
    app.run(host='0.0.0.0', port=5000)
