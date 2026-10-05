"""
Database setup and verification utility for JobFlow.
Connects to MySQL, creates the database if not present, and applies table migrations/schemas.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', 3306))
DB_NAME = os.environ.get('DB_NAME', 'jobflow_db')


def setup_mysql_database():
    print("=" * 60)
    print(" JobFlow — Database Setup & Verification")
    print("=" * 60)
    print(f"Target Host: {DB_HOST}:{DB_PORT}")
    print(f"Target User: {DB_USER}")
    print(f"Database:    {DB_NAME}")
    print("-" * 60)

    try:
        import pymysql
        print("[1/3] Connecting to MySQL server...")
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            charset='utf8mb4'
        )
        print("  [OK] Connected to MySQL server successfully!")

        with conn.cursor() as cursor:
            print(f"[2/3] Ensuring database '{DB_NAME}' exists...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"  [OK] Database '{DB_NAME}' created or already exists.")
        conn.close()

        print("[3/3] Applying database migrations via Flask-Migrate (flask db upgrade)...")
        from app import create_app
        from flask_migrate import upgrade as migrate_upgrade
        flask_app = create_app('development')
        with flask_app.app_context():
            migrate_upgrade()
            print("  [OK] Database schema up to date via migrations (users, applications, interviews, followups, notes)!")

        print("-" * 60)
        print(" SUCCESS: Database setup completed without errors.")
        print(" You can now run the application with: python run.py")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n[!] MySQL Connection Failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure MySQL is running on your machine.")
        print("2. Check DB_PASSWORD in your .env file matches your MySQL root password.")
        print("3. Alternatively, you can use SQLite by setting in .env:")
        print("   DATABASE_URL=sqlite:///jobflow_dev.db\n")
        return False


if __name__ == '__main__':
    success = setup_mysql_database()
    if not success:
        sys.exit(1)
