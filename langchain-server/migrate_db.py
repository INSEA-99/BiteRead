"""
Database migration script to add new columns to articles table

This script adds VOA-related fields to the existing articles table.
"""

import sqlite3

def migrate_database():
    """Add new columns to articles table for VOA content"""
    conn = sqlite3.connect('biteread.db')
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(articles)")
    columns = [row[1] for row in cursor.fetchall()]

    # Add new columns if they don't exist
    new_columns = {
        'difficulty': 'VARCHAR(50)',
        'category': 'VARCHAR(100)',
        'source_url': 'VARCHAR(1000)',
        'vocabulary': 'JSON',
        'questions': 'JSON',
        'published_date': 'DATETIME'
    }

    for column_name, column_type in new_columns.items():
        if column_name not in columns:
            try:
                cursor.execute(f'ALTER TABLE articles ADD COLUMN {column_name} {column_type}')
                print(f'✓ Added column: {column_name}')
            except sqlite3.OperationalError as e:
                print(f'✗ Error adding {column_name}: {e}')
        else:
            print(f'○ Column already exists: {column_name}')

    conn.commit()
    conn.close()
    print('\n✓ Database migration completed!')

if __name__ == '__main__':
    migrate_database()
