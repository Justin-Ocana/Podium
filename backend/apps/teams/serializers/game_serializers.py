from rest_framework import serializers
from apps.teams.models import Game


class GameSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Game"""
    
    class Meta:
        model = Game
        fields = [
            'id',
            'rawg_id',
            'name',
            'slug',
            'cover_url',
            'genres',
            'platforms',
            'rating',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class GameSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de juegos"""
    query = serializers.CharField(
        required=True,
        min_length=2,
        max_length=100,
        help_text='Término de búsqueda (mínimo 2 caracteres)'
    )
    page_size = serializers.IntegerField(
        required=False,
        default=10,
        min_value=1,
        max_value=40,
        help_text='Cantidad de resultados (1-40)'
    )
