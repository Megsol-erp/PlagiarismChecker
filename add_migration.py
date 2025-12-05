#!/usr/bin/env python
"""Add video_recording_path column to exam_sessions table"""

from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='exam_sessions' 
            AND column_name='video_recording_path'
        """))
        
        if result.fetchone() is None:
            # Add the column
            db.session.execute(text("""
                ALTER TABLE exam_sessions 
                ADD COLUMN video_recording_path VARCHAR(500)
            """))
            db.session.commit()
            print("✅ Column 'video_recording_path' added successfully!")
        else:
            print("ℹ️  Column 'video_recording_path' already exists")
            
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
