"""
Migration script to add candidate application fields to User model
Run this script to update the database schema
"""
from app import create_app
from models import db
from sqlalchemy import text

def migrate():
    app = create_app()
    with app.app_context():
        try:
            # Add new columns to users table
            with db.engine.connect() as conn:
                # Check if columns exist before adding
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='users' AND column_name='phone'
                """))
                
                if not result.fetchone():
                    print("Adding new columns to users table...")
                    
                    # Add application fields
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20)"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN position_applied VARCHAR(200)"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN qualification VARCHAR(200)"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN experience_years INTEGER"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN current_organization VARCHAR(200)"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN linkedin_url VARCHAR(255)"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN portfolio_url VARCHAR(255)"))
                    conn.execute(text("ALTER TABLE users ADD COLUMN assigned_exam_id INTEGER REFERENCES exams(id)"))
                    
                    # Make password_hash nullable for candidates who apply through form
                    conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL"))
                    
                    conn.commit()
                    
                    print("✅ Migration completed successfully!")
                    print("New columns added:")
                    print("  - phone")
                    print("  - position_applied")
                    print("  - qualification")
                    print("  - experience_years")
                    print("  - current_organization")
                    print("  - linkedin_url")
                    print("  - portfolio_url")
                    print("  - assigned_exam_id")
                    print("\n✅ password_hash is now nullable")
                else:
                    print("✅ Columns already exist. No migration needed.")
                    
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
