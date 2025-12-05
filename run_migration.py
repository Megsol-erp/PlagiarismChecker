"""
Simple migration script to add candidate application fields
"""
import psycopg2
from config import Config

def migrate():
    try:
        # Connect directly to database
        conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='phone'
        """)
        
        if not cursor.fetchone():
            print("Adding new columns to users table...")
            
            # Add application fields
            cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20)")
            cursor.execute("ALTER TABLE users ADD COLUMN position_applied VARCHAR(200)")
            cursor.execute("ALTER TABLE users ADD COLUMN qualification VARCHAR(200)")
            cursor.execute("ALTER TABLE users ADD COLUMN experience_years INTEGER")
            cursor.execute("ALTER TABLE users ADD COLUMN current_organization VARCHAR(200)")
            cursor.execute("ALTER TABLE users ADD COLUMN linkedin_url VARCHAR(255)")
            cursor.execute("ALTER TABLE users ADD COLUMN portfolio_url VARCHAR(255)")
            cursor.execute("ALTER TABLE users ADD COLUMN assigned_exam_id INTEGER REFERENCES exams(id)")
            
            # Make password_hash nullable for candidates who apply through form
            cursor.execute("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL")
            
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
            
        cursor.close()
        conn.close()
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == '__main__':
    migrate()
