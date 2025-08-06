# GestorCloud - Sistema de Gestión de Clientes

Sistema optimizado de gestión de clientes para pequeñas empresas con PostgreSQL para un rendimiento, escalabilidad y robustez mejorados.

## Características Principales

- **Gestión completa de clientes**: registra información detallada de tus clientes
- **Registro de ventas**: mantén un historial de compras de cada cliente
- **Categorización automática de clientes**: clasifica clientes como VIP basado en sus compras
- **Estadísticas y reportes**: visualiza datos clave del negocio
- **Base de datos PostgreSQL**: rendimiento y confiabilidad mejorados
- **Interfaz web intuitiva**: accede al sistema desde cualquier navegador

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

## Estructura de archivos

- `web/`: Interfaz web con FastAPI
- `src/`: Código fuente principal
  - `models.py`: Modelos de datos (Cliente, Venta)
  - `database_postgres.py`: Implementación para PostgreSQL
- `schema_postgresql.sql`: Esquema optimizado para PostgreSQL
- `requirements-optimized.txt`: Dependencias optimizadas

## Mejoras futuras

- Implementar sistema de autenticación de usuarios
- Añadir backups automáticos
- Implementar API REST completa
- Mejorar UI/UX con framework frontend moderno

## Licencia

[MIT](./LICENSE)