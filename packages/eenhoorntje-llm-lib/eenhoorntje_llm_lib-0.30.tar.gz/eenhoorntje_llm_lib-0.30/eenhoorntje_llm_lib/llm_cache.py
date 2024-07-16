import sqlite3
import os


class Cache:
    def __init__(self, db_path="llm_cache.db"):
        self.db_path = db_path
        if os.path.exists(db_path) is False:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE llm_cache (key TEXT PRIMARY KEY, value TEXT)")
            conn.commit()
            conn.close()

    def add(self, key, value):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO llm_cache (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            if conn:
                conn.close()

    def query(self, key):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM llm_cache WHERE key=?", (key,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
            else:
                return None
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def clear(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM llm_cache")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
        finally:
            if conn:
                conn.close()


cache = Cache()


def clear_cache():
    cache.clear()


def init_cache(db_path="llm_cache.db"):
    global cache
    cache = Cache(db_path)


init_cache()
