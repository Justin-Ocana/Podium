# Podium Frontend

Frontend de la plataforma Podium construido con React + Vite siguiendo el sistema de diseño especificado.

## Tecnologías

- React 19
- React Router DOM 7
- Vite 8
- CSS Modules

## Sistema de Diseño

El frontend implementa el sistema de diseño Podium con:

- Dark UI (#0F172A background principal)
- Paleta de colores profesional (Primary: #3B82F6, Accent Purple: #A855F7, Accent Cyan: #22D3EE)
- Tipografía Inter
- Componentes reutilizables

## Estructura

```
src/
├── components/          # Componentes reutilizables
│   ├── Button.jsx      # Botón con variantes (primary, secondary, danger)
│   ├── Input.jsx       # Input con validación y estados
│   ├── Card.jsx        # Tarjeta contenedora
│   ├── Badge.jsx       # Etiquetas de estado
│   ├── Avatar.jsx      # Avatar de usuario/equipo
│   ├── Navbar.jsx      # Barra de navegación
│   └── ProtectedRoute.jsx  # Rutas protegidas
├── contexts/           # Contextos de React
│   └── AuthContext.jsx # Contexto de autenticación
├── pages/              # Páginas de la aplicación
│   ├── Login.jsx       # Página de inicio de sesión
│   ├── Register.jsx    # Página de registro
│   ├── Dashboard.jsx   # Dashboard principal con stats
│   ├── Tournaments.jsx # Lista de torneos
│   ├── Teams.jsx       # Lista de equipos
│   └── Profile.jsx     # Perfil de usuario
├── services/           # Servicios y API
│   └── api.js          # Cliente API para backend Django
├── styles/             # Estilos globales
│   └── variables.css   # Variables CSS del sistema de diseño
├── App.jsx             # Componente principal con rutas
├── main.jsx            # Punto de entrada
└── index.css           # Estilos globales
```

## Componentes Implementados

### Button
Variantes: `primary`, `secondary`, `danger`
Tamaños: `small`, `medium`, `large`
Estados: `normal`, `hover`, `disabled`, `loading`

### Input
- Validación integrada
- Mensajes de error
- Estados: `normal`, `focus`, `error`, `disabled`

### Card
- Contenedor con estilo del sistema de diseño
- Opción de hover effect

### Badge
Variantes: `success`, `warning`, `danger`, `info`, `purple`, `cyan`
Uso: Estados de torneos, equipos, etc.

### Avatar
Tamaños: `small` (32px), `medium` (48px), `large` (96px)
Soporte para imágenes o iniciales

### Navbar
- Logo de Podium
- Links de navegación (Tournaments, Teams, Leaderboard)
- Notificaciones
- Menú de usuario con dropdown

## Páginas Implementadas

### Login (`/login`)
- Formulario de inicio de sesión
- Integración con API de Django
- Validación de email y password
- Manejo de errores del backend
- Link a registro

### Register (`/register`)
- Formulario de registro
- Integración con API de Django
- Validación de username, email, password
- Confirmación de password
- Manejo de errores del backend (username/email duplicado)
- Link a login

### Dashboard (`/dashboard`)
- Estadísticas del usuario (teams, tournaments, wins, win rate)
- Lista de torneos recientes
- Lista de equipos del usuario
- Estados vacíos con CTAs
- Integración completa con backend

### Tournaments (`/tournaments`)
- Lista de todos los torneos
- Filtros y búsqueda (próximamente)
- Botón para crear torneo

### Teams (`/teams`)
- Lista de todos los equipos
- Información de miembros y torneos
- Botón para crear equipo

### Profile (`/profile`)
- Información del usuario
- Avatar y bio
- Estadísticas detalladas
- Edición de perfil

## Integración con Backend

### API Service (`src/services/api.js`)

Cliente API que se conecta con el backend Django en `http://localhost:8000/api`

Endpoints implementados:
- `POST /auth/register/` - Registro de usuario
- `POST /auth/login/` - Inicio de sesión
- `POST /auth/logout/` - Cerrar sesión
- `GET /users/me/` - Obtener usuario actual
- `PATCH /users/me/` - Actualizar perfil
- `GET /profiles/{id}/stats/` - Estadísticas de usuario
- `GET /teams/` - Lista de equipos
- `GET /teams/{id}/` - Detalle de equipo
- `POST /teams/` - Crear equipo
- `GET /tournaments/` - Lista de torneos (placeholder)

### Autenticación

El sistema usa Token Authentication de Django REST Framework:
- El token se guarda en `localStorage`
- Se incluye en el header `Authorization: Token <token>`
- El contexto `AuthContext` maneja el estado de autenticación
- Las rutas protegidas redirigen a `/login` si no hay autenticación

## Instalación y Ejecución

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Construir para producción
npm run build

# Preview de producción
npm run preview
```

## Configuración del Backend

Asegúrate de que el backend Django esté corriendo en `http://localhost:8000`

Si necesitas cambiar la URL del backend, edita `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## Variables CSS Principales

```css
--bg-main: #0F172A
--bg-card: #1E293B
--bg-navbar: #020617
--primary: #3B82F6
--accent-purple: #A855F7
--accent-cyan: #22D3EE
--text-main: #F8FAFC
--text-secondary: #CBD5E1
--text-muted: #94A3B8
```

## Flujo de Autenticación

1. Usuario se registra o inicia sesión
2. Backend devuelve token y datos de usuario
3. Token se guarda en localStorage
4. AuthContext actualiza el estado
5. Usuario es redirigido al dashboard
6. Todas las peticiones incluyen el token
7. Al cerrar sesión, se limpia el token

## Próximos Pasos

- [ ] Implementar creación de torneos
- [ ] Implementar creación de equipos
- [ ] Agregar página de detalle de torneo
- [ ] Agregar página de detalle de equipo
- [ ] Implementar sistema de brackets
- [ ] Agregar gestión de matches
- [ ] Implementar notificaciones en tiempo real
- [ ] Agregar búsqueda y filtros
- [ ] Implementar leaderboard
- [ ] Agregar más componentes del sistema de diseño (Modal, Dropdown, Tabs, Tooltip)

## Notas de Diseño

El frontend sigue fielmente el documento de diseño especificado en `docs/diseño.txt` y `docs/ui.txt`, implementando:

- Filosofía de diseño minimalista y funcional
- Alto contraste para legibilidad
- Interfaz dark con colores de acento
- Transiciones suaves (150ms)
- Responsive design
- Componentes reutilizables y consistentes
