#!/usr/bin/env python3
"""
Database connection and operation module
Provides database connection, query, update and other basic functions
"""
import sqlite3
from contextlib import contextmanager
import logging
from config import DATABASE_CONFIG

logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Get database connection
    """
    try:
        connection = sqlite3.connect(
            DATABASE_CONFIG['database'],
            timeout=DATABASE_CONFIG['timeout'],
            check_same_thread=DATABASE_CONFIG['check_same_thread']
        )
        # Enable foreign keys
        connection.execute("PRAGMA foreign_keys = ON")
        # Return rows as dictionaries
        connection.row_factory = sqlite3.Row
        logger.info("Database connection successful")
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def close_db_connection(connection):
    """
    Close database connection
    """
    try:
        if connection:
            connection.close()
            logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Failed to close database connection: {e}")

@contextmanager
def get_db_cursor():
    """
    Get database cursor context manager
    """
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        yield cursor, connection
    except Exception as e:
        if connection:
            connection.rollback()
            logger.error(f"Database operation failed, rolled back: {e}")
        raise
    finally:
        if connection:
            close_db_connection(connection)

def execute_query(sql, params=None):
    """
    Execute query statement
    """
    try:
        with get_db_cursor() as (cursor, connection):
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            # Convert sqlite3.Row to dict
            result = [dict(row) for row in result]
            logger.info(f"Query executed successfully, returned {len(result)} records")
            return result
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise

def execute_query_one(sql, params=None):
    """
    Execute query statement, return one record
    """
    try:
        with get_db_cursor() as (cursor, connection):
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchone()
            # Convert sqlite3.Row to dict
            result = dict(result) if result else None
            logger.info(f"Query executed successfully, returned one record")
            return result
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise

def execute_update(sql, params=None):
    """
    Execute update statement (INSERT, UPDATE, DELETE)
    """
    try:
        with get_db_cursor() as (cursor, connection):
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            connection.commit()
            affected_rows = cursor.rowcount
            logger.info(f"Update executed successfully, affected {affected_rows} rows")
            return affected_rows
    except Exception as e:
        logger.error(f"Update execution failed: {e}")
        raise

def execute_insert(sql, params=None):
    """
    Execute insert statement, return the ID of the newly inserted record
    """
    try:
        with get_db_cursor() as (cursor, connection):
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            connection.commit()
            new_id = cursor.lastrowid
            logger.info(f"Insert executed successfully, new record ID: {new_id}")
            return new_id
    except Exception as e:
        logger.error(f"Insert execution failed: {e}")
        raise

def execute_batch_insert(sql, params_list):
    """
    Execute batch insert
    """
    try:
        with get_db_cursor() as (cursor, connection):
            cursor.executemany(sql, params_list)
            connection.commit()
            affected_rows = cursor.rowcount
            logger.info(f"Batch insert executed successfully, affected {affected_rows} rows")
            return affected_rows
    except Exception as e:
        logger.error(f"Batch insert execution failed: {e}")
        raise

def test_connection():
    """
    Test database connection
    """
    try:
        result = execute_query("SELECT 1 as test")
        if result and result[0]['test'] == 1:
            logger.info("Database connection test successful")
            return True
        else:
            logger.error("Database connection test failed")
            return False
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def get_table_info(table_name):
    """
    Get table information
    """
    try:
        sql = f"PRAGMA table_info({table_name})"
        result = execute_query(sql)
        logger.info(f"Get table {table_name} information successful")
        return result
    except Exception as e:
        logger.error(f"Get table {table_name} information failed: {e}")
        raise

def check_table_exists(table_name):
    """
    Check if table exists
    """
    try:
        sql = """
        SELECT COUNT(*) as count
        FROM sqlite_master
        WHERE type='table' AND name=?
        """
        result = execute_query_one(sql, (table_name,))
        exists = result['count'] > 0 if result else False
        logger.info(f"Table {table_name} {'exists' if exists else 'does not exist'}")
        return exists
    except Exception as e:
        logger.error(f"Check if table {table_name} exists failed: {e}")
        raise