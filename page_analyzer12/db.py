import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


class DatabaseRepository:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def cursor(self, cursor_factory=NamedTupleCursor):
        return self.conn.cursor(cursor_factory=cursor_factory)

    def fetch_all(self, query, values=()):
        with self.cursor() as cur:
            cur.execute(query, values)
            return cur.fetchall()

    def execute(self, query, values=()):
        with self.cursor() as cur:
            cur.execute(query, values)
            self.conn.commit()


def add_url_to_db(url):
    with DatabaseRepository() as repo:
        repo.execute("INSERT INTO urls (name) VALUES (%s)", (url,))

def get_url_by_name(url):
    with DatabaseRepository() as repo:
        results = repo.fetch_all("SELECT * FROM urls WHERE name = %s", (url,))
        if results:
            return results[0]
        else:
            return None

def get_url_by_id(url_id):
    query = "SELECT * FROM urls WHERE id = %s"
    with DatabaseRepository() as repo:
        return repo.fetch_all(query, (url_id,))[0]

def add_check_to_db(url_id, status_code, page_data):
    with DatabaseRepository() as repo:
        repo.execute(
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
    with DatabaseRepository() as repo:
        return repo.fetch_all(query)

def get_checks_desc(url_id):
    query = """
        SELECT id, status_code, COALESCE(h1, '') as h1,
        COALESCE(title, '') as title, COALESCE(description, '') as description,
        created_at::text
        FROM url_checks
        WHERE url_id = %s
        ORDER BY id DESC
    """
    with DatabaseRepository() as repo:
        return repo.fetch_all(query, (url_id,))
