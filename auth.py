# auth.py
import json
import os
import hashlib
import base64
from datetime import datetime
import streamlit as st
import sqlite3

class AuthSystem:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table with additional fields
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME,
            preferences TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = "melodai_salt_2024"  # In production, use a unique salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def register_user(self, name, email, password):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                st.error("Email already exists. Please use a different email or login.")
                return False
            
            # Validate inputs
            if not name or not email or not password:
                st.error("All fields are required.")
                return False
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters long.")
                return False
            
            # Add new user
            cursor.execute(
                "INSERT INTO users (email, name, password) VALUES (?, ?, ?)",
                (email, name.strip(), self._hash_password(password))
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except sqlite3.Error as e:
            st.error(f"Error creating account: {str(e)}")
            return False
    
    def login_user(self, email, password):
        """Authenticate user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT name FROM users WHERE email = ? AND password = ?",
                (email, self._hash_password(password))
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # Update last login time
                self._update_last_login(email)
                return result[0]  # Return user's name
            return None
            
        except sqlite3.Error:
            return None
    
    def _update_last_login(self, email):
        """Update last login timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE email = ?",
                (email,)
            )
            
            conn.commit()
            conn.close()
        except sqlite3.Error:
            pass
    
    def change_password(self, email, current_password, new_password):
        """Change user password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verify current password
            cursor.execute(
                "SELECT id FROM users WHERE email = ? AND password = ?",
                (email, self._hash_password(current_password))
            )
            
            if cursor.fetchone():
                # Update password
                cursor.execute(
                    "UPDATE users SET password = ? WHERE email = ?",
                    (self._hash_password(new_password), email)
                )
                
                conn.commit()
                conn.close()
                return True
                
            conn.close()
            return False
            
        except sqlite3.Error:
            return False
    
    def get_user_data(self, email):
        """Get user data by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT name, email, created_at, last_login, preferences FROM users WHERE email = ?",
                (email,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'name': result[0],
                    'email': result[1],
                    'created_at': result[2],
                    'last_login': result[3],
                    'preferences': json.loads(result[4]) if result[4] else {}
                }
            return {}
            
        except sqlite3.Error:
            return {}
    
    def update_user_data(self, email, updates):
        """Update user data (name, preferences, etc.)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if 'name' in updates:
                cursor.execute(
                    "UPDATE users SET name = ? WHERE email = ?",
                    (updates['name'], email)
                )
            
            if 'preferences' in updates:
                cursor.execute(
                    "UPDATE users SET preferences = ? WHERE email = ?",
                    (json.dumps(updates['preferences']), email)
                )
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error:
            return False

class UserHistory:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced history table with more fields
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            input_text TEXT NOT NULL,
            mood_analysis TEXT NOT NULL,
            music_params TEXT NOT NULL,
            audio_data BLOB,
            generation_time REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            favorite BOOLEAN DEFAULT 0,
            play_count INTEGER DEFAULT 0,
            last_played DATETIME,
            tags TEXT,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_generation(self, user_email, input_text, mood_analysis, music_params, audio_data, generation_time, tags=None):
        """Save generation with enhanced metadata"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO user_history (user_email, input_text, mood_analysis, music_params, audio_data, generation_time, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_email,
                input_text,
                json.dumps(mood_analysis),
                json.dumps(music_params),
                audio_data,
                generation_time,
                json.dumps(tags) if tags else None
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            st.error(f"Error saving history: {str(e)}")
            return False
    
    def get_user_history(self, user_email, limit=100):
        """Get user history with enhanced data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT input_text, mood_analysis, music_params, audio_data, generation_time, timestamp, favorite, play_count, tags
            FROM user_history 
            WHERE user_email = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
            ''', (user_email, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    'input_text': row[0],
                    'mood_analysis': json.loads(row[1]),
                    'music_params': json.loads(row[2]),
                    'audio_data': row[3],
                    'generation_time': row[4],
                    'timestamp': row[5],
                    'favorite': bool(row[6]),
                    'play_count': row[7],
                    'tags': json.loads(row[8]) if row[8] else []
                })
            
            return history
            
        except sqlite3.Error:
            return []
    
    def delete_entry(self, user_email, timestamp):
        """Delete a specific history entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            DELETE FROM user_history 
            WHERE user_email = ? AND timestamp = ?
            ''', (user_email, timestamp))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error:
            return False
    
    def mark_as_favorite(self, user_email, timestamp, favorite=True):
        """Mark an entry as favorite"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE user_history 
            SET favorite = ? 
            WHERE user_email = ? AND timestamp = ?
            ''', (favorite, user_email, timestamp))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error:
            return False
    
    def increment_play_count(self, user_email, timestamp):
        """Increment play count and update last played timestamp"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE user_history 
            SET play_count = play_count + 1, last_played = CURRENT_TIMESTAMP
            WHERE user_email = ? AND timestamp = ?
            ''', (user_email, timestamp))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error:
            return False
    
    def add_tags(self, user_email, timestamp, tags):
        """Add tags to a history entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get existing tags
            cursor.execute('SELECT tags FROM user_history WHERE user_email = ? AND timestamp = ?', 
                          (user_email, timestamp))
            result = cursor.fetchone()
            
            existing_tags = json.loads(result[0]) if result and result[0] else []
            updated_tags = list(set(existing_tags + tags))
            
            cursor.execute('''
            UPDATE user_history 
            SET tags = ? 
            WHERE user_email = ? AND timestamp = ?
            ''', (json.dumps(updated_tags), user_email, timestamp))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error:
            return False