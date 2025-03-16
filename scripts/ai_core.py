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
REPO_URL = "https://raw.githubusercontent.com/7SleepyDog7/ai-assistant-2/main/scripts"

class SelfManagingAI:
    def __init__(self):
        self.required_dirs = {
            SSD_ROOT: [
                "config", 
                "scripts", 
                "memory_db", 
                "obsidian_vault", 
                "libreoffice_docs", 
                "thunderbird_data/profile"
            ]
        }
        self.required_files = {
            SSD_ROOT/"config/personality.json": {
                "content": {
                    "response_templates": {
                        "acknowledge": [
                            "Roger that. Initiating protocol.",
                            "Analyzing request parameters..."
                        ],
                        "error": [
                            "System destabilization detected.",
                            "YorHa protocol violation"
                        ]
                    }
                }
            }
        }

    def setup_environment(self):
        """Create directory structure and default files"""
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
        """Update script from repository"""
        try:
            with open(__file__, 'rb') as f:
                current_content = f.read()
            current_hash = hashlib.sha256(current_content).hexdigest()
            
            response = requests.get(f"{REPO_URL}/ai_core.py")
            response.raise_for_status()
            new_script = response.content
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
        """Main execution loop"""
        if self.setup_environment() and self.self_update():
            print("9S System Ready [Version 5.1]")
            while True:
                try:
                    user_input = input("\nUser: ").strip()
                    if user_input.lower() == "exit":
                        break
                    print(f"9S: Processing '{user_input}'")
                except KeyboardInterrupt:
                    print("\nEmergency shutdown initiated")
                    break

if __name__ == "__main__":
    SelfManagingAI().run()
