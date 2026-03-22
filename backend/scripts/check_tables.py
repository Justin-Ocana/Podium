import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'team%'")
tables = [row[0] for row in cursor.fetchall()]
print("Tablas de teams:", tables)
