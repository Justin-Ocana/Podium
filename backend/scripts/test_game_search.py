"""
Quick test script for game search functionality.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.teams.rawg_service import rawg_service

print("🎮 Testing game search...")
print("-" * 50)

# Test search
query = "left"
print(f"\n🔍 Searching for: '{query}'")
results = rawg_service.search_games(query, page_size=5)

if results and 'results' in results:
    print(f"✅ Found {results['count']} games:")
    for game in results['results']:
        print(f"  - {game['name']} (ID: {game['id']})")
else:
    print("❌ No results found")

print("\n" + "-" * 50)
print("✨ Test complete!")
