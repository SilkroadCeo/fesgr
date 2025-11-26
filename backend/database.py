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

        # Chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                profile_name TEXT NOT NULL,
                telegram_user_id INTEGER,
                last_read_message_id INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                is_from_user INTEGER DEFAULT 0,
                is_system INTEGER DEFAULT 0,
                text TEXT,
                file_url TEXT,
                file_type TEXT,
                file_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        """)

        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL,
                profile_id INTEGER NOT NULL,
                telegram_user_id INTEGER,
                amount REAL NOT NULL,
                bonus_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                crypto_type TEXT,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'unpaid',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
        """)

        # Comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                user_name TEXT DEFAULT 'Anonymous User',
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chats_profile_id
            ON chats(profile_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chats_telegram_user_id
            ON chats(telegram_user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_chat_id
            ON messages(chat_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_telegram_user_id
            ON orders(telegram_user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_status
            ON orders(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_comments_profile_id
            ON comments(profile_id)
        """)

        logger.info("✅ Database initialized successfully")


# ==================== USER MANAGEMENT ====================

def get_or_create_user(telegram_id: int, username: str = None,
                       first_name: str = None, last_name: str = None,
                       language_code: str = 'en', is_premium: bool = False) -> Dict[str, Any]:
    """
    Get existing user or create new one from Telegram data
    Returns user dictionary with id, telegram_id, etc.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Try to get existing user
        cursor.execute("""
            SELECT id, telegram_id, username, first_name, last_name,
                   language_code, is_premium, created_at, last_login
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
                    is_premium = ?
                WHERE telegram_id = ?
            """, (username, first_name, last_name, language_code,
                  1 if is_premium else 0, telegram_id))

            logger.info(f"✅ User logged in: {telegram_id} ({first_name} {last_name})")

            # Fetch updated user
            cursor.execute("""
                SELECT id, telegram_id, username, first_name, last_name,
                       language_code, is_premium, created_at, last_login
                FROM users
                WHERE telegram_id = ?
            """, (telegram_id,))
            user = cursor.fetchone()
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users (telegram_id, username, first_name, last_name,
                                   language_code, is_premium)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (telegram_id, username, first_name, last_name, language_code,
                  1 if is_premium else 0))

            user_id = cursor.lastrowid
            logger.info(f"✅ New user created: {telegram_id} ({first_name} {last_name})")

            # Fetch created user
            cursor.execute("""
                SELECT id, telegram_id, username, first_name, last_name,
                       language_code, is_premium, created_at, last_login
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
                   language_code, is_premium, created_at, last_login
            FROM users
            WHERE telegram_id = ?
        """, (telegram_id,))

        user = cursor.fetchone()
        return dict(user) if user else None


# ==================== FILE MANAGEMENT ====================

def add_file(user_id: int, telegram_user_id: int, filename: str,
             original_filename: str, file_path: str, file_size: int,
             mime_type: str) -> int:
    """Add file to database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO files (user_id, telegram_user_id, filename, original_filename,
                              file_path, file_size, mime_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, telegram_user_id, filename, original_filename,
              file_path, file_size, mime_type))

        file_id = cursor.lastrowid
        logger.info(f"✅ File added to database: {filename} (user_id: {user_id})")
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
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, telegram_user_id, filename, original_filename,
                   file_path, file_size, mime_type, uploaded_at
            FROM files
            WHERE id = ? AND telegram_user_id = ?
        """, (file_id, telegram_user_id))

        file = cursor.fetchone()
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
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if file exists and belongs to user
        cursor.execute("""
            SELECT file_path FROM files
            WHERE id = ? AND telegram_user_id = ?
        """, (file_id, telegram_user_id))

        file = cursor.fetchone()
        if not file:
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


# ==================== CHAT MANAGEMENT ====================

def create_chat(profile_id: int, profile_name: str, telegram_user_id: Optional[int] = None) -> Dict[str, Any]:
    """Create a new chat or return existing one"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if chat already exists
        if telegram_user_id:
            cursor.execute("""
                SELECT id, profile_id, profile_name, telegram_user_id,
                       last_read_message_id, created_at
                FROM chats
                WHERE profile_id = ? AND telegram_user_id = ?
            """, (profile_id, telegram_user_id))
        else:
            cursor.execute("""
                SELECT id, profile_id, profile_name, telegram_user_id,
                       last_read_message_id, created_at
                FROM chats
                WHERE profile_id = ? AND telegram_user_id IS NULL
            """, (profile_id,))

        chat = cursor.fetchone()

        if chat:
            return dict(chat)

        # Create new chat
        cursor.execute("""
            INSERT INTO chats (profile_id, profile_name, telegram_user_id)
            VALUES (?, ?, ?)
        """, (profile_id, profile_name, telegram_user_id))

        chat_id = cursor.lastrowid
        logger.info(f"✅ Chat created: profile_id={profile_id}, telegram_user_id={telegram_user_id}")

        # Fetch created chat
        cursor.execute("""
            SELECT id, profile_id, profile_name, telegram_user_id,
                   last_read_message_id, created_at
            FROM chats
            WHERE id = ?
        """, (chat_id,))

        return dict(cursor.fetchone())


def get_chat(profile_id: int, telegram_user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Get chat by profile_id and telegram_user_id"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if telegram_user_id:
            cursor.execute("""
                SELECT id, profile_id, profile_name, telegram_user_id,
                       last_read_message_id, created_at
                FROM chats
                WHERE profile_id = ? AND telegram_user_id = ?
            """, (profile_id, telegram_user_id))
        else:
            cursor.execute("""
                SELECT id, profile_id, profile_name, telegram_user_id,
                       last_read_message_id, created_at
                FROM chats
                WHERE profile_id = ? AND telegram_user_id IS NULL
            """, (profile_id,))

        chat = cursor.fetchone()
        return dict(chat) if chat else None


def get_user_chats(telegram_user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get all chats for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if telegram_user_id:
            cursor.execute("""
                SELECT id, profile_id, profile_name, telegram_user_id,
                       last_read_message_id, created_at
                FROM chats
                WHERE telegram_user_id = ?
                ORDER BY created_at DESC
            """, (telegram_user_id,))
        else:
            cursor.execute("""
                SELECT id, profile_id, profile_name, telegram_user_id,
                       last_read_message_id, created_at
                FROM chats
                WHERE telegram_user_id IS NULL
                ORDER BY created_at DESC
            """)

        chats = cursor.fetchall()
        return [dict(chat) for chat in chats]


def update_chat_last_read(chat_id: int, message_id: int) -> bool:
    """Update last read message ID for a chat"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chats
            SET last_read_message_id = ?
            WHERE id = ?
        """, (message_id, chat_id))
        return cursor.rowcount > 0


# ==================== MESSAGE MANAGEMENT ====================

def add_message(chat_id: int, text: Optional[str] = None, is_from_user: bool = True,
                is_system: bool = False, file_url: Optional[str] = None,
                file_type: Optional[str] = None, file_name: Optional[str] = None) -> int:
    """Add message to chat"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (chat_id, is_from_user, is_system, text,
                                 file_url, file_type, file_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, 1 if is_from_user else 0, 1 if is_system else 0,
              text, file_url, file_type, file_name))

        message_id = cursor.lastrowid
        logger.info(f"✅ Message added to chat {chat_id}")
        return message_id


def get_chat_messages(chat_id: int) -> List[Dict[str, Any]]:
    """Get all messages for a chat"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, chat_id, is_from_user, is_system, text,
                   file_url, file_type, file_name, created_at
            FROM messages
            WHERE chat_id = ?
            ORDER BY created_at ASC
        """, (chat_id,))

        messages = cursor.fetchall()
        return [dict(msg) for msg in messages]


def get_chat_messages_after(chat_id: int, after_message_id: int) -> List[Dict[str, Any]]:
    """Get messages after a specific message ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, chat_id, is_from_user, is_system, text,
                   file_url, file_type, file_name, created_at
            FROM messages
            WHERE chat_id = ? AND id > ?
            ORDER BY created_at ASC
        """, (chat_id, after_message_id))

        messages = cursor.fetchall()
        return [dict(msg) for msg in messages]


def get_last_message_id() -> int:
    """Get the highest message ID in database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) as max_id FROM messages")
        result = cursor.fetchone()
        return result['max_id'] if result['max_id'] else 0


# ==================== ORDER MANAGEMENT ====================

def create_order(order_number: str, profile_id: int, amount: float,
                bonus_amount: float, total_amount: float, crypto_type: str,
                currency: str = 'USD', telegram_user_id: Optional[int] = None,
                expires_at: Optional[str] = None) -> Dict[str, Any]:
    """Create a new order"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_number, profile_id, telegram_user_id, amount,
                               bonus_amount, total_amount, crypto_type, currency,
                               status, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'unpaid', ?)
        """, (order_number, profile_id, telegram_user_id, amount, bonus_amount,
              total_amount, crypto_type, currency, expires_at))

        order_id = cursor.lastrowid
        logger.info(f"✅ Order created: #{order_number}, amount=${total_amount}")

        # Fetch created order
        cursor.execute("""
            SELECT id, order_number, profile_id, telegram_user_id, amount,
                   bonus_amount, total_amount, crypto_type, currency, status,
                   created_at, expires_at
            FROM orders
            WHERE id = ?
        """, (order_id,))

        return dict(cursor.fetchone())


def get_order(profile_id: int, status: str, telegram_user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Get order by profile_id, status, and telegram_user_id"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if telegram_user_id:
            cursor.execute("""
                SELECT id, order_number, profile_id, telegram_user_id, amount,
                       bonus_amount, total_amount, crypto_type, currency, status,
                       created_at, expires_at
                FROM orders
                WHERE profile_id = ? AND status = ? AND telegram_user_id = ?
            """, (profile_id, status, telegram_user_id))
        else:
            cursor.execute("""
                SELECT id, order_number, profile_id, telegram_user_id, amount,
                       bonus_amount, total_amount, crypto_type, currency, status,
                       created_at, expires_at
                FROM orders
                WHERE profile_id = ? AND status = ? AND telegram_user_id IS NULL
            """, (profile_id, status))

        order = cursor.fetchone()
        return dict(order) if order else None


def get_user_orders(telegram_user_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get orders for a user, optionally filtered by status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        if telegram_user_id and status:
            cursor.execute("""
                SELECT id, order_number, profile_id, telegram_user_id, amount,
                       bonus_amount, total_amount, crypto_type, currency, status,
                       created_at, expires_at
                FROM orders
                WHERE telegram_user_id = ? AND status = ?
                ORDER BY created_at DESC
            """, (telegram_user_id, status))
        elif telegram_user_id:
            cursor.execute("""
                SELECT id, order_number, profile_id, telegram_user_id, amount,
                       bonus_amount, total_amount, crypto_type, currency, status,
                       created_at, expires_at
                FROM orders
                WHERE telegram_user_id = ?
                ORDER BY created_at DESC
            """, (telegram_user_id,))
        elif status:
            cursor.execute("""
                SELECT id, order_number, profile_id, telegram_user_id, amount,
                       bonus_amount, total_amount, crypto_type, currency, status,
                       created_at, expires_at
                FROM orders
                WHERE telegram_user_id IS NULL AND status = ?
                ORDER BY created_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, order_number, profile_id, telegram_user_id, amount,
                       bonus_amount, total_amount, crypto_type, currency, status,
                       created_at, expires_at
                FROM orders
                WHERE telegram_user_id IS NULL
                ORDER BY created_at DESC
            """)

        orders = cursor.fetchall()
        return [dict(order) for order in orders]


def update_order(order_id: int, amount: float, bonus_amount: float,
                total_amount: float, crypto_type: str, currency: str,
                expires_at: Optional[str] = None) -> bool:
    """Update an existing order"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE orders
            SET amount = ?, bonus_amount = ?, total_amount = ?,
                crypto_type = ?, currency = ?, expires_at = ?
            WHERE id = ?
        """, (amount, bonus_amount, total_amount, crypto_type, currency,
              expires_at, order_id))
        return cursor.rowcount > 0


def delete_order(order_id: int) -> bool:
    """Delete an order"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        return cursor.rowcount > 0


def delete_expired_orders(cutoff_time: str) -> int:
    """Delete expired unpaid orders before cutoff_time"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM orders
            WHERE status = 'unpaid' AND expires_at < ?
        """, (cutoff_time,))
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            logger.info(f"🗑️ Deleted {deleted_count} expired orders")
        return deleted_count


# ==================== COMMENT MANAGEMENT ====================

def add_comment(profile_id: int, text: str, user_name: str = 'Anonymous User') -> int:
    """Add a comment to a profile"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (profile_id, user_name, text)
            VALUES (?, ?, ?)
        """, (profile_id, user_name, text))

        comment_id = cursor.lastrowid
        logger.info(f"✅ Comment added to profile {profile_id}")
        return comment_id


def get_profile_comments(profile_id: int) -> List[Dict[str, Any]]:
    """Get all comments for a profile"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, profile_id, user_name, text, created_at
            FROM comments
            WHERE profile_id = ?
            ORDER BY created_at DESC
        """, (profile_id,))

        comments = cursor.fetchall()
        return [dict(comment) for comment in comments]


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

        cursor.execute("SELECT COUNT(*) as count FROM chats")
        chat_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM messages")
        message_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM orders")
        order_count = cursor.fetchone()['count']

        cursor.execute("SELECT COUNT(*) as count FROM comments")
        comment_count = cursor.fetchone()['count']

        return {
            'total_users': user_count,
            'total_files': file_count,
            'total_storage_bytes': total_size,
            'total_storage_mb': round(total_size / (1024 * 1024), 2),
            'total_chats': chat_count,
            'total_messages': message_count,
            'total_orders': order_count,
            'total_comments': comment_count
        }


# Initialize database on module import
if not os.path.exists(DATABASE_PATH):
    logger.info("📦 Creating new database...")
    init_database()
else:
    logger.info("✅ Database already exists")
