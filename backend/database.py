"""
Database management for Telegram Mini App File Management System
Handles user authentication, file storage, and user data isolation
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(current_dir, "app_database.db")


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_database():
    """Initialize database with schema"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT DEFAULT 'en',
                is_premium INTEGER DEFAULT 0,
                user_type TEXT DEFAULT 'telegram' CHECK(user_type IN ('telegram', 'web')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                telegram_user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_user_id
            ON files(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_files_telegram_user_id
            ON files(telegram_user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_telegram_id
            ON users(telegram_id)
        """)

        # Profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                avatar TEXT,
                bio TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_profiles_user_id
            ON profiles(user_id)
        """)

        logger.info("✅ Database initialized successfully")


# ==================== USER MANAGEMENT ====================

def get_or_create_user(telegram_id: int, username: str = None,
                       first_name: str = None, last_name: str = None,
                       language_code: str = 'en', is_premium: bool = False,
                       user_type: str = 'telegram') -> Dict[str, Any]:
    """
    Get existing user or create new one from Telegram data
    Returns user dictionary with id, telegram_id, etc.

    Security: Validates telegram_id to prevent invalid data
    """
    # SECURITY: Validate telegram_id format
    if not isinstance(telegram_id, int) or telegram_id <= 0:
        raise ValueError(f"Invalid telegram_id: {telegram_id}. Must be a positive integer.")

    # Validate user_type
    if user_type not in ('telegram', 'web'):
        raise ValueError(f"Invalid user_type: {user_type}. Must be 'telegram' or 'web'.")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Try to get existing user
        cursor.execute("""
            SELECT id, telegram_id, username, first_name, last_name,
                   language_code, is_premium, user_type, created_at, last_login
            FROM users
            WHERE telegram_id = ?
        """, (telegram_id,))

        user = cursor.fetchone()

        if user:
            # Update last login and user info
            cursor.execute("""
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP,
                    username = ?,
                    first_name = ?,
                    last_name = ?,
                    language_code = ?,
                    is_premium = ?,
                    user_type = ?
                WHERE telegram_id = ?
            """, (username, first_name, last_name, language_code,
                  1 if is_premium else 0, user_type, telegram_id))

            logger.info(f"✅ User logged in: {telegram_id} ({first_name} {last_name})")

            # Fetch updated user
            cursor.execute("""
                SELECT id, telegram_id, username, first_name, last_name,
                       language_code, is_premium, user_type, created_at, last_login
                FROM users
                WHERE telegram_id = ?
            """, (telegram_id,))
            user = cursor.fetchone()
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name,
                                   language_code, is_premium, user_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (telegram_id, username, first_name, last_name, language_code,
                  1 if is_premium else 0, user_type))

            user_id = cursor.lastrowid
            logger.info(f"✅ New user created: {telegram_id} ({first_name} {last_name})")

            # Create profile for new user
            cursor.execute("""
                INSERT INTO profiles (user_id, bio)
                VALUES (?, ?)
            """, (user_id, ''))
            logger.info(f"✅ Profile created for user_id: {user_id}")

            # Fetch created user
            cursor.execute("""
                SELECT id, telegram_id, username, first_name, last_name,
                       language_code, is_premium, user_type, created_at, last_login
                FROM users
                WHERE id = ?
            """, (user_id,))
            user = cursor.fetchone()

        return dict(user)


def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by Telegram ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, telegram_id, username, first_name, last_name,
                   language_code, is_premium, user_type, created_at, last_login
            FROM users
            WHERE telegram_id = ?
        """, (telegram_id,))

        user = cursor.fetchone()
        return dict(user) if user else None


# ==================== FILE MANAGEMENT ====================

def add_file(user_id: int, telegram_user_id: int, filename: str,
             original_filename: str, file_path: str, file_size: int,
             mime_type: str) -> int:
    """
    Add file to database with ownership validation

    Security: Validates that user_id corresponds to telegram_user_id
    """
    # SECURITY: Validate inputs
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")

    if not isinstance(telegram_user_id, int) or telegram_user_id <= 0:
        raise ValueError(f"Invalid telegram_user_id: {telegram_user_id}")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # SECURITY: Verify user_id belongs to telegram_user_id
        cursor.execute("""
            SELECT telegram_id FROM users WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

        if not user:
            raise ValueError(f"User ID {user_id} not found")

        if user['telegram_id'] != telegram_user_id:
            raise ValueError(
                f"User ID mismatch: user_id {user_id} has telegram_id {user['telegram_id']}, "
                f"but {telegram_user_id} was provided"
            )

        cursor.execute("""
            INSERT INTO files (user_id, telegram_user_id, filename, original_filename,
                              file_path, file_size, mime_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, telegram_user_id, filename, original_filename,
              file_path, file_size, mime_type))

        file_id = cursor.lastrowid
        logger.info(f"✅ File added to database: {filename} (user_id: {user_id}, telegram_id: {telegram_user_id})")
        return file_id


def get_user_files(telegram_user_id: int) -> List[Dict[str, Any]]:
    """Get all files for a specific user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, original_filename, file_path, file_size,
                   mime_type, uploaded_at
            FROM files
            WHERE telegram_user_id = ?
            ORDER BY uploaded_at DESC
        """, (telegram_user_id,))

        files = cursor.fetchall()
        return [dict(file) for file in files]


def get_file_by_id(file_id: int, telegram_user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get file by ID with ownership verification
    Returns None if file doesn't exist or doesn't belong to user

    Security: Critical function for preventing unauthorized file access
    """
    # SECURITY: Validate inputs
    if not isinstance(telegram_user_id, int) or telegram_user_id <= 0:
        logger.error(f"Invalid telegram_user_id in get_file_by_id: {telegram_user_id}")
        return None

    if not isinstance(file_id, int) or file_id <= 0:
        logger.error(f"Invalid file_id in get_file_by_id: {file_id}")
        return None

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, telegram_user_id, filename, original_filename,
                   file_path, file_size, mime_type, uploaded_at
            FROM files
            WHERE id = ? AND telegram_user_id = ?
        """, (file_id, telegram_user_id))

        file = cursor.fetchone()

        # SECURITY: Log access attempts for auditing
        if file:
            logger.debug(f"File {file_id} accessed by telegram_user_id {telegram_user_id}")
        else:
            logger.warning(f"Unauthorized file access attempt: file_id={file_id}, telegram_user_id={telegram_user_id}")

        return dict(file) if file else None


def get_file_by_filename(filename: str, telegram_user_id: int) -> Optional[Dict[str, Any]]:
    """Get file by filename with ownership verification"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, telegram_user_id, filename, original_filename,
                   file_path, file_size, mime_type, uploaded_at
            FROM files
            WHERE filename = ? AND telegram_user_id = ?
        """, (filename, telegram_user_id))

        file = cursor.fetchone()
        return dict(file) if file else None


def delete_file(file_id: int, telegram_user_id: int) -> bool:
    """
    Delete file with ownership verification
    Returns True if deleted, False if not found or unauthorized

    Security: Critical function for preventing unauthorized file deletion
    """
    # SECURITY: Validate inputs
    if not isinstance(telegram_user_id, int) or telegram_user_id <= 0:
        logger.error(f"Invalid telegram_user_id in delete_file: {telegram_user_id}")
        return False

    if not isinstance(file_id, int) or file_id <= 0:
        logger.error(f"Invalid file_id in delete_file: {file_id}")
        return False

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # SECURITY: Check if file exists and belongs to user
        cursor.execute("""
            SELECT file_path FROM files
            WHERE id = ? AND telegram_user_id = ?
        """, (file_id, telegram_user_id))

        file = cursor.fetchone()
        if not file:
            logger.warning(f"Unauthorized delete attempt: file_id={file_id}, telegram_user_id={telegram_user_id}")
            return False

        file_path = file['file_path']

        # Delete from database
        cursor.execute("""
            DELETE FROM files
            WHERE id = ? AND telegram_user_id = ?
        """, (file_id, telegram_user_id))

        # Delete physical file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"✅ File deleted: {file_path}")
            except Exception as e:
                logger.error(f"❌ Error deleting file: {e}")

        return cursor.rowcount > 0


def delete_file_by_filename(filename: str, telegram_user_id: int) -> bool:
    """Delete file by filename with ownership verification"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get file info
        cursor.execute("""
            SELECT id, file_path FROM files
            WHERE filename = ? AND telegram_user_id = ?
        """, (filename, telegram_user_id))

        file = cursor.fetchone()
        if not file:
            return False

        file_path = file['file_path']

        # Delete from database
        cursor.execute("""
            DELETE FROM files
            WHERE filename = ? AND telegram_user_id = ?
        """, (filename, telegram_user_id))

        # Delete physical file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"✅ File deleted: {file_path}")
            except Exception as e:
                logger.error(f"❌ Error deleting file: {e}")

        return cursor.rowcount > 0


def get_user_storage_stats(telegram_user_id: int) -> Dict[str, Any]:
    """Get storage statistics for user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) as file_count,
                COALESCE(SUM(file_size), 0) as total_size
            FROM files
            WHERE telegram_user_id = ?
        """, (telegram_user_id,))

        stats = cursor.fetchone()
        return {
            'file_count': stats['file_count'],
            'total_size': stats['total_size'],
            'total_size_mb': round(stats['total_size'] / (1024 * 1024), 2)
        }


# ==================== UTILITY FUNCTIONS ====================

def get_database_stats() -> Dict[str, Any]:
    """Get overall database statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM files")
        file_count = cursor.fetchone()['count']

        cursor.execute("SELECT COALESCE(SUM(file_size), 0) as total FROM files")
        total_size = cursor.fetchone()['total']

        return {
            'total_users': user_count,
            'total_files': file_count,
            'total_storage_bytes': total_size,
            'total_storage_mb': round(total_size / (1024 * 1024), 2)
        }


# ==================== PROFILE MANAGEMENT ====================

def get_or_create_profile(user_id: int) -> Dict[str, Any]:
    """
    Get existing profile or create new one for user
    Returns profile dictionary with id, user_id, avatar, bio
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}. Must be a positive integer.")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Try to get existing profile
        cursor.execute("""
            SELECT id, user_id, avatar, bio, created_at, updated_at
            FROM profiles
            WHERE user_id = ?
        """, (user_id,))

        profile = cursor.fetchone()

        if not profile:
            # Create new profile
            cursor.execute("""
                INSERT INTO profiles (user_id, bio)
                VALUES (?, ?)
            """, (user_id, ''))

            profile_id = cursor.lastrowid
            logger.info(f"✅ Profile created for user_id: {user_id}")

            # Fetch created profile
            cursor.execute("""
                SELECT id, user_id, avatar, bio, created_at, updated_at
                FROM profiles
                WHERE id = ?
            """, (profile_id,))
            profile = cursor.fetchone()

        return dict(profile) if profile else None


def update_profile(user_id: int, avatar: str = None, bio: str = None) -> bool:
    """
    Update user profile
    Returns True if updated, False otherwise
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}. Must be a positive integer.")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Build update query dynamically based on provided fields
        update_fields = []
        params = []

        if avatar is not None:
            update_fields.append("avatar = ?")
            params.append(avatar)

        if bio is not None:
            update_fields.append("bio = ?")
            params.append(bio)

        if not update_fields:
            return False

        # Always update updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)

        query = f"""
            UPDATE profiles
            SET {', '.join(update_fields)}
            WHERE user_id = ?
        """

        cursor.execute(query, params)

        if cursor.rowcount > 0:
            logger.info(f"✅ Profile updated for user_id: {user_id}")
            return True

        return False


def get_profile_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get profile by user ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, avatar, bio, created_at, updated_at
            FROM profiles
            WHERE user_id = ?
        """, (user_id,))

        profile = cursor.fetchone()
        return dict(profile) if profile else None


# Initialize database on module import
if not os.path.exists(DATABASE_PATH):
    logger.info("📦 Creating new database...")
    init_database()
else:
    logger.info("✅ Database already exists")
