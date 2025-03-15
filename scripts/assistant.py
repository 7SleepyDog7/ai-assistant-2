#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import sqlite3
import requests
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import uno
from com.sun.star.beans import PropertyValue

# Configuration (DO NOT EDIT THESE DIRECTLY)
SSD_ROOT = os.path.expanduser("/media/chris/T7 Shield/AI_Assistant")
CONFIG_KEY = os.getenv("CONFIG_KEY")  # Set in your .bashrc

class SecureConfig:
    """Encrypted configuration manager"""
    def __init__(self):
        self.cipher = Fernet(CONFIG_KEY)
        self.config_path = os.path.join(SSD_ROOT, "config/encrypted.cfg")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, "rb") as f:
                return json.loads(self.cipher.decrypt(f.read()).decode())
        except FileNotFoundError:
            return {"deepseek_key": "", "user_prefs": {}}

    def save_config(self):
        encrypted = self.cipher.encrypt(json.dumps(self.config).encode())
        with open(self.config_path, "wb") as f:
            f.write(encrypted)

class MemoryCore:
    """Persistent memory system"""
    def __init__(self):
        self.db_path = os.path.join(SSD_ROOT, "memory_db/memory.sqlite")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY,
                    timestamp DATETIME,
                    user_input TEXT,
                    response TEXT
                )""")

    def store_interaction(self, user_input: str, response: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO interactions (timestamp, user_input, response)
                VALUES (?, ?, ?)""", 
                (datetime.now(), user_input, response))

class RealTimeServices:
    """External services integration"""
    def __init__(self, config: SecureConfig):
        self.config = config
        self.thunderbird_profile = os.path.join(SSD_ROOT, "thunderbird_data/profile")

    def get_emails(self, limit: int = 5) -> list:
        try:
            mbox = mailbox.mbox(os.path.join(self.thunderbird_profile, "Inbox"))
            return [msg['subject'] for msg in mbox[:limit]]
        except Exception as e:
            return [f"Email error: {str(e)}"]

class LibreOfficeController:
    """LibreOffice automation"""
    def __init__(self):
        self.context = uno.getComponentContext()
        self.smgr = self.context.ServiceManager
        self.desktop = self.smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.context)
        self.doc_path = os.path.join(SSD_ROOT, "libreoffice_docs")

    def create_document(self, doc_type: str, content: str, filename: str) -> bool:
        try:
            doc = self.desktop.loadComponentFromURL(
                f"private:factory/{doc_type}", "_blank", 0, ())
            text = doc.Text
            cursor = text.createTextCursor()
            text.insertString(cursor, content, 0)
            full_path = os.path.join(self.doc_path, filename)
            doc.storeAsURL(f"file://{full_path}", ())
            return True
        except Exception as e:
            print(f"Office Error: {str(e)}")
            return False

class PersonalityEngine:
    """9S personality implementation"""
    def __init__(self):
        profile_path = os.path.join(SSD_ROOT, "config/personality.json")
        with open(profile_path) as f:
            self.profile = json.load(f)
            
    def format_response(self, text: str) -> str:
        if "error" in text.lower():
            return random.choice(self.profile['error']).format(error=text)
        return random.choice(self.profile['acknowledge']) + "\n" + text

class AICore:
    """Main AI system"""
    def __init__(self):
        self.config = SecureConfig()
        self.memory = MemoryCore()
        self.services = RealTimeServices(self.config)
        self.personality = PersonalityEngine()
        self.libre_office = LibreOfficeController()
        
        # Configure browser
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(
            executable_path="/usr/bin/geckodriver",
            options=options
        )

    def process_command(self, user_input: str) -> str:
        """Process user input"""
        try:
            # Get API response
            api_response = self._query_deepseek(user_input)
            
            # Execute command
            response_text = self._execute_action(api_response)
            
            # Store interaction
            self.memory.store_interaction(user_input, response_text)
            
            return self.personality.format_response(response_text)
            
        except Exception as e:
            return self.personality.format_response(f"System error: {str(e)}")

    def _query_deepseek(self, prompt: str) -> Dict[str, Any]:
        """Query DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.config.config['deepseek_key']}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )
        return json.loads(response.json()['choices'][0]['message']['content'])

    def _execute_action(self, command: Dict[str, Any]) -> str:
        """Execute validated command"""
        action = command["intent"]
        
        if action == "create_note":
            return self._create_note(
                command["parameters"]["content"],
                command["parameters"]["title"]
            )
        elif action == "create_document":
            success = self.libre_office.create_document(
                command["parameters"]["type"],
                command["parameters"]["content"],
                command["parameters"]["filename"]
            )
            return "Document created" if success else "Creation failed"
            
        return "Command executed"

    def _create_note(self, content: str, title: str) -> str:
        """Create Obsidian note"""
        note_path = os.path.join(SSD_ROOT, "obsidian_vault", f"{title}.md")
        try:
            with open(note_path, "w") as f:
                f.write(content)
            return f"Note '{title}' created"
        except Exception as e:
            return f"Note error: {str(e)}"

if __name__ == "__main__":
    ai = AICore()
    print("9S Online [Version 5.1]")
    print("Type 'exit' to end session\n")
    
    while True:
        try:
            user_input = input("User: ").strip()
            if user_input.lower() == "exit":
                break
                
            response = ai.process_command(user_input)
            print(f"\n9S: {response}\n")
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
