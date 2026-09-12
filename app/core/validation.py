"""Input validation and sanitization utilities for LoveAI."""

import os
from pathlib import Path
from typing import Tuple, Optional, List

SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def validate_names(name1: str, name2: str) -> Tuple[bool, str, Tuple[str, str]]:
    """Validate two person names for compatibility checking.
    
    Returns:
        (is_valid, error_message, (sanitized_name1, sanitized_name2))
    """
    clean1 = name1.strip()
    clean2 = name2.strip()
    
    if not clean1:
        return False, "Please enter your name.", ("", "")
    if not clean2:
        return False, "Please enter the other person's name.", ("", "")
        
    if len(clean1) > 50:
        return False, "First name must be under 50 characters.", ("", "")
    if len(clean2) > 50:
        return False, "Second name must be under 50 characters.", ("", "")
        
    return True, "", (clean1, clean2)


def validate_interests(interests: List[str]) -> List[str]:
    """Clean and deduplicate list of interest tags."""
    cleaned = []
    seen = set()
    for item in interests:
        tag = item.strip()
        if tag and tag.lower() not in seen and len(tag) <= 100:
            seen.add(tag.lower())
            cleaned.append(tag)
    return cleaned


def validate_situation_text(text: str) -> Tuple[bool, str, str]:
    """Validate user situation description for AI Advisor."""
    clean = text.strip()
    if not clean:
        return False, "Please provide a brief description of your situation.", ""
    if len(clean) < 10:
        return False, "Please provide a bit more context (at least 10 characters).", ""
    if len(clean) > 2000:
        return False, "Situation description is too long (maximum 2000 characters).", ""
    return True, "", clean


def validate_message_text(text: str) -> Tuple[bool, str, str]:
    """Validate draft message for Message Assistant."""
    clean = text.strip()
    if not clean:
        return False, "Please enter a message to analyze or improve.", ""
    if len(clean) > 1000:
        return False, "Message is too long (maximum 1000 characters).", ""
    return True, "", clean


def validate_image_file(file_path: str) -> Tuple[bool, str]:
    """Validate that a file exists and has a supported image extension."""
    if not file_path or not os.path.exists(file_path):
        return False, "File does not exist."
        
    path = Path(file_path)
    if not path.is_file():
        return False, "Selected path is not a valid file."
        
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        return False, f"Unsupported format. Please choose: {', '.join(SUPPORTED_IMAGE_EXTENSIONS)}"
        
    # Check file size limit (e.g. max 20MB)
    try:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > 25:
            return False, "Image file size exceeds 25MB limit."
    except Exception as e:
        return False, f"Could not inspect file: {e}"
        
    return True, ""
