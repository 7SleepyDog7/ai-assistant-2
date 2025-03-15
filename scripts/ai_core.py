#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import hashlib
import requests
from pathlib import Path

# Configuration
SSD_ROOT = Path("/media/chris/T7 Shield/AI_Assistant")
REPO_URL = "https://github.com/7SleepyDog7/ai-assistant-2/blob/main/.gitignore"  # ← CHANGE THIS

class SelfManagingAI:
    def __init__(self):
        self.required_dirs = {
            SSD_ROOT: ["config", "scripts", "memory_db", 
                      "obsidian_vault", "libreoffice_docs", 
                      "thunderbird_data/profile"]
        }
        self.required_files = {
            SSD_ROOT/"config/personality.json": {
                "content": {
                    "response_templates": {
                        "acknowledge": ["Roger that..."],
                        "error": ["System error..."]
                    }
                }
            }
        }

    def setup_environment(self):
        try:
            for base, dirs in self.required_dirs.items():
                for d in dirs:
                    (base/d).mkdir(parents=True, exist_ok=True)
            for path, content in self.required_files.items():
                if not path.exists():
                    with open(path, 'w') as f:
                        json.dump(content["content"], f, indent=2)
            return True
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            return False

    def self_update(self):
        try:
            with open(__file__, 'rb') as f:
                current_content = f.read()
            current_hash = hashlib.sha256(current_content).hexdigest()
            
            new_script = requests.get(f"{REPO_URL}/scripts/ai_core.py").content
            new_hash = hashlib.sha256(new_script).hexdigest()

            if new_hash != current_hash:
                with open(__file__, 'wb') as f:
                    f.write(new_script)
                print("Update successful. Restarting...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            return True
        except Exception as e:
            print(f"Update failed: {str(e)}")
            return False

    def run(self):
        if self.setup_environment() and self.self_update():
            print("9S System Ready")
            while True:
                try:
                    user_input = input("\nUser: ").strip()
                    if user_input.lower() == "exit":
                        break
                    print(f"9S: Processing '{user_input}'")
                except KeyboardInterrupt:
                    print("\nShutting down...")
                    break

if __name__ == "__main__":
    SelfManagingAI().run()
