"""Deterministic compatibility scoring algorithms for LoveAI."""

import hashlib
from typing import List, Dict, Any
from app.config import COMPATIBILITY_DISCLAIMER

def calculate_name_score(name1: str, name2: str) -> int:
    """Calculates a deterministic name compatibility percentage.
    
    The score is order-independent: calculate_name_score(A, B) == calculate_name_score(B, A).
    Deterministic: identical names will always produce the identical score.
    Range: 55% to 97%.
    """
    n1 = name1.strip().lower()
    n2 = name2.strip().lower()
    
    # Sort so order doesn't matter
    pair_key = "::".join(sorted([n1, n2]))
    
    # Generate deterministic hash
    hash_bytes = hashlib.sha256(pair_key.encode("utf-8")).digest()
    hash_int = int.from_bytes(hash_bytes[:4], byteorder="big")
    
    # Letter overlap bonus
    letters1 = set(n1)
    letters2 = set(n2)
    common_letters = letters1.intersection(letters2)
    overlap_factor = len(common_letters) * 2
    
    # Map into range [55, 96]
    base_score = 55 + (hash_int % 38)
    final_score = min(97, max(52, base_score + (overlap_factor % 5)))
    return final_score


def calculate_interest_score(interests: List[str]) -> int:
    """Calculates an interest alignment score based on selected shared interests.
    
    Range: 50% to 98%.
    """
    if not interests:
        return 65  # Default baseline for neutral interest input
        
    count = len(interests)
    
    # Deduce a deterministic hash of sorted interests for nuanced flavor
    sorted_interests = sorted([i.strip().lower() for i in interests])
    key = "||".join(sorted_interests)
    hash_val = int(hashlib.md5(key.encode("utf-8")).hexdigest()[:4], 16)
    variance = hash_val % 7  # small 0-6 variance
    
    if count == 1:
        base = 72
    elif count == 2:
        base = 80
    elif count == 3:
        base = 86
    elif count == 4:
        base = 91
    else:
        base = 94
        
    return min(98, base + variance)


def calculate_combined_score(name_score: int, interest_score: int) -> int:
    """Calculates weighted combined entertainment score."""
    # 40% Name, 60% Interests
    combined = round(name_score * 0.40 + interest_score * 0.60)
    return max(50, min(99, combined))


def get_match_verdict(score: int) -> Dict[str, str]:
    """Provides categorized feedback based on the score."""
    if score >= 90:
        return {
            "title": "Cosmic പൊരുത്തം! 💕",
            "description": "അടിപൊളി പൊരുത്തം! നിങ്ങളുടെ vibes-ഉം താല്പര്യങ്ങളും തമ്മിൽ നല്ല matching ആണ്."
        }
    elif score >= 82:
        return {
            "title": "നല്ല പൊരുത്തം! ✨",
            "description": "നല്ല connection സാധ്യതയുണ്ട്! സംസാരിക്കാൻ നല്ല താല്പര്യങ്ങളും ലഭിക്കും."
        }
    elif score >= 72:
        return {
            "title": "നല്ല Connection! 🌟",
            "description": "നല്ലൊരു തുടക്കമാണ്, ഒരുമിച്ച് കൂടുതൽ താല്പര്യങ്ങൾ കണ്ടെത്താൻ കഴിയും."
        }
    elif score >= 62:
        return {
            "title": "നല്ല Dynamic! 💫",
            "description": "ചില സാമ്യങ്ങളും വ്യത്യാസങ്ങളുമുണ്ട്, അത് സംസാരം കൂടുതൽ രസകരമാക്കും."
        }
    else:
        return {
            "title": "വ്യത്യസ്തമായ Contrast! ⚡",
            "description": "Opposites attract എന്ന് പറയും പോലെ! നിങ്ങളുടെ വ്യത്യാസങ്ങൾ പുതിയ അനുഭവങ്ങൾ നൽകും."
        }
