"""
Script to populate Testuser with random gaming profile data.

Usage:
    python scripts/populate_testuser.py
"""

import os
import sys
import django
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User


def populate_testuser():
    """Populate TestXD with random gaming profile data."""
    
    try:
        user = User.objects.get(username='TestXD')
    except User.DoesNotExist:
        print("❌ User 'TestXD' not found. Please create it first.")
        return
    
    # Random data pools
    bios = [
        "Competitive gamer with 5+ years of experience in FPS and MOBA games. Always looking for new challenges!",
        "Esports enthusiast and tournament organizer. Passionate about building the competitive gaming community.",
        "Professional player specializing in tactical shooters. Former semi-pro, now focusing on team management.",
        "Casual competitive player who loves strategy games. Available for scrims and tournaments on weekends.",
        "Veteran gamer with experience across multiple titles. Team captain and shot-caller.",
    ]
    
    countries = [
        "United States",
        "Canada",
        "United Kingdom",
        "Germany",
        "France",
        "Spain",
        "Brazil",
        "Mexico",
        "Australia",
        "Japan",
        "South Korea",
        "Sweden",
    ]
    
    regions = {
        "United States": ["California", "Texas", "New York", "Florida", "Illinois"],
        "Canada": ["Ontario", "Quebec", "British Columbia", "Alberta"],
        "United Kingdom": ["England", "Scotland", "Wales", "Northern Ireland"],
        "Germany": ["Bavaria", "Berlin", "Hamburg", "Saxony"],
        "France": ["Île-de-France", "Provence", "Brittany", "Normandy"],
        "Spain": ["Madrid", "Catalonia", "Andalusia", "Valencia"],
        "Brazil": ["São Paulo", "Rio de Janeiro", "Minas Gerais", "Bahia"],
        "Mexico": ["Mexico City", "Jalisco", "Nuevo León", "Puebla"],
        "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia"],
        "Japan": ["Tokyo", "Osaka", "Kyoto", "Hokkaido"],
        "South Korea": ["Seoul", "Busan", "Incheon", "Daegu"],
        "Sweden": ["Stockholm", "Gothenburg", "Malmö", "Uppsala"],
    }
    
    # Generate random profile data
    selected_country = random.choice(countries)
    selected_region = random.choice(regions.get(selected_country, ["N/A"]))
    
    # Update user profile
    user.bio = random.choice(bios)
    user.country = selected_country
    user.region = selected_region
    
    # Gaming connections
    user.steam_username = f"{user.username}Gaming"
    user.steam_url = f"https://steamcommunity.com/id/{user.username.lower()}{random.randint(100, 999)}"
    user.riot_id = f"{user.username}#{random.choice(['NA1', 'EUW', 'KR', 'BR1', 'LAN'])}"
    user.battlenet_id = f"{user.username}#{random.randint(1000, 9999)}"
    user.discord_id = f"{user.username.lower()}#{random.randint(1000, 9999)}"
    
    # Optional: Add some gaming platforms (50% chance each)
    if random.choice([True, False]):
        user.xbox_gamertag = f"{user.username}Gaming"
    
    if random.choice([True, False]):
        user.psn_id = f"{user.username}_{random.randint(10, 99)}"
    
    # Optional: Add social media (30% chance each)
    if random.choice([True, False, False]):
        user.twitter_handle = user.username.lower()
    
    if random.choice([True, False, False]):
        user.twitch_username = user.username.lower()
    
    if random.choice([True, False, False]):
        user.youtube_channel = f"@{user.username}Gaming"
    
    user.save()
    
    print("✅ Successfully populated TestXD profile!")
    print("\n📋 Profile Data:")
    print(f"   Username: {user.username}")
    print(f"   Bio: {user.bio[:50]}...")
    print(f"   Location: {user.region}, {user.country}")
    print(f"\n🎮 Gaming Connections:")
    print(f"   Steam: {user.steam_username}")
    print(f"   Steam URL: {user.steam_url}")
    print(f"   Riot ID: {user.riot_id}")
    print(f"   Battle.net: {user.battlenet_id}")
    print(f"   Discord: {user.discord_id}")
    
    if user.xbox_gamertag:
        print(f"   Xbox: {user.xbox_gamertag}")
    if user.psn_id:
        print(f"   PSN: {user.psn_id}")
    
    if user.twitter_handle or user.twitch_username or user.youtube_channel:
        print(f"\n📱 Social Media:")
        if user.twitter_handle:
            print(f"   Twitter: @{user.twitter_handle}")
        if user.twitch_username:
            print(f"   Twitch: {user.twitch_username}")
        if user.youtube_channel:
            print(f"   YouTube: {user.youtube_channel}")


if __name__ == '__main__':
    print("🚀 Populating TestXD profile with random data...\n")
    populate_testuser()
