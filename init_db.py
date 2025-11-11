#!/usr/bin/env python3
"""
Database initialization script for SQLite
Creates all necessary tables and inserts default data
"""
import sqlite3
import os
import logging
from config import DATABASE_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize SQLite database"""
    db_path = DATABASE_CONFIG['database']
    
    # Check if database already exists
    db_exists = os.path.exists(db_path)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        logger.info(f"Connected to database: {db_path}")
        
        # Read and execute SQL script
        with open('init_database_sqlite.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # Execute SQL script
        cursor.executescript(sql_script)
        conn.commit()
        
        logger.info("Database initialization completed successfully!")
        
        # Display table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        logger.info(f"Created tables: {[table[0] for table in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == '__main__':
    init_database()

