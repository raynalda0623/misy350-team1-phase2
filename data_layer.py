import json
from pathlib import Path

# data layer - handles loading and saving json files

def load_data(json_path):
    if json_path.exists():
        with open(json_path, "r") as f:
            data = json.load(f)
        return data
    else:
        return []

def save_data(json_path, data):
    with open(json_path, "w") as f:
        json.dump(data, f, indent=2)