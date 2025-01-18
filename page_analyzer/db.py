import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.DATABASE_URL = os.getenv('DATABASE_URL')

    def get_connection(self):
        return psycopg2.connect(self.DATABASE_URL)

    def fetch_all(self, query, values=()):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                cur.execute(query, values)
                return cur.fetchall()

    def add_url_to_db(self, url):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
                conn.commit()

    def get_url_by_name(self, url):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
                return cur.fetchone()

    def get_url_by_id(self, url_id):
        query = "SELECT * FROM urls WHERE id = %s"
        return self.fetch_all(query, (url_id,))

    def add_check_to_db(self, url_id, status_code, page_data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO url_checks (
                    url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (url_id, status_code,
                     page_data['h1'], page_data['title'], page_data['description']),
                )
                conn.commit()

    def get_urls_with_latest_check(self):
        query = """
            SELECT urls.id, urls.name,
            COALESCE(url_checks.status_code::text, '') as status_code,
            COALESCE(MAX(url_checks.created_at)::text, '') as latest_check
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id, url_checks.status_code
            ORDER BY urls.id DESC
        """
        return self.fetch_all(query)

    def get_checks_desc(self, url_id):
        query = """
            SELECT id, status_code, COALESCE(h1, '') as h1,
            COALESCE(title, '') as title, COALESCE(description, '') as description,
            created_at::text
            FROM url_checks
            WHERE url_id = %s
            ORDER BY id DESC
        """
        return self.fetch_all(query, (url_id,))
