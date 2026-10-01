import json
import sqlite3
import uuid
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "items.db"
SEED_PATH = BASE_DIR / "seed.json"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            source_name TEXT NOT NULL,
            published_at TEXT NOT NULL,
            url TEXT NOT NULL,
            summary TEXT NOT NULL,
            tags TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def seed_database():
    connection = get_connection()

    count = connection.execute(
        "SELECT COUNT(*) FROM items"
    ).fetchone()[0]

    if count == 0:
        with open(SEED_PATH, "r", encoding="utf-8") as file:
            seed_data = json.load(file)

        for item in seed_data["items"]:
            connection.execute(
                """
                INSERT INTO items (
                    id,
                    title,
                    source_name,
                    published_at,
                    url,
                    summary,
                    tags
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    item["title"],
                    item["source"]["name"],
                    item["publishedAt"],
                    item["url"],
                    item["summary"],
                    json.dumps(item["tags"]),
                ),
            )

        connection.commit()

    connection.close()


def row_to_item(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "source": {
            "name": row["source_name"]
        },
        "publishedAt": row["published_at"],
        "url": row["url"],
        "summary": row["summary"],
        "tags": json.loads(row["tags"]),
    }


def get_items(limit: int, offset: int):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM items
        ORDER BY published_at ASC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    ).fetchall()

    connection.close()

    return [row_to_item(row) for row in rows]


def get_item(item_id: str):
    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM items
        WHERE id = ?
        """,
        (item_id,),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return row_to_item(row)

def create_item(item_id, item):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO items (
            id,
            title,
            source_name,
            published_at,
            url,
            summary,
            tags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item_id,
            item["title"],
            item["source"]["name"],
            item["publishedAt"],
            item["url"],
            item["summary"],
            json.dumps(item["tags"]),
        ),
    )

    connection.commit()

    row = connection.execute(
        """
        SELECT *
        FROM items
        WHERE id = ?
        """,
        (item_id,),
    ).fetchone()

    connection.close()

    return row_to_item(row)

def update_item(item_id, updates):
    connection = get_connection()

    existing = connection.execute(
        """
        SELECT *
        FROM items
        WHERE id = ?
        """,
        (item_id,),
    ).fetchone()

    if existing is None:
        connection.close()
        return None

    if "title" in updates:
        connection.execute(
            "UPDATE items SET title = ? WHERE id = ?",
            (updates["title"], item_id),
        )

    if "source" in updates:
        connection.execute(
            "UPDATE items SET source_name = ? WHERE id = ?",
            (updates["source"]["name"], item_id),
        )

    if "publishedAt" in updates:
        connection.execute(
            "UPDATE items SET published_at = ? WHERE id = ?",
            (updates["publishedAt"], item_id),
        )

    if "url" in updates:
        connection.execute(
            "UPDATE items SET url = ? WHERE id = ?",
            (updates["url"], item_id),
        )

    if "summary" in updates:
        connection.execute(
            "UPDATE items SET summary = ? WHERE id = ?",
            (updates["summary"], item_id),
        )

    if "tags" in updates:
        connection.execute(
            "UPDATE items SET tags = ? WHERE id = ?",
            (json.dumps(updates["tags"]), item_id),
        )

    connection.commit()

    row = connection.execute(
        """
        SELECT *
        FROM items
        WHERE id = ?
        """,
        (item_id,),
    ).fetchone()

    connection.close()

    return row_to_item(row)

def delete_item(item_id):
    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM items
        WHERE id = ?
        """,
        (item_id,),
    )

    connection.commit()
    deleted = cursor.rowcount > 0

    connection.close()

    return deleted