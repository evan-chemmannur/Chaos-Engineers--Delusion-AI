"""High-level compatibility analyzer service."""

from typing import List, Dict, Any, Tuple
from app.core.validation import validate_names, validate_interests
from app.core.calculator import (
    calculate_name_score,
    calculate_interest_score,
    calculate_combined_score,
    get_match_verdict,
)
from app.config import COMPATIBILITY_DISCLAIMER

class CompatibilityAnalyzer:
    """Encapsulates compatibility analysis calculations and formatting."""
    
    @staticmethod
    def analyze(name1: str, name2: str, interests: List[str]) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates inputs and calculates deterministic compatibility metrics.
        
        Returns:
            (success, error_message, result_dict)
        """
        valid, err, sanitized_names = validate_names(name1, name2)
        if not valid:
            return False, err, {}
            
        clean_name1, clean_name2 = sanitized_names
        clean_interests = validate_interests(interests)
        
        name_score = calculate_name_score(clean_name1, clean_name2)
        interest_score = calculate_interest_score(clean_interests)
        combined_score = calculate_combined_score(name_score, interest_score)
        verdict = get_match_verdict(combined_score)
        
        result = {
            "name1": clean_name1,
            "name2": clean_name2,
            "interests": clean_interests,
            "name_score": name_score,
            "interest_score": interest_score,
            "combined_score": combined_score,
            "verdict_title": verdict["title"],
            "verdict_description": verdict["description"],
            "disclaimer": COMPATIBILITY_DISCLAIMER,
        }
        
        return True, "", result
