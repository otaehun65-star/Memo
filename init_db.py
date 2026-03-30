import psycopg2
import os

def init_db():
    db_url = os.environ.get('POSTGRES_URL')
    if not db_url:
        print("ERROR: POSTGRES_URL environment variable is not set.")
        print("Please provide the Vercel Postgres URL to run this script.")
        return

    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(db_url, sslmode='require')
        cur = conn.cursor()
        
        print("Creating 'memos' table if it doesn't exist...")
        cur.execute('''
            CREATE TABLE IF NOT EXISTS memos (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table 'memos' initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
