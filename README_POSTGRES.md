# Configuración de PostgreSQL para GestorCloud

## Requisitos
- PostgreSQL 12 o superior
- Python 3.7 o superior
- Dependencias en requirements.txt

## Configuración Inicial

1. Crea una base de datos en PostgreSQL:
```sql
CREATE DATABASE gestorcloud;
```

2. Copia el archivo de variables de entorno:
```bash
cp env.template .env
```

3. Edita el archivo `.env` con tus credenciales de PostgreSQL:
```
PG_HOST=localhost
PG_PORT=5432
PG_DATABASE=gestorcloud
PG_USER=tu_usuario
PG_PASSWORD=tu_contraseña
```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

5. Ejecuta la aplicación:
```bash
python run_web.py
```

## Estructura de la Base de Datos

La estructura de la base de datos se creará automáticamente al iniciar la aplicación. La misma incluye las siguientes tablas:

- **clientes**: Almacena la información de los clientes
- **ventas**: Registra las ventas realizadas, con una relación a clientes

## Migración desde SQLite (Opcional)

Si estás migrando desde una instalación anterior con SQLite, puedes utilizar el script de migración:

```bash
python migrate_optimized.py
```

El script transferirá todos los datos de tu base de datos SQLite existente a PostgreSQL.

## Recomendaciones

1. Considera configurar un usuario específico para la aplicación con privilegios limitados.
2. Realiza copias de seguridad regulares de la base de datos.
3. Para entornos de producción, asegúrate de que la base de datos esté protegida y no expuesta directamente a internet.
4. Ajusta los parámetros de conexión en la configuración según el volumen de usuarios esperado.