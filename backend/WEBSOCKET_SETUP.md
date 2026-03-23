# Configuración de WebSockets en Render

## Cambios realizados

1. **Agregado Daphne** al `requirements.txt` - Servidor ASGI que soporta WebSockets
2. **Actualizado `render.yaml`** - Cambio de Gunicorn a Daphne
3. **Configurado Channels** - Usa InMemoryChannelLayer (no requiere Redis en plan gratuito)

## Cómo actualizar en Render

### Opción 1: Actualizar el Start Command manualmente

1. Ve a tu servicio en Render Dashboard
2. Ve a **Settings** → **Build & Deploy**
3. Cambia el **Start Command** a:
   ```
   daphne -b 0.0.0.0 -p $PORT config.asgi:application
   ```
4. Haz clic en **Save Changes**
5. Render redesplegará automáticamente

### Opción 2: Usar render.yaml (recomendado)

El archivo `render.yaml` ya está actualizado. Render lo detectará automáticamente en el próximo deploy.

## Verificar que funciona

1. Después del deploy, ve a tu frontend en Vercel
2. Abre la consola del navegador (F12)
3. Deberías ver: `✅ WebSocket connected`
4. Las notificaciones en tiempo real deberían funcionar

## Notas importantes

- **InMemoryChannelLayer**: Funciona bien para un solo servidor (plan gratuito de Render)
- **Redis**: Si escalas a múltiples instancias, necesitarás Redis
  - Render ofrece Redis como servicio adicional (de pago)
  - Agrega la variable de entorno `REDIS_URL` y el código cambiará automáticamente

## Troubleshooting

Si WebSocket no conecta:

1. Verifica que el Start Command sea correcto
2. Revisa los logs en Render: `Dashboard → Logs`
3. Busca errores relacionados con Daphne o ASGI
4. Verifica que `ALLOWED_HOSTS` incluya tu dominio de Render

## Comandos útiles para desarrollo local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr con Daphne localmente
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# O usar el servidor de desarrollo de Django (también soporta WebSockets con Channels)
python manage.py runserver
```
