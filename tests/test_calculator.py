"""Unit tests for deterministic calculator and compatibility analyzer."""

import unittest
from app.core.calculator import (
    calculate_name_score,
    calculate_interest_score,
    calculate_combined_score,
    get_match_verdict
)
from app.core.compatibility import CompatibilityAnalyzer
from app.core.validation import validate_names, validate_interests

class TestCompatibilityCalculator(unittest.TestCase):

    def test_deterministic_scoring(self):
        """Identical inputs must produce the exact same score."""
        score1 = calculate_name_score("Alex", "Sam")
        score2 = calculate_name_score("Alex", "Sam")
        self.assertEqual(score1, score2)
        
    def test_order_independence(self):
        """Order of names should not affect compatibility result."""
        score_ab = calculate_name_score("Jordan", "Taylor")
        score_ba = calculate_name_score("Taylor", "Jordan")
        self.assertEqual(score_ab, score_ba)

    def test_score_range(self):
        """Scores must stay within 50% to 100% bound."""
        test_pairs = [
            ("Alice", "Bob"),
            ("Charlie", "David"),
            ("Emma", "Liam"),
            ("Sophia", "Noah"),
            ("A", "B")
        ]
        for n1, n2 in test_pairs:
            s = calculate_name_score(n1, n2)
            self.assertGreaterEqual(s, 50)
            self.assertLessEqual(s, 100)

    def test_interest_scoring(self):
        """More shared interests yield higher scores within bounds."""
        s0 = calculate_interest_score([])
        s1 = calculate_interest_score(["Music"])
        s4 = calculate_interest_score(["Music", "Movies", "Gaming", "Coding"])
        
        self.assertGreaterEqual(s1, s0)
        self.assertGreaterEqual(s4, s1)
        self.assertLessEqual(s4, 100)

    def test_validation_empty_names(self):
        """Empty names should fail validation."""
        v1, err1, _ = validate_names("", "Sam")
        self.assertFalse(v1)
        
        v2, err2, _ = validate_names("Alex", "   ")
        self.assertFalse(v2)

    def test_compatibility_analyzer_service(self):
        """Full analyzer produces valid result dictionary with required disclaimer."""
        success, err, res = CompatibilityAnalyzer.analyze("Alex", "Sam", ["Music", "Gaming"])
        self.assertTrue(success)
        self.assertIn("combined_score", res)
        self.assertIn("name_score", res)
        self.assertIn("interest_score", res)
        self.assertIn("disclaimer", res)
        self.assertTrue(len(res["disclaimer"]) > 10)

if __name__ == "__main__":
    unittest.main()
