import psycopg2
from psycopg2.extras import NamedTupleCursor
from contextlib import contextmanager

class DatabaseRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    @contextmanager
    def connection(self):
        conn = psycopg2.connect(self.db_url, cursor_factory=NamedTupleCursor)
        try:
            yield conn
        finally:
            conn.close()

    def fetch_all(self, query, values=()):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                return cur.fetchall()

    def execute(self, query, values=()):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                conn.commit()

    def add_url_to_db(self, url):
        self.execute("INSERT INTO urls (name) VALUES (%s)", (url,))

    def get_url_by_name(self, url):
        results = self.fetch_all("SELECT * FROM urls WHERE name = %s", (url,))
        if results:
            return results[0]
        else:
            return None

    def get_url_by_id(self, url_id):
        return self.fetch_all("SELECT * FROM urls WHERE id = %s", (url_id,))[0]

    def add_check_to_db(self, url_id, status_code, page_data):
        self.execute(
            """
            INSERT INTO url_checks (
                url_id, status_code, h1, title, description)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (url_id, status_code,
             page_data['h1'], page_data['title'], page_data['description']),
        )

    def get_urls_with_latest_check(self):
        return self.fetch_all("""
               SELECT urls.id, urls.name,
               COALESCE(url_checks.status_code::text, '') as status_code,
               COALESCE(MAX(url_checks.created_at)::text, '') as latest_check
               FROM urls
               LEFT JOIN url_checks ON urls.id = url_checks.url_id
               GROUP BY urls.id, url_checks.status_code
               ORDER BY urls.id DESC
           """)

    def get_checks_desc(self, url_id):
        return self.fetch_all("""
               SELECT id, status_code, COALESCE(h1, '') as h1,
               COALESCE(title, '') as title, COALESCE(description, '') as description,
               created_at::text
               FROM url_checks
               WHERE url_id = %s
               ORDER BY id DESC
           """, (url_id,))

    def add_url_to_db_with_returning(self, url):
        query = "INSERT INTO urls (name) VALUES (%s) RETURNING *"
        result = self.fetch_all(query, (url,))
        return result[0] if result else None
