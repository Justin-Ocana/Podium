import requests
from django.conf import settings
from typing import Optional, Dict, List


class RAWGService:
    """Servicio para interactuar con la API de RAWG con cache local"""
    
    BASE_URL = "https://api.rawg.io/api"
    
    def __init__(self):
        self.api_key = settings.RAWG_API_KEY
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Realiza una petición a la API de RAWG"""
        if params is None:
            params = {}
        
        params['key'] = self.api_key
        
        try:
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  RAWG API error: {e}")
            print(f"ℹ️  Falling back to local game cache...")
            return None
    
    def search_games(self, query: str, page: int = 1, page_size: int = 20) -> Optional[Dict]:
        """Busca juegos por nombre"""
        params = {
            'search': query,
            'page': page,
            'page_size': page_size
        }
        result = self._make_request('games', params)
        
        # If RAWG API fails, search in local cache
        if result is None:
            print(f"🔍 Searching local cache for: '{query}'")
            from apps.teams.models import Game
            
            # Search in local database
            games = Game.objects.filter(name__icontains=query)[:page_size]
            
            print(f"✅ Found {games.count()} games in local cache")
            
            # Format as RAWG-like response
            return {
                'count': games.count(),
                'results': [
                    {
                        'id': game.rawg_id,
                        'name': game.name,
                        'slug': game.slug,
                        'background_image': game.cover_url,
                        'genres': [{'name': g} for g in game.genres],
                        'platforms': [{'platform': {'name': p}} for p in game.platforms],
                        'rating': float(game.rating) if game.rating else None
                    }
                    for game in games
                ]
            }
        
        return result
    
    def get_game_details(self, game_id: int) -> Optional[Dict]:
        """Obtiene detalles de un juego específico"""
        return self._make_request(f'games/{game_id}')
    
    def get_or_cache_game(self, rawg_id: int):
        """
        Obtiene un juego del cache local o lo descarga de RAWG.
        
        Esta es la función principal para el sistema de cache.
        """
        from apps.teams.models import Game
        
        # Intentar obtener del cache local
        try:
            game = Game.objects.get(rawg_id=rawg_id)
            return game
        except Game.DoesNotExist:
            pass
        
        # Si no existe, descargar de RAWG
        game_data = self.get_game_details(rawg_id)
        if not game_data:
            return None
        
        # Extraer solo los datos esenciales
        genres = [genre['name'] for genre in game_data.get('genres', [])]
        platforms = [platform['platform']['name'] for platform in game_data.get('platforms', [])]
        
        # Guardar en cache local
        game = Game.objects.create(
            rawg_id=game_data['id'],
            name=game_data['name'],
            slug=game_data['slug'],
            cover_url=game_data.get('background_image', ''),
            genres=genres,
            platforms=platforms,
            rating=game_data.get('rating')
        )
        
        return game
    
    def search_and_cache_games(self, query: str, page_size: int = 10) -> List:
        """
        Busca juegos y los guarda en cache si no existen.
        
        Retorna lista de objetos Game del cache local.
        """
        from apps.teams.models import Game
        from django.db import IntegrityError
        
        results = self.search_games(query, page_size=page_size)
        if not results or 'results' not in results:
            return []
        
        cached_games = []
        for game_data in results['results']:
            # Safely extract genres
            genres_data = game_data.get('genres')
            if genres_data and isinstance(genres_data, list):
                genres = [genre['name'] for genre in genres_data if genre and 'name' in genre]
            else:
                genres = []
            
            # Safely extract platforms
            platforms_data = game_data.get('platforms')
            if platforms_data and isinstance(platforms_data, list):
                platforms = [p['platform']['name'] for p in platforms_data if p and 'platform' in p and 'name' in p['platform']]
            else:
                platforms = []
            
            try:
                # Verificar si ya existe en cache
                game, created = Game.objects.get_or_create(
                    rawg_id=game_data['id'],
                    defaults={
                        'name': game_data['name'],
                        'slug': game_data['slug'],
                        'cover_url': game_data.get('background_image', ''),
                        'genres': genres,
                        'platforms': platforms,
                        'rating': game_data.get('rating')
                    }
                )
                cached_games.append(game)
            except IntegrityError as e:
                # Si hay un error de slug duplicado, intentar obtener por rawg_id
                print(f"⚠️  Integrity error for game {game_data['name']}: {e}")
                try:
                    game = Game.objects.get(rawg_id=game_data['id'])
                    cached_games.append(game)
                except Game.DoesNotExist:
                    # Si no existe, intentar con un slug único
                    unique_slug = f"{game_data['slug']}-{game_data['id']}"
                    game = Game.objects.create(
                        rawg_id=game_data['id'],
                        name=game_data['name'],
                        slug=unique_slug,
                        cover_url=game_data.get('background_image', ''),
                        genres=genres,
                        platforms=platforms,
                        rating=game_data.get('rating')
                    )
                    cached_games.append(game)
        
        return cached_games
    
    def get_platforms(self) -> Optional[Dict]:
        """Obtiene la lista de plataformas disponibles"""
        return self._make_request('platforms')
    
    def get_genres(self) -> Optional[Dict]:
        """Obtiene la lista de géneros disponibles"""
        return self._make_request('genres')
    
    def validate_game_exists(self, game_id: int) -> bool:
        """Valida si un juego existe en RAWG"""
        game = self.get_game_details(game_id)
        return game is not None


# Instancia global del servicio
rawg_service = RAWGService()
