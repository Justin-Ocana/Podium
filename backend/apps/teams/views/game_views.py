from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.teams.serializers import GameSerializer, GameSearchSerializer
from apps.teams.rawg_service import rawg_service
from apps.teams.models import Game


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_games(request):
    """
    Busca juegos en RAWG y los guarda en cache local.
    
    Query params:
    - query: término de búsqueda (requerido, mínimo 2 caracteres)
    - page_size: cantidad de resultados (opcional, default 10, máximo 40)
    
    Returns:
    - Lista de juegos con datos esenciales (nombre, portada, géneros, plataformas)
    """
    serializer = GameSearchSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    query = serializer.validated_data['query']
    page_size = serializer.validated_data.get('page_size', 10)
    
    # Buscar y cachear juegos
    games = rawg_service.search_and_cache_games(query, page_size)
    
    # Serializar resultados
    game_serializer = GameSerializer(games, many=True)
    
    return Response({
        'count': len(games),
        'results': game_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_detail(request, rawg_id):
    """
    Obtiene detalles de un juego específico.
    
    Si el juego no está en cache, lo descarga de RAWG.
    """
    game = rawg_service.get_or_cache_game(rawg_id)
    
    if not game:
        return Response(
            {'error': 'Juego no encontrado en RAWG'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = GameSerializer(game)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cached_games(request):
    """
    Lista todos los juegos en cache local.
    
    Útil para mostrar juegos populares sin hacer llamadas a la API.
    """
    games = Game.objects.all()[:50]  # Limitar a 50 juegos más recientes
    serializer = GameSerializer(games, many=True)
    
    return Response({
        'count': games.count(),
        'results': serializer.data
    }, status=status.HTTP_200_OK)
