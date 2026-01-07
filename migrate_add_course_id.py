#!/usr/bin/env python3
"""
Migration: Add course_id column to attendance table
"""
from sqlalchemy import create_engine, text
from config import Config

# Create database connection
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

print("=" * 60)
print("Adding course_id column to attendance table")
print("=" * 60)

with engine.connect() as conn:
    try:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='attendance' AND column_name='course_id'
        """))

        if result.fetchone():
            print("\n✓ course_id column already exists!")
        else:
            print("\nAdding course_id column...")

            # Add the column
            conn.execute(text("""
                ALTER TABLE attendance
                ADD COLUMN course_id INTEGER REFERENCES courses(id)
            """))

            conn.commit()
            print("✓ Successfully added course_id column!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        raise

print("\n" + "=" * 60)
print("Migration complete!")
print("=" * 60)
