# GestorCloud - Sistema de Gestión de Clientes

Sistema optimizado de gestión de clientes para pequeñas empresas. Esta versión ha sido migrada de SQLite a PostgreSQL para mejorar el rendimiento, escalabilidad y robustez.

## Características Principales

- **Gestión completa de clientes**: registra información detallada de tus clientes
- **Registro de ventas**: mantén un historial de compras de cada cliente
- **Categorización automática de clientes**: clasifica clientes como VIP basado en sus compras
- **Estadísticas y reportes**: visualiza datos clave del negocio
- **Base de datos PostgreSQL**: rendimiento y confiabilidad mejorados
- **Interfaz web intuitiva**: accede al sistema desde cualquier navegador

## Cambios en la Migración

Esta versión introduce las siguientes mejoras:

1. **Migración completa a PostgreSQL**
   - Mayor rendimiento con grandes volúmenes de datos
   - Mejor manejo de concurrencia
   - Tipos de datos optimizados

2. **Optimización de dependencias**
   - Reducción de paquetes innecesarios
   - Separación de dependencias de desarrollo
   - Eliminación de bibliotecas pesadas

3. **Mejoras estructurales**
   - Implementación optimizada para PostgreSQL
   - Esquema SQL mejorado con índices y vistas
   - Mejor manejo de errores

## Requisitos

- Python 3.8+
- PostgreSQL 12+
- Bibliotecas Python (ver `requirements-optimized.txt`)

## Instalación

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/tu-usuario/GestorCloud.git
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
   PG_DATABASE=gestorcloud
   PG_USER=gestorcloud
   PG_PASSWORD=password_seguro
   PG_HOST=localhost
   PG_PORT=5432
   ```

6. **Inicializar la base de datos**

   ```bash
   python migrate_optimized.py
   ```

7. **Actualizar la importación en app.py**

   Editar `web/app.py` y cambiar:
   ```python
   from database import GestorCloudDB
   ```
   por:
   ```python
   from database_postgres import GestorCloudDB
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
  - `database_postgres.py`: Nueva implementación para PostgreSQL
- `schema_postgresql.sql`: Esquema optimizado para PostgreSQL
- `migrate_optimized.py`: Script mejorado para migrar datos
- `requirements-optimized.txt`: Dependencias optimizadas

## Documentación adicional

- [MIGRATION_RECOMMENDATIONS.md](./MIGRATION_RECOMMENDATIONS.md) - Detalles técnicos sobre la migración
- [README_MIGRADO.md](./README_MIGRADO.md) - Instrucciones paso a paso para la migración
- [README_POSTGRES.md](./README_POSTGRES.md) - Documentación original sobre PostgreSQL

## Mejoras futuras

- Implementar sistema de autenticación de usuarios
- Añadir backups automáticos
- Implementar API REST completa
- Mejorar UI/UX con framework frontend moderno

## Solución de problemas

Consulta [README_MIGRADO.md](./README_MIGRADO.md) para instrucciones detalladas sobre solución de problemas durante y después de la migración.

## Licencia

[MIT](./LICENSE)