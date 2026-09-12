"""Unit tests for SQLite database operations."""

import os
import tempfile
import unittest
from app.database.database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        """Create temporary test database file."""
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix=".db")
        self.db = DatabaseManager(db_path=self.temp_path)

    def tearDown(self):
        """Close and remove temporary database."""
        os.close(self.temp_fd)
        if os.path.exists(self.temp_path):
            try:
                os.remove(self.temp_path)
            except Exception:
                pass

    def test_milestone_seeding(self):
        """Default database must initialize with the 6 core milestones."""
        milestones = self.db.get_all_milestones()
        self.assertEqual(len(milestones), 6)
        completed, total = self.db.get_journey_progress()
        self.assertEqual(total, 6)
        self.assertEqual(completed, 3) # First 3 completed by default

    def test_compatibility_save_and_retrieve(self):
        """Saving compatibility results and retrieving latest record."""
        row_id = self.db.save_compatibility_result("Alex", "Sam", 85, 92, 88)
        self.assertGreater(row_id, 0)
        
        latest = self.db.get_latest_compatibility()
        self.assertIsNotNone(latest)
        self.assertEqual(latest["name1"], "Alex")
        self.assertEqual(latest["name2"], "Sam")
        self.assertEqual(latest["combined_score"], 88)

    def test_milestone_crud(self):
        """Full milestone CRUD lifecycle."""
        # Add
        mid = self.db.add_milestone("First Trip", "Went to the beach", "2026-06-15", "Great sunset", completed=0)
        self.assertGreater(mid, 0)
        
        # Toggle
        self.db.toggle_milestone(mid)
        milestones = {m["id"]: m for m in self.db.get_all_milestones()}
        self.assertEqual(milestones[mid]["completed"], 1)
        
        # Update
        self.db.update_milestone(mid, "First Beach Trip", "Updated description", "2026-06-16", "Fun notes", 1)
        updated = {m["id"]: m for m in self.db.get_all_milestones()}[mid]
        self.assertEqual(updated["title"], "First Beach Trip")
        
        # Delete
        self.db.delete_milestone(mid)
        remaining = [m["id"] for m in self.db.get_all_milestones()]
        self.assertNotIn(mid, remaining)

    def test_ai_history(self):
        """Logging AI prompts and clearing."""
        self.db.save_ai_history("advisor", "Test situation", "Step 1: Talk")
        history = self.db.get_ai_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["feature_type"], "advisor")
        
        self.db.clear_ai_history()
        history_after = self.db.get_ai_history()
        self.assertEqual(len(history_after), 0)

if __name__ == "__main__":
    unittest.main()
