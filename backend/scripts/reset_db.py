"""
Script to reset the database and migrations for Podium project.
This is needed when switching to a custom User model.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def reset_database():
    """Drop all tables and reset migrations."""
    print("🔄 Resetting database...")
    
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Found {len(tables)} tables to drop")
            
            # Drop all tables
            for table in tables:
                table_name = table[0]
                print(f"  ❌ Dropping table: {table_name}")
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
            
            connection.commit()
            print("✅ All tables dropped successfully")
        else:
            print("ℹ️  No tables found")
    
    print("\n🔄 Running migrations...")
    call_command('migrate', verbosity=2)
    print("\n✅ Database reset complete!")

if __name__ == '__main__':
    confirm = input("⚠️  This will DELETE ALL DATA in the database. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("❌ Operation cancelled")
