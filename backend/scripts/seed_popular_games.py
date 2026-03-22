"""
Script to seed popular esports games into the database.

This provides a fallback when RAWG API is unavailable.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.teams.models import Game


POPULAR_GAMES = [
    {
        'rawg_id': 3328,
        'name': 'Valorant',
        'slug': 'valorant',
        'cover_url': 'https://media.rawg.io/media/games/4be/4be6a6ad0364751a96229c56bf69be59.jpg',
        'genres': ['Action', 'Shooter'],
        'platforms': ['PC'],
        'rating': 4.5
    },
    {
        'rawg_id': 3498,
        'name': 'Counter-Strike 2',
        'slug': 'counter-strike-2',
        'cover_url': 'https://media.rawg.io/media/games/736/73619bd336c894d6941d926bfd563946.jpg',
        'genres': ['Action', 'Shooter'],
        'platforms': ['PC'],
        'rating': 4.8
    },
    {
        'rawg_id': 3272,
        'name': 'Rocket League',
        'slug': 'rocket-league',
        'cover_url': 'https://media.rawg.io/media/games/8cc/8cce7c0e99dcc43d66c8efd42f9d03e3.jpg',
        'genres': ['Sports', 'Racing'],
        'platforms': ['PC', 'PlayStation', 'Xbox', 'Nintendo Switch'],
        'rating': 4.4
    },
    {
        'rawg_id': 4062,
        'name': 'League of Legends',
        'slug': 'league-of-legends',
        'cover_url': 'https://media.rawg.io/media/games/78d/78dfae12fb8c5b16cd78648553071e0a.jpg',
        'genres': ['Action', 'Strategy', 'MOBA'],
        'platforms': ['PC'],
        'rating': 4.3
    },
    {
        'rawg_id': 28,
        'name': 'Dota 2',
        'slug': 'dota-2',
        'cover_url': 'https://media.rawg.io/media/games/6fc/6fcf4cd3b17c288821388e6085bb0fc9.jpg',
        'genres': ['Action', 'Strategy', 'MOBA'],
        'platforms': ['PC'],
        'rating': 4.2
    },
    {
        'rawg_id': 5679,
        'name': 'Overwatch 2',
        'slug': 'overwatch-2',
        'cover_url': 'https://media.rawg.io/media/games/c92/c9207a31f0eeb9904a840fc26eae6afb.jpg',
        'genres': ['Action', 'Shooter'],
        'platforms': ['PC', 'PlayStation', 'Xbox', 'Nintendo Switch'],
        'rating': 4.1
    },
    {
        'rawg_id': 58175,
        'name': 'Apex Legends',
        'slug': 'apex-legends',
        'cover_url': 'https://media.rawg.io/media/games/b72/b7233d5d5b1e75e86bb860ccc7aeca85.jpg',
        'genres': ['Action', 'Shooter', 'Battle Royale'],
        'platforms': ['PC', 'PlayStation', 'Xbox', 'Nintendo Switch'],
        'rating': 4.3
    },
    {
        'rawg_id': 3939,
        'name': 'Fortnite',
        'slug': 'fortnite',
        'cover_url': 'https://media.rawg.io/media/games/1f4/1f47a270b8f241e4676b14d39ec620f7.jpg',
        'genres': ['Action', 'Shooter', 'Battle Royale'],
        'platforms': ['PC', 'PlayStation', 'Xbox', 'Nintendo Switch', 'Mobile'],
        'rating': 4.0
    },
    {
        'rawg_id': 5286,
        'name': 'Rainbow Six Siege',
        'slug': 'tom-clancys-rainbow-six-siege',
        'cover_url': 'https://media.rawg.io/media/games/511/5118aff5091cb3efec399c808f8c598f.jpg',
        'genres': ['Action', 'Shooter'],
        'platforms': ['PC', 'PlayStation', 'Xbox'],
        'rating': 4.4
    },
    {
        'rawg_id': 13536,
        'name': 'Call of Duty: Warzone',
        'slug': 'call-of-duty-warzone',
        'cover_url': 'https://media.rawg.io/media/games/d82/d82990b9c67ba0d2d09d4e6fa88885a7.jpg',
        'genres': ['Action', 'Shooter', 'Battle Royale'],
        'platforms': ['PC', 'PlayStation', 'Xbox'],
        'rating': 4.2
    },
]


def seed_games():
    """Seed popular esports games into the database."""
    print("🎮 Seeding popular esports games...")
    
    created_count = 0
    updated_count = 0
    
    for game_data in POPULAR_GAMES:
        game, created = Game.objects.update_or_create(
            rawg_id=game_data['rawg_id'],
            defaults={
                'name': game_data['name'],
                'slug': game_data['slug'],
                'cover_url': game_data['cover_url'],
                'genres': game_data['genres'],
                'platforms': game_data['platforms'],
                'rating': game_data['rating']
            }
        )
        
        if created:
            created_count += 1
            print(f"  ✅ Created: {game.name}")
        else:
            updated_count += 1
            print(f"  🔄 Updated: {game.name}")
    
    print(f"\n✨ Done! Created {created_count}, Updated {updated_count}")
    print(f"📊 Total games in database: {Game.objects.count()}")


if __name__ == '__main__':
    seed_games()
