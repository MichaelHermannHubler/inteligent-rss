import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from sources.BaseSource import RSSItem
from .utils import adapt_timeobj, convert_timeobj


class RSSDatabase:
    """SQLite database for storing RSS items and LLM processing results"""

    def __init__(self, db_path: str = "rss_data.db"):
        """
        Initialize the database

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

        # Converts DT.time to TEXT when inserting
        sqlite3.register_adapter(datetime.time, adapt_timeobj)

        # Converts TEXT to DT.time when selecting
        sqlite3.register_converter("timeobj", convert_timeobj)

        self._create_tables()

    def _create_tables(self):
        """Create the necessary database tables"""
        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()

            # Create RSS items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rss_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    description TEXT,
                    content TEXT,
                    published TEXT NOT NULL,
                    source ID NOT NULL,
                    FOREIGN KEY (source) REFERENCES sources(name)
                )
            """
            )

            # Create query_text table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT UNIQUE NOT NULL,
                    resolved INTEGER DEFAULT 0,
                    resolved_by INTEGER DEFAULT NULL,
                    FOREIGN KEY (resolved_by) REFERENCES rss_items(id)
                )
            """
            )

            # Create LLM processing results table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS llm_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER NOT NULL,
                    query_id INTEGER NOT NULL,
                    llm_response INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES rss_items (id)
                )
            """
            )

            # Create sources table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    last_consumed TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_rss_items_source ON rss_items(source)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_rss_items_published ON rss_items(published)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_llm_results_query_id ON llm_results(query_id)"
            )

            conn.commit()

    def store_rss_items(self, items: List[RSSItem]) -> int:
        """
        Store RSS items in the database

        Args:
            items: List of RSS items to store

        Returns:
            Number of items successfully stored
        """
        stored_count = 0

        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()

            for item in items:
                try:
                    cursor.execute(
                        "SELECT id FROM rss_items WHERE link = ? AND source = ?",
                        (item.link, item.source),
                    )
                    exists = cursor.fetchone()
                    if exists:
                        continue  # Skip if already exists

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO rss_items 
                        (title, link, description, content, published, source)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            item.title,
                            item.link,
                            item.description,
                            item.content,
                            item.published,
                            item.source,
                        ),
                    )
                    stored_count += 1

                except sqlite3.Error as e:
                    print(f"Error storing RSS item '{item.title}': {e}")
                    continue

            conn.commit()

        return stored_count

    def store_llm_results(
        self, query_id: int, item_title: str, source: str, response: str
    ) -> int:
        """
        Store LLM processing results in the database.
        Uses query_id as a foreign key from the queries table.
        Finds item_id using item_title and source.

        Args:
            query_id: ID of the query in the queries table
            item_title: Title of the RSS item
            source: Source name of the RSS item
            response: LLM response to store

        Returns:
            1 if result successfully stored, 0 otherwise
        """
        stored_count = 0

        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()
            try:
                # Find item_id using title and source
                cursor.execute(
                    "SELECT id FROM rss_items WHERE title = ? AND source = ?",
                    (item_title, source),
                )
                item_row = cursor.fetchone()
                if not item_row:
                    print(
                        f"RSS item not found for title '{item_title}' and source '{source}'."
                    )
                    return 0
                item_id = item_row[0]

                # Insert into llm_results using query_id and found item_id
                cursor.execute(
                    """
                    INSERT INTO llm_results 
                    (item_id, query_id, llm_response, created_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (item_id, query_id, response, datetime.now().isoformat()),
                )
                stored_count += 1

            except sqlite3.Error as e:
                print(
                    f"Error storing LLM result for '{(item_title, source, query_id)}': {e}"
                )

            conn.commit()

        return stored_count

    def get_queries(self, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Retrieve queries from the queries table.

        Args:
            resolved: If set, filter queries by resolved status.

        Returns:
            List of queries as dictionaries.
        """
        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()
            if resolved is None:
                cursor.execute("SELECT id, query, resolved, resolved_by FROM queries")
            else:
                cursor.execute(
                    "SELECT id, query, resolved, resolved_by FROM queries WHERE coalesce(resolved, ?) = ?",
                    ((int(resolved)), (int(resolved))),
                )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "query": row[1],
                    "resolved": bool(row[2]),
                    "resolved_by": row[3],
                }
                for row in rows
            ]

    def store_source_info(self, name: str, url: str):
        """
        Store or update source information

        Args:
            source_info: Source metadata to store
        """
        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO sources 
                    (name, url, last_consumed)
                    VALUES (?, ?, ?)
                """,
                    (
                        name,
                        url,
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()

            except sqlite3.Error as e:
                print(f"Error storing source info for '{name}': {e}")

    def resolve_query(
        self, query_id: int, resolved_by_item_title: str, resolved_by_source: str
    ) -> bool:
        """
        Mark a query as resolved in the queries table.

        Args:
            query_id: ID of the query to resolve
            resolved_by_item_id: Optional RSS item ID that resolved the query

        Returns:
            True if the query was updated, False otherwise
        """
        with sqlite3.connect(
            self.db_path, detect_types=sqlite3.PARSE_DECLTYPES
        ) as conn:
            cursor = conn.cursor()
            try:
                # Find item_id using title and source
                cursor.execute(
                    "SELECT id FROM rss_items WHERE title = ? AND source = ?",
                    (resolved_by_item_title, resolved_by_source),
                )
                item_row = cursor.fetchone()
                if not item_row:
                    print(
                        f"RSS item not found for title '{resolved_by_item_title}' and source '{resolved_by_source}'."
                    )
                    return 0
                resolved_by_item_id = item_row[0]

                if resolved_by_item_id is not None:
                    cursor.execute(
                        "UPDATE queries SET resolved = 1, resolved_by = ? WHERE id = ?",
                        (resolved_by_item_id, query_id),
                    )
                else:
                    cursor.execute(
                        "UPDATE queries SET resolved = 1 WHERE id = ?", (query_id,)
                    )
                conn.commit()
                return cursor.rowcount > 0
            except sqlite3.Error as e:
                print(f"Error resolving query {query_id}: {e}")
                return False
