# GestorCloud - Sistema de Gestión de Clientes

Sistema optimizado de gestión de clientes para pequeñas empresas con PostgreSQL para un rendimiento, escalabilidad y robustez mejorados.

## Características Principales

- **Gestión completa de clientes**: registra información detallada de tus clientes
- **Registro de ventas**: mantén un historial de compras de cada cliente
- **Categorización automática de clientes**: clasifica clientes como VIP basado en sus compras
- **Estadísticas y reportes**: visualiza datos clave del negocio
- **Base de datos PostgreSQL**: rendimiento y confiabilidad mejorados
- **Interfaz web intuitiva**: accede al sistema desde cualquier navegador
- **Gestión de usuarios**: registro, inicio de sesión y perfiles de usuario

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- Bibliotecas Python (ver `requirements-optimized.txt`)

## Instalación

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/cesarcorrales17/GestorCloud.git
   cd GestorCloud
   ```

2. **Configurar el entorno virtual**

   ```bash
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

3. **Instalar dependencias**

   ```bash
   pip install -r requirements-optimized.txt
   ```

4. **Configurar PostgreSQL**

   - Instalar PostgreSQL según tu sistema operativo
   - Crear una base de datos y un usuario:
     ```sql
     CREATE USER gestorcloud WITH PASSWORD 'password_seguro';
     CREATE DATABASE gestorcloud OWNER gestorcloud;
     ```

5. **Configurar variables de entorno**

   Crear un archivo `.env` en el directorio raíz:
   ```
   DB_TYPE=postgres
   PG_DATABASE=GestorCloudDB
   PG_USER=gestorcloud
   PG_PASSWORD=password_seguro
   PG_HOST=localhost
   PG_PORT=5432
   ```

## Ejecución

```bash
python run_web.py
```

El sistema estará disponible en http://localhost:8000

## Módulos del Sistema

### Módulo de Autenticación y Usuarios
- **Registro de usuarios**: Crea nuevas cuentas en `/registro`
- **Inicio de sesión**: Accede al sistema en `/login`
- **Perfil de usuario**: Administra tu información personal en `/perfil`
- **Cierre de sesión**: Termina tu sesión de forma segura

### Módulo de Clientes
- Gestión completa de clientes
- Búsqueda avanzada
- Historial de interacciones

### Módulo de Ventas
- Registro de transacciones
- Generación de facturas
- Seguimiento de pagos

### Módulo de Reportes
- Estadísticas de ventas
- Análisis de clientes
- Exportación a múltiples formatos

## Estructura de archivos

- `web/`: Interfaz web con FastAPI
  - `templates/`: Plantillas HTML para la interfaz
  - `static/`: Archivos CSS, JavaScript e imágenes
  - `app.py`: Aplicación principal FastAPI
- `src/`: Código fuente principal
  - `models.py`: Modelos de datos (Cliente, Venta, Usuario)
  - `database_postgres.py`: Implementación para PostgreSQL
- `schema_postgresql.sql`: Esquema optimizado para PostgreSQL
- `requirements-optimized.txt`: Dependencias optimizadas

## Estado Actual del Desarrollo

- ✅ Interfaz web básica implementada
- ✅ Rutas de navegación configuradas
- ✅ Sistema de autenticación (front-end)
- ⏳ Integración con PostgreSQL en progreso
- ⏳ Implementación del módulo de clientes en progreso
- 🔜 Implementación del módulo de ventas planificada
- 🔜 Implementación de reportes y estadísticas planificada

## Mejoras futuras

- Implementar sistema de autenticación con JWT
- Añadir backups automáticos de la base de datos
- Implementar API REST completa
- Mejorar UI/UX con framework frontend moderno
- Añadir soporte para múltiples idiomas
- Implementar notificaciones en tiempo real

## Licencia

[MIT](./LICENSE)