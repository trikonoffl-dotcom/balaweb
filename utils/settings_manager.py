import json
import os

# Default settings matching the current hardcoded values
DEFAULT_SETTINGS = {
    "id_card": {
        "first_name_pos": [14.8, 148],
        "last_name_pos": [15.0, 163],
        "title_pos": [15.5, 183],
        "doj_pos": [15.1, 196],
        "id_number_pos": [15.6, 226],
        "photo_pos": [11, 35.2],
        "photo_size": [95, 98],
        "template_path": "Name_Trikon.pdf"
    },
    "business_card": {
        "templates": {
            "Modern Blue": "modern_blue.pdf",
            "Classic White": "classic_white.pdf"
        },
        "font_size_name": 14,
        "font_size_title": 9,
        "font_size_details": 8
    },
    "welcome_aboard": {
        "template_path": "welcome aboard - Without name.pdf",
        "first_name_pos": [563, 500],
        "last_name_pos": [563, 580],
        "title_pos": [563, 640],
        "date_pos": [563, 700],
        "photo_rect": [71, 340, 421.978, 502.045, 28.492]
    },
    "auto_crop": {
        "id_card": {
            "target_ratio": 1.15,
            "top_headroom": 0.5,
            "bottom_extension": 1.2
        },
        "welcome": {
            "target_ratio": 0.8,
            "top_headroom": 0.3,
            "bottom_extension": 0.3
        }
    }
}

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json")

def load_settings():
    """Loads settings from JSON, fallback to defaults if not exists."""
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Saves settings to JSON."""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def get_setting(category, key=None):
    """Utility to get a specific setting."""
    settings = load_settings()
    cat = settings.get(category, DEFAULT_SETTINGS.get(category, {}))
    if key:
        return cat.get(key, DEFAULT_SETTINGS.get(category, {}).get(key))
    return cat

def resolve_asset_path(path, category="template"):
    """
    Resolves a path/filename to an absolute path.
    Checks inside 'Templates' or 'fonts' directories if not absolute.
    """
    if not path:
        return None
    
    # If absolute or already exists, return as is
    if os.path.isabs(path) and os.path.exists(path):
        return path
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Search locations based on category
    search_dirs = []
    if category == "template":
        search_dirs = [
            os.path.join(base_dir, "Templates"),
            os.path.join(base_dir, "Templates", "idcard"),
            os.path.join(base_dir, "Templates", "businesscard")
        ]
    elif category == "font":
        search_dirs = [
            os.path.join(base_dir, "fonts"),
            os.path.join(base_dir, "fonts", "Rubik", "static")
        ]
        
    # Check if path is just a filename in one of the search dirs
    filename = os.path.basename(path)
    for d in search_dirs:
        test_path = os.path.join(d, filename)
        if os.path.exists(test_path):
            return test_path
            
    # Fallback to local path check
    if os.path.exists(path):
        return os.path.abspath(path)
        
    return None
