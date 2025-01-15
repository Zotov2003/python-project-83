import psycopg2
from psycopg2.extras import NamedTupleCursor
from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

class DBConnection:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cur = self.conn.cursor(cursor_factory=NamedTupleCursor)
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()

def fetch_all(query, values=()):
    with DBConnection() as cur:
        cur.execute(query, values)
        return cur.fetchall()

def add_url_to_db(url):
    with DBConnection() as cur:
        cur.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
        # Не нужно явно вызывать commit, так как делается в __exit__

def get_url_by_name(url):
    with DBConnection() as cur:
        cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
        return cur.fetchone()

def get_url_by_id(url_id):
    query = "SELECT * FROM urls WHERE id = %s"
    return fetch_all(query, (url_id,))

def add_check_to_db(url_id, status_code, page_data):
    with DBConnection() as cur:
        cur.execute(
            """
            INSERT INTO url_checks (
            url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (url_id, status_code,
             page_data['h1'], page_data['title'], page_data['description']),
        )

def get_urls_with_latest_check():
    query = """
        SELECT urls.id, urls.name,
        COALESCE(url_checks.status_code::text, '') as status_code,
        COALESCE(MAX(url_checks.created_at)::text, '') as latest_check
        FROM urls
        LEFT JOIN url_checks ON urls.id = url_checks.url_id
        GROUP BY urls.id, url_checks.status_code
        ORDER BY urls.id DESC
    """
    return fetch_all(query)

def get_checks_desc(url_id):
    query = """
        SELECT id, status_code, COALESCE(h1, '') as h1,
        COALESCE(title, '') as title, COALESCE(description, '') as description,
        created_at::text
        FROM url_checks
        WHERE url_id = %s
        ORDER BY id DESC
    """
    return fetch_all(query, (url_id,))
