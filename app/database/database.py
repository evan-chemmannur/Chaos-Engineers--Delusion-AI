"""SQLite persistence layer for LoveAI."""

import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.config import DATABASE_PATH, DEFAULT_MILESTONES

class DatabaseManager:
    """Manages SQLite database interactions with parameterized queries."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or DATABASE_PATH)
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a database connection with dictionary row access."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Creates tables if they do not exist and populates initial milestone templates."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. compatibility_results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compatibility_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name1 TEXT NOT NULL,
                    name2 TEXT NOT NULL,
                    name_score INTEGER NOT NULL,
                    interest_score INTEGER NOT NULL,
                    combined_score INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. journey_milestones table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS journey_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    completed INTEGER DEFAULT 0,
                    event_date TEXT DEFAULT '',
                    notes TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 3. ai_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feature_type TEXT NOT NULL,
                    input_summary TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if default milestones exist; if empty, seed them
            cursor.execute("SELECT COUNT(*) as count FROM journey_milestones")
            count = cursor.fetchone()["count"]
            if count == 0:
                today = datetime.now().strftime("%Y-%m-%d")
                for title, desc, completed in DEFAULT_MILESTONES:
                    cursor.execute("""
                        INSERT INTO journey_milestones (title, description, completed, event_date, notes)
                        VALUES (?, ?, ?, ?, ?)
                    """, (title, desc, completed, today, "Sample initial milestone."))
                    
            conn.commit()

    # ---------------- Compatibility Operations ---------------- #

    def save_compatibility_result(
        self, name1: str, name2: str, name_score: int, interest_score: int, combined_score: int
    ) -> int:
        """Saves a compatibility check record and returns the record ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO compatibility_results (name1, name2, name_score, interest_score, combined_score)
                VALUES (?, ?, ?, ?, ?)
            """, (name1, name2, name_score, interest_score, combined_score))
            conn.commit()
            return cursor.lastrowid

    def get_latest_compatibility(self) -> Optional[Dict[str, Any]]:
        """Fetches the most recently recorded compatibility calculation."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM compatibility_results
                ORDER BY id DESC LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_compatibility(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetches recent compatibility calculations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM compatibility_results
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # ---------------- Journey Milestones Operations ---------------- #

    def get_all_milestones(self) -> List[Dict[str, Any]]:
        """Returns all journey milestones ordered by id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM journey_milestones ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]

    def add_milestone(
        self, title: str, description: str = "", event_date: str = "", notes: str = "", completed: int = 0
    ) -> int:
        """Adds a new custom relationship milestone."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO journey_milestones (title, description, event_date, notes, completed)
                VALUES (?, ?, ?, ?, ?)
            """, (title.strip(), description.strip(), event_date.strip(), notes.strip(), 1 if completed else 0))
            conn.commit()
            return cursor.lastrowid

    def update_milestone(
        self, milestone_id: int, title: str, description: str, event_date: str, notes: str, completed: int
    ) -> bool:
        """Updates an existing milestone."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE journey_milestones
                SET title = ?, description = ?, event_date = ?, notes = ?, completed = ?
                WHERE id = ?
            """, (title.strip(), description.strip(), event_date.strip(), notes.strip(), 1 if completed else 0, milestone_id))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_milestone(self, milestone_id: int) -> bool:
        """Toggles the completion status of a milestone."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE journey_milestones
                SET completed = CASE WHEN completed = 1 THEN 0 ELSE 1 END
                WHERE id = ?
            """, (milestone_id,))
            conn.commit()
            return cursor.rowcount > 0

    def delete_milestone(self, milestone_id: int) -> bool:
        """Deletes a milestone by id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM journey_milestones WHERE id = ?", (milestone_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_journey_progress(self) -> Tuple[int, int]:
        """Returns (completed_milestones, total_milestones)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total FROM journey_milestones")
            total = cursor.fetchone()["total"]
            cursor.execute("SELECT COUNT(*) as completed FROM journey_milestones WHERE completed = 1")
            completed = cursor.fetchone()["completed"]
            return completed, total

    # ---------------- AI History Operations ---------------- #

    def save_ai_history(self, feature_type: str, input_summary: str, response: str) -> int:
        """Logs an AI prompt and response."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ai_history (feature_type, input_summary, response)
                VALUES (?, ?, ?)
            """, (feature_type, input_summary, response))
            conn.commit()
            return cursor.lastrowid

    def get_ai_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent AI interaction history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ai_history
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def clear_ai_history(self) -> None:
        """Clears all logged AI interactions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_history")
            conn.commit()

    def clear_all_data(self) -> None:
        """Wipes all data across tables for privacy/testing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM compatibility_results")
            cursor.execute("DELETE FROM journey_milestones")
            cursor.execute("DELETE FROM ai_history")
            conn.commit()
        self.init_db()

# Singleton DB instance
db = DatabaseManager()
