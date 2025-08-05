# GestorCloud - Migración a PostgreSQL y Optimización

Este documento describe el proceso de migración del sistema GestorCloud de SQLite a PostgreSQL, así como las optimizaciones realizadas para mejorar el rendimiento y mantenibilidad del código.

## Cambios realizados

### 1. Migración a PostgreSQL

La aplicación ha sido migrada completamente de SQLite a PostgreSQL:

- Se ha eliminado toda la lógica específica para SQLite
- Se han optimizado las consultas para aprovechar las características de PostgreSQL
- Se han añadido índices para mejorar el rendimiento de las consultas frecuentes
- Se han implementado vistas y funciones para optimizar operaciones comunes

### 2. Optimización de dependencias

Se han eliminado dependencias innecesarias para reducir el tamaño de la aplicación y mejorar su rendimiento:

- Eliminados paquetes CLI redundantes (colorama, rich, click)
- Eliminada dependencia pesada de pandas (reemplazada por SQL nativo)
- Separadas las dependencias de desarrollo en un archivo independiente

### 3. Mejoras estructurales

- Creación de un nuevo archivo `database_postgres.py` con código optimizado exclusivamente para PostgreSQL
- Implementación de un esquema SQL optimizado (`schema_postgresql.sql`) con tipos de datos apropiados
- Mejora de manejo de errores y conexiones a la base de datos

## Instrucciones de migración

### Preparación del entorno

1. **Instalar PostgreSQL**

   En sistemas basados en Debian/Ubuntu:
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

   En sistemas basados en Red Hat/Fedora:
   ```bash
   sudo dnf install postgresql postgresql-server
   sudo postgresql-setup --initdb
   sudo systemctl enable postgresql
   sudo systemctl start postgresql
   ```

2. **Crear usuario y base de datos**

   ```bash
   sudo -u postgres psql
   ```

   En la consola de PostgreSQL:
   ```sql
   CREATE USER gestorcloud WITH PASSWORD 'password_seguro';
   CREATE DATABASE gestorcloud OWNER gestorcloud;
   \q
   ```

3. **Configurar variables de entorno**

   Crear un archivo `.env` en el directorio raíz del proyecto:
   ```
   DB_TYPE=postgres
   PG_DATABASE=gestorcloud
   PG_USER=gestorcloud
   PG_PASSWORD=password_seguro
   PG_HOST=localhost
   PG_PORT=5432
   ```

### Ejecutar la migración

1. **Instalar dependencias optimizadas**

   ```bash
   pip install -r requirements-optimized.txt
   ```

2. **Migrar datos de SQLite a PostgreSQL**

   Si ya tienes datos en SQLite que deseas migrar:
   ```bash
   python migrate_to_postgres.py
   ```

3. **Actualizar la aplicación para usar PostgreSQL**

   Actualizar el archivo `web/app.py` para importar desde la nueva implementación:
   ```python
   # Cambiar:
   from database import GestorCloudDB
   # Por:
   from database_postgres import GestorCloudDB
   ```

4. **Iniciar la aplicación**

   ```bash
   python run_web.py
   ```

## Mejoras de rendimiento

La migración a PostgreSQL ofrece varias mejoras de rendimiento:

1. **Mejor rendimiento con grandes volúmenes de datos**
   - PostgreSQL está optimizado para grandes conjuntos de datos
   - Índices más eficientes para búsquedas frecuentes

2. **Optimización de consultas**
   - Las vistas permiten acceso más rápido a datos frecuentemente consultados
   - Las funciones y triggers automatizan operaciones comunes

3. **Concurrencia mejorada**
   - PostgreSQL permite más conexiones concurrentes sin bloqueos
   - Mejor manejo de transacciones simultáneas

## Verificación de la migración

Para verificar que la migración se ha completado correctamente:

1. **Comprobar la conexión a PostgreSQL**
   ```bash
   python -c "import psycopg2; print(psycopg2.connect('dbname=gestorcloud user=gestorcloud password=password_seguro host=localhost port=5432'))"
   ```

2. **Verificar las tablas**
   ```bash
   psql -U gestorcloud -d gestorcloud -c "\dt"
   ```

3. **Ejecutar pruebas de rendimiento**
   ```bash
   python tests/test_performance.py
   ```

## Solución de problemas

### Error de conexión a PostgreSQL

Si encuentras errores de conexión:

1. **Verificar variables de entorno**
   ```bash
   cat .env
   ```

2. **Verificar que PostgreSQL está en ejecución**
   ```bash
   sudo systemctl status postgresql
   ```

3. **Verificar permisos en pg_hba.conf**
   ```bash
   sudo nano /etc/postgresql/*/main/pg_hba.conf
   ```

### Datos no migrados correctamente

1. **Verificar registros en PostgreSQL**
   ```bash
   psql -U gestorcloud -d gestorcloud -c "SELECT COUNT(*) FROM clientes"
   psql -U gestorcloud -d gestorcloud -c "SELECT COUNT(*) FROM ventas"
   ```

2. **Ejecutar migración en modo debug**
   ```bash
   DB_DEBUG=true python migrate_to_postgres.py
   ```

## Próximos pasos recomendados

1. **Implementar backup automático**
   - Configurar `pg_dump` para backups diarios

2. **Optimizar consultas adicionales**
   - Revisar consultas lentas con el analizador de PostgreSQL

3. **Implementar autenticación de usuarios**
   - Añadir sistema de login para entornos multiusuario

---

Para cualquier consulta o problema durante la migración, por favor reportarlo en el repositorio oficial de GestorCloud.