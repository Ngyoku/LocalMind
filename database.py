import sqlite3
from datetime import datetime

from config import DATABASE_DIR, DATABASE_PATH


def get_connection():
    """Crée une connexion à SQLite."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Active les relations entre tables
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Crée les tables si elles n'existent pas."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'Nouvelle conversation',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE
        )
    """)

    connection.commit()
    connection.close()


def create_conversation(title="Nouvelle conversation"):
    """Crée une nouvelle conversation."""

    now = datetime.now().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO conversations (title, created_at, updated_at)
        VALUES (?, ?, ?)
    """, (title, now, now))

    conversation_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return get_conversation(conversation_id)


def get_conversations():
    """Retourne toutes les conversations."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM conversations
        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_conversation(conversation_id):
    """Retourne une conversation."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM conversations
        WHERE id = ?
    """, (conversation_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return dict(row)


def get_messages(conversation_id):
    """Retourne les messages d'une conversation."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id ASC
    """, (conversation_id,))

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def add_message(conversation_id, role, content):
    """Ajoute un message à une conversation."""

    if role not in ("user", "assistant"):
        raise ValueError("Le rôle doit être 'user' ou 'assistant'.")

    now = datetime.now().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (
            conversation_id,
            role,
            content,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        conversation_id,
        role,
        content,
        now
    ))

    cursor.execute("""
        UPDATE conversations
        SET updated_at = ?
        WHERE id = ?
    """, (now, conversation_id))

    message_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return message_id


def update_conversation_title(conversation_id, title):
    """Modifie le titre d'une conversation."""

    now = datetime.now().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE conversations
        SET title = ?, updated_at = ?
        WHERE id = ?
    """, (
        title,
        now,
        conversation_id
    ))

    connection.commit()
    connection.close()


def delete_conversation(conversation_id):
    """Supprime une conversation et ses messages."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM conversations
        WHERE id = ?
    """, (conversation_id,))

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    return deleted > 0