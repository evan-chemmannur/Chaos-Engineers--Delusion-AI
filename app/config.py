"""Application configuration and constants for LoveAI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
ASSETS_DIR = BASE_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "loveai.db"

# Ensure runtime directories exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
ICONS_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()

# App Branding
APP_NAME = "LoveAI"
APP_VERSION = "1.0.0"
APP_TAGLINE = "മനസ്സിലാക്കുക. സംസാരിക്കുക. ബന്ധപ്പെടുക. 💕"
WINDOW_TITLE = f"{APP_NAME} — {APP_TAGLINE}"
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 720

# Disclaimers (Required by PRD Sections 3.1, 3.2, and 22)
COMPATIBILITY_DISCLAIMER = (
    "പൊരുത്തം scores entertainment-ന് വേണ്ടി മാത്രമാണ്. ഇത് ഒരിക്കലും "
    "relationship success-ഓ മറ്റുള്ളവരുടെ മനസ്സോ തീരുമാനിക്കുന്നില്ല."
)

IMAGE_DISCLAIMER = (
    "ഈ feature ചിത്രങ്ങളുടെ visual സാമ്യം മാത്രമേ നോക്കുന്നുള്ളൂ. "
    "ഇത് ആളെ തിരിച്ചറിയുന്നതോ, പ്രണയമോ attraction-ഓ കണക്കാക്കുന്നതോ അല്ല."
)

GENERAL_DISCLAIMER = (
    "LoveAI ഒരു entertainment & communication-support ആപ്പ് മാത്രമാണ്. "
    "AI-generated ഉപദേശം മാർഗ്ഗനിർദ്ദേശം മാത്രമാണ്, മറ്റുള്ളവരുടെ മനസ്സോ "
    "തീരുമാനങ്ങളോ ഇത് പ്രവചിക്കുന്നില്ല. Always respect consent and boundaries."
)

# AI Options
RELATIONSHIP_STATUSES = [
    "Stranger",
    "Classmate",
    "Acquaintance",
    "Friend",
    "Close Friend",
    "Already talking",
]

COMMUNICATION_FREQUENCIES = [
    "Rarely",
    "Sometimes",
    "Often",
    "Daily",
]

DEFAULT_INTERESTS = [
    "Music",
    "Movies",
    "Gaming",
    "Coding",
    "Books",
    "Travel",
    "Fitness",
    "Art",
    "Photography",
    "Food",
]

ADVISOR_GOALS = [
    "Start talking",
    "Become better friends",
    "Spend more time together",
    "Ask them to hang out",
    "Express feelings",
    "Ask them on a date",
    "Improve an existing relationship",
]

MESSAGE_TONES = [
    "Casual",
    "Friendly",
    "Funny",
    "Confident",
    "Sweet",
    "Direct",
    "Short",
]

DEFAULT_MILESTONES = [
    ("ആദ്യത്തെ സംസാരം", "Ice break ചെയ്ത് ആദ്യമായി സംസാരിച്ചു.", 1),
    ("സുഹൃത്തുക്കളായി", "പൊതുവായ വിഷയങ്ങൾ സംസാരിച്ച് നല്ല friends ആയി.", 1),
    ("തുടർച്ചയായി സംസാരിച്ചു തുടങ്ങി", "ദിവസവും messages-ഉം casual check-ins-ഉം തുടങ്ങി.", 1),
    ("ആദ്യത്തെ Hangout", "കോളേജ്/ജോലിക്ക് പുറത്ത് ആദ്യമായി ഒരുമിച്ച് സമയം ചിലവഴിച്ചു.", 0),
    ("ഇഷ്ടം തുറന്നു പറഞ്ഞു", "മനസ്സിലുള്ള താല്പര്യം തുറന്നു പറഞ്ഞു.", 0),
    ("Date-ന് ക്ഷണിച്ചു", "ഒരുമിച്ച് പുറത്ത് പോകാനായി ക്ഷണിച്ചു.", 0),
]

