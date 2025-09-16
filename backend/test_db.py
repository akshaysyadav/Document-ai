#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, init_db
from app.models import Document
from sqlalchemy import text

def test_database():
    print("Testing database connection...")
    
    try:
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connected successfully")
            print(f"PostgreSQL version: {version}")
        
        # Test session
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = result.fetchone()[0]
            print(f"✅ Session working, found {table_count} tables")
            
            # Check if our tables exist
            result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('documents', 'document_pages', 'text_chunks')"))
            tables = [row[0] for row in result.fetchall()]
            print(f"Our tables: {tables}")
            
            if 'documents' not in tables:
                print("⚠️  Documents table doesn't exist, creating tables...")
                init_db()
                print("✅ Tables created successfully")
            
            # Test documents query
            documents = db.query(Document).limit(5).all()
            print(f"✅ Found {len(documents)} documents in database")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_database()