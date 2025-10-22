"""
Database module for user management and sessions
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

class Database:
    def __init__(self, db_path: str = "videomusic.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # Sessions table (auth tokens)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # User API settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_api_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                suno_api_key TEXT,
                suno_base_url TEXT DEFAULT 'https://api.sunoapi.org',
                replicate_api_token TEXT,
                openai_api_key TEXT,
                openai_assistant_id TEXT DEFAULT 'asst_tR6OL8QLpSsDDlc6hKdBmVNU',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Generation sessions tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                style TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Create default admin user if not exists
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = ?", ("admin",))
        if cursor.fetchone()["count"] == 0:
            admin_password = "admin123"  # Change this in production!
            password_hash = self.hash_password(admin_password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_admin)
                VALUES (?, ?, ?, 1)
            """, ("admin", "admin@videomusic.local", password_hash))
            print(f"⚠️  Default admin user created: admin / {admin_password}")
            print("⚠️  PLEASE CHANGE THE PASSWORD IMMEDIATELY!")

        conn.commit()
        conn.close()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_token() -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(32)

    def create_user(self, username: str, email: str, password: str, is_admin: bool = False) -> Optional[int]:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            password_hash = self.hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, is_admin)
                VALUES (?, ?, ?, ?)
            """, (username, email, password_hash, is_admin))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return user_id
        except sqlite3.IntegrityError:
            return None

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        password_hash = self.hash_password(password)
        cursor.execute("""
            SELECT id, username, email, is_admin, is_active
            FROM users
            WHERE username = ? AND password_hash = ? AND is_active = 1
        """, (username, password_hash))

        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    def create_session(self, user_id: int, expires_hours: int = 24) -> str:
        """Create authentication session and return token"""
        conn = self.get_connection()
        cursor = conn.cursor()

        token = self.generate_token()
        expires_at = datetime.now() + timedelta(hours=expires_hours)

        cursor.execute("""
            INSERT INTO auth_sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, token, expires_at))

        conn.commit()
        conn.close()

        return token

    def validate_session(self, token: str) -> Optional[Dict]:
        """Validate session token and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.id, u.username, u.email, u.is_admin
            FROM auth_sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ? AND u.is_active = 1
        """, (token, datetime.now()))

        user = cursor.fetchone()
        conn.close()

        if user:
            return dict(user)
        return None

    def delete_session(self, token: str):
        """Delete (logout) a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM auth_sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM auth_sessions WHERE expires_at <= ?", (datetime.now(),))
        conn.commit()
        conn.close()

    def save_user_api_settings(self, user_id: int, settings: Dict):
        """Save or update user API settings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO user_api_settings (
                user_id, suno_api_key, suno_base_url,
                replicate_api_token, openai_api_key, openai_assistant_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                suno_api_key = excluded.suno_api_key,
                suno_base_url = excluded.suno_base_url,
                replicate_api_token = excluded.replicate_api_token,
                openai_api_key = excluded.openai_api_key,
                openai_assistant_id = excluded.openai_assistant_id,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user_id,
            settings.get('suno_api_key', ''),
            settings.get('suno_base_url', 'https://api.sunoapi.org'),
            settings.get('replicate_api_token', ''),
            settings.get('openai_api_key', ''),
            settings.get('openai_assistant_id', 'asst_tR6OL8QLpSsDDlc6hKdBmVNU')
        ))

        conn.commit()
        conn.close()

    def get_user_api_settings(self, user_id: int) -> Optional[Dict]:
        """Get user API settings"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT suno_api_key, suno_base_url, replicate_api_token,
                   openai_api_key, openai_assistant_id
            FROM user_api_settings
            WHERE user_id = ?
        """, (user_id,))

        settings = cursor.fetchone()
        conn.close()

        if settings:
            return dict(settings)
        return None

    def track_generation_session(self, user_id: int, session_id: str, title: str, style: str):
        """Track a generation session"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO generation_sessions (user_id, session_id, title, style)
            VALUES (?, ?, ?, ?)
        """, (user_id, session_id, title, style))

        conn.commit()
        conn.close()

    def update_generation_status(self, session_id: str, status: str):
        """Update generation session status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        completed_at = datetime.now() if status == 'completed' else None
        cursor.execute("""
            UPDATE generation_sessions
            SET status = ?, completed_at = ?
            WHERE session_id = ?
        """, (status, completed_at, session_id))

        conn.commit()
        conn.close()

    def get_user_sessions(self, user_id: int) -> List[Dict]:
        """Get all generation sessions for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT session_id, title, style, status, created_at, completed_at
            FROM generation_sessions
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))

        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return sessions

    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            password_hash = self.hash_password(new_password)
            cursor.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
            """, (password_hash, user_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
