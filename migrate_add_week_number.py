#!/usr/bin/env python3
"""
Database migration script to add week_number column to attendance table
"""

import sys
from sqlalchemy import text
from database import engine, get_db

def migrate():
    """Add week_number column to attendance table"""
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='attendance' AND column_name='week_number';
            """))
            
            if result.fetchone():
                print("✓ Column 'week_number' already exists in attendance table")
                return True
            
            # Add the column
            print("Adding week_number column to attendance table...")
            conn.execute(text("""
                ALTER TABLE attendance 
                ADD COLUMN week_number INTEGER;
            """))
            conn.commit()
            
            print("✓ Successfully added week_number column to attendance table")
            return True
            
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Database Migration: Add week_number to attendance table")
    print("=" * 60)
    
    success = migrate()
    
    if success:
        print("\n✓ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Migration failed!")
        sys.exit(1)
