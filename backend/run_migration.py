#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def run_migration():
    print('Adding summary and tasks columns to documents table...')

    try:
        with engine.connect() as conn:
            # Add summary column
            conn.execute(text('ALTER TABLE documents ADD COLUMN IF NOT EXISTS summary TEXT'))
            print('✅ Added summary column')
            
            # Add tasks column
            conn.execute(text('ALTER TABLE documents ADD COLUMN IF NOT EXISTS tasks JSONB'))
            print('✅ Added tasks column')
            
            # Commit the changes
            conn.commit()
            print('✅ Database migration completed successfully')
            
            # Verify columns exist
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'documents' 
                AND column_name IN ('summary', 'tasks')
            """))
            
            columns = result.fetchall()
            print(f'Verified columns: {columns}')
            
    except Exception as e:
        print(f'❌ Migration failed: {e}')

if __name__ == "__main__":
    run_migration()