"""Слой доступа к данным: единая точка работы с pyodbc."""

import pyodbc
from src.config import DB_CONFIG


class DatabaseContext:
    def __init__(self):
        self.connection_string = (
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection={DB_CONFIG['trusted_connection']};"
            f"TrustServerCertificate={DB_CONFIG['trust_server_certificate']};"
        )

    def get_connection(self) -> pyodbc.Connection:
        return pyodbc.connect(self.connection_string, autocommit=False)

    def execute(self, query: str, params: tuple = ()) -> int:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount

    def fetch_all(self, query: str, params: tuple = ()) -> list:
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            cols = [c[0] for c in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]

    def fetch_one(self, query: str, params: tuple = ()):
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None


db = DatabaseContext()