#!/usr/bin/env python3
"""
Database migration script to add missing columns
"""

import sqlite3
import logging
from pathlib import Path
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Add missing columns to the database"""
    # Extract database path from DATABASE_URL
    db_path = config.DATABASE_URL.replace('sqlite:///', '')
    
    if not Path(db_path).exists():
        logger.error(f"Database file not found: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_notification_sent' not in columns:
            logger.info("Adding last_notification_sent column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN last_notification_sent DATETIME
            """)
            conn.commit()
            logger.info("Column added successfully!")
        else:
            logger.info("Column last_notification_sent already exists.")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting database migration...")
    if migrate_database():
        logger.info("Migration completed successfully!")
    else:
        logger.error("Migration failed!") 