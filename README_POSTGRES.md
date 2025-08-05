# GestorCloud - Integración con PostgreSQL

## Introducción

GestorCloud ahora soporta dos opciones de bases de datos:

1. **SQLite** (predeterminado) - Base de datos local en archivo, ideal para desarrollo y despliegues pequeños.
2. **PostgreSQL** - Sistema de base de datos robusto, ideal para producción y despliegues más grandes.

## Configuración

La configuración de la base de datos se realiza a través de variables de entorno, que pueden definirse en un archivo `.env` en la raíz del proyecto.

### Archivo .env

Cree un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
# Database Configuration

# Database Type (sqlite or postgres)
DB_TYPE=sqlite

# SQLite Configuration
SQLITE_PATH=data/gestorcloud.db

# PostgreSQL Configuration
PG_HOST=localhost
PG_PORT=5432
PG_USER=postgres
PG_PASSWORD=postgres
PG_DATABASE=gestorcloud
```

Para usar PostgreSQL, cambie `DB_TYPE=sqlite` a `DB_TYPE=postgres` y actualice las credenciales de PostgreSQL según sea necesario.

## Herramientas de Configuración y Pruebas

GestorCloud incluye scripts para simplificar la configuración y verificación:

### Script de Configuración Automática

```bash
# Ejecutar el asistente de configuración
./setup_environment.sh
```

Este script automatiza:
- Instalación de dependencias
- Creación del archivo .env si no existe
- Migración opcional de datos
- Prueba de conexión a la base de datos

### Prueba de Conexión a la Base de Datos

```bash
# Probar conexión a ambos tipos de base de datos
./test_db_connection.py

# Probar sólo la conexión a SQLite
./test_db_connection.py --sqlite

# Probar sólo la conexión a PostgreSQL
./test_db_connection.py --postgres
```

## Migración de SQLite a PostgreSQL

Se incluye un script para migrar los datos existentes de SQLite a PostgreSQL:

```bash
# Verificar la conexión a PostgreSQL sin migrar datos
python migrate_to_postgres.py --check

# Migrar datos desde SQLite a PostgreSQL
python migrate_to_postgres.py
```

### Requisitos previos para PostgreSQL

Antes de migrar a PostgreSQL:

1. Asegúrese de tener PostgreSQL instalado y en ejecución.
2. Cree una base de datos para GestorCloud:
   ```sql
   CREATE DATABASE gestorcloud;
   ```
3. Instale los requisitos adicionales:
   ```bash
   pip install psycopg2-binary sqlalchemy python-dotenv alembic
   ```

## Estructura del Sistema de Base de Datos

La nueva implementación utiliza un diseño modular:

- `DatabaseConnection`: Clase base abstracta para operaciones de base de datos
- `SQLiteConnection`: Implementación específica para SQLite
- `PostgreSQLConnection`: Implementación específica para PostgreSQL
- `GestorCloudDB`: Clase principal que utiliza la implementación adecuada según la configuración

## Estructura Actualizada

- `.env` - Archivo de configuración para la base de datos
- `.env.example` - Ejemplo de configuración para la base de datos
- `src/database_new.py` - Nuevo módulo que soporta PostgreSQL y SQLite
- `migrate_to_postgres.py` - Script para migrar datos desde SQLite a PostgreSQL
- `test_db_connection.py` - Script para verificar la conexión a la base de datos
- `setup_environment.sh` - Script para configurar el entorno automáticamente

## Ventajas de PostgreSQL

- Mayor rendimiento con grandes volúmenes de datos
- Mejor soporte para concurrencia (múltiples usuarios simultáneos)
- Funciones avanzadas de SQL
- Mayor escalabilidad
- Mejores herramientas de administración y respaldo