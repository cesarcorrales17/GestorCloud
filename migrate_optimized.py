#!/usr/bin/env python3
"""
GestorCloud - Script optimizado para migración de datos de SQLite a PostgreSQL
Este script mejora el proceso de migración con mejor manejo de errores y reportes
"""

import os
import sys
import sqlite3
import psycopg2
import dotenv
from datetime import datetime
from pathlib import Path
import argparse

# Cargar variables de entorno
dotenv.load_dotenv()

# Configuración
DEFAULT_SQLITE_PATH = "data/gestorcloud.db"
LOG_FILE = f"migration_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
DEBUG = os.getenv("DB_DEBUG", "false").lower() == "true"

def log_message(message, file=None):
    """Registra mensajes en consola y en archivo"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    if file:
        file.write(log_entry + "\n")
        file.flush()

def get_sqlite_connection(db_path):
    """Establece conexión a SQLite"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise ConnectionError(f"Error al conectar a SQLite: {e}")

def get_postgres_connection():
    """Establece conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("PG_DATABASE", "gestorcloud"),
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASSWORD", "postgres"),
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "5432")
        )
        return conn
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"Error al conectar a PostgreSQL: {e}")

def create_postgres_schema(pg_conn):
    """Crea el esquema en PostgreSQL si no existe"""
    try:
        cursor = pg_conn.cursor()
        
        # Verificar si el esquema existe
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'clientes')")
        schema_exists = cursor.fetchone()[0]
        
        if not schema_exists:
            log_message("Creando esquema en PostgreSQL...")
            
            # Intentar cargar desde archivo
            schema_path = Path('schema_postgresql.sql')
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    sql_schema = f.read()
                cursor.execute(sql_schema)
                log_message("Esquema creado desde archivo")
            else:
                # Crear esquema básico
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clientes (
                        id_cliente SERIAL PRIMARY KEY,
                        nombre_completo TEXT NOT NULL,
                        edad INTEGER NOT NULL,
                        direccion TEXT NOT NULL,
                        correo TEXT UNIQUE NOT NULL,
                        telefono TEXT NOT NULL,
                        empresa TEXT DEFAULT '',
                        categoria TEXT DEFAULT 'Regular',
                        estado TEXT DEFAULT 'Activo',
                        fecha_registro DATE NOT NULL,
                        ultima_actualizacion TIMESTAMP NOT NULL,
                        notas TEXT DEFAULT '',
                        valor_total_compras DECIMAL(12,2) DEFAULT 0.0,
                        numero_compras INTEGER DEFAULT 0,
                        ultima_compra DATE DEFAULT NULL,
                        descuento_cliente DECIMAL(4,2) DEFAULT 0.0
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ventas (
                        id_venta SERIAL PRIMARY KEY,
                        id_cliente INTEGER NOT NULL,
                        fecha_venta DATE NOT NULL,
                        hora_venta TIME NOT NULL,
                        productos TEXT NOT NULL,
                        valor_total DECIMAL(12,2) NOT NULL,
                        descuento_aplicado DECIMAL(4,2) DEFAULT 0.0,
                        metodo_pago TEXT DEFAULT 'Efectivo',
                        vendedor TEXT DEFAULT '',
                        notas_venta TEXT DEFAULT '',
                        FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
                    )
                """)
                
                # Crear índices básicos
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cliente_nombre ON clientes(nombre_completo);
                    CREATE INDEX IF NOT EXISTS idx_cliente_correo ON clientes(correo);
                    CREATE INDEX IF NOT EXISTS idx_cliente_categoria ON clientes(categoria);
                    CREATE INDEX IF NOT EXISTS idx_venta_fecha ON ventas(fecha_venta);
                    CREATE INDEX IF NOT EXISTS idx_venta_cliente ON ventas(id_cliente);
                """)
                
                log_message("Esquema básico creado manualmente")
            
            pg_conn.commit()
        else:
            log_message("El esquema ya existe en PostgreSQL")
        
        return True
    except (psycopg2.Error, Exception) as e:
        log_message(f"Error al crear esquema: {e}")
        pg_conn.rollback()
        return False

def get_client_mappings(sqlite_conn, pg_conn):
    """Obtiene un mapeo de IDs de clientes entre SQLite y PostgreSQL"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    # Obtener correos de clientes en SQLite
    cursor_sqlite.execute("SELECT id_cliente, correo FROM clientes")
    sqlite_clients = {row['correo']: row['id_cliente'] for row in cursor_sqlite.fetchall()}
    
    # Obtener correos e IDs de clientes en PostgreSQL
    cursor_pg.execute("SELECT id_cliente, correo FROM clientes")
    pg_clients = {row[1]: row[0] for row in cursor_pg.fetchall()}
    
    # Crear mapeo de IDs
    id_mapping = {}
    for correo, sqlite_id in sqlite_clients.items():
        if correo in pg_clients:
            id_mapping[sqlite_id] = pg_clients[correo]
    
    return id_mapping

def migrate_clientes(sqlite_conn, pg_conn, log_file):
    """Migra datos de clientes de SQLite a PostgreSQL"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    log_message("Migrando clientes...", log_file)
    
    # Obtener todos los clientes de SQLite
    cursor_sqlite.execute("SELECT * FROM clientes")
    clientes = cursor_sqlite.fetchall()
    
    total_clientes = len(clientes)
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for cliente in clientes:
        try:
            # Verificar si ya existe el cliente con el mismo correo
            cursor_pg.execute("SELECT COUNT(*) FROM clientes WHERE correo = %s", (cliente['correo'],))
            exists = cursor_pg.fetchone()[0] > 0
            
            if exists:
                if DEBUG:
                    log_message(f"Cliente ya existe: {cliente['correo']}", log_file)
                skipped_count += 1
                continue
            
            # Preparar fechas
            fecha_registro = cliente['fecha_registro'] 
            ultima_actualizacion = cliente['ultima_actualizacion']
            ultima_compra = cliente['ultima_compra'] if cliente['ultima_compra'] else None
            
            # Insertar cliente en PostgreSQL
            cursor_pg.execute("""
                INSERT INTO clientes (
                    nombre_completo, edad, direccion, correo, telefono,
                    empresa, categoria, estado, fecha_registro, ultima_actualizacion,
                    notas, valor_total_compras, numero_compras, ultima_compra, descuento_cliente
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                cliente['nombre_completo'], cliente['edad'], cliente['direccion'],
                cliente['correo'], cliente['telefono'], cliente['empresa'],
                cliente['categoria'], cliente['estado'], fecha_registro,
                ultima_actualizacion, cliente['notas'],
                float(cliente['valor_total_compras']), cliente['numero_compras'],
                ultima_compra, float(cliente['descuento_cliente'])
            ))
            
            migrated_count += 1
            if migrated_count % 10 == 0:
                log_message(f"Migrados {migrated_count} de {total_clientes} clientes", log_file)
                pg_conn.commit()
            
        except Exception as e:
            error_count += 1
            log_message(f"Error al migrar cliente {cliente['nombre_completo']}: {e}", log_file)
            if DEBUG:
                import traceback
                traceback.print_exc()
    
    pg_conn.commit()
    log_message(f"Migración de clientes completada: {migrated_count} migrados, {skipped_count} omitidos, {error_count} errores", log_file)
    return migrated_count, skipped_count, error_count

def migrate_ventas(sqlite_conn, pg_conn, log_file):
    """Migra datos de ventas de SQLite a PostgreSQL"""
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    log_message("Migrando ventas...", log_file)
    
    # Obtener mapeo de IDs de clientes
    id_mapping = get_client_mappings(sqlite_conn, pg_conn)
    
    # Obtener todas las ventas de SQLite
    cursor_sqlite.execute("SELECT * FROM ventas")
    ventas = cursor_sqlite.fetchall()
    
    total_ventas = len(ventas)
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for venta in ventas:
        try:
            # Verificar si existe el cliente en PostgreSQL
            sqlite_cliente_id = venta['id_cliente']
            if sqlite_cliente_id not in id_mapping:
                log_message(f"Cliente no encontrado para venta {venta['id_venta']}", log_file)
                skipped_count += 1
                continue
            
            pg_cliente_id = id_mapping[sqlite_cliente_id]
            
            # Verificar si ya existe la venta (basado en fecha, hora y cliente)
            cursor_pg.execute("""
                SELECT COUNT(*) FROM ventas 
                WHERE id_cliente = %s AND fecha_venta = %s AND hora_venta = %s AND valor_total = %s
            """, (
                pg_cliente_id, venta['fecha_venta'], venta['hora_venta'], float(venta['valor_total'])
            ))
            
            if cursor_pg.fetchone()[0] > 0:
                if DEBUG:
                    log_message(f"Venta ya existe: cliente {pg_cliente_id}, fecha {venta['fecha_venta']}", log_file)
                skipped_count += 1
                continue
            
            # Insertar venta en PostgreSQL
            cursor_pg.execute("""
                INSERT INTO ventas (
                    id_cliente, fecha_venta, hora_venta, productos,
                    valor_total, descuento_aplicado, metodo_pago, vendedor, notas_venta
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                pg_cliente_id, venta['fecha_venta'], venta['hora_venta'],
                venta['productos'], float(venta['valor_total']), float(venta['descuento_aplicado']),
                venta['metodo_pago'], venta['vendedor'], venta['notas_venta']
            ))
            
            migrated_count += 1
            if migrated_count % 20 == 0:
                log_message(f"Migradas {migrated_count} de {total_ventas} ventas", log_file)
                pg_conn.commit()
            
        except Exception as e:
            error_count += 1
            log_message(f"Error al migrar venta {venta['id_venta']}: {e}", log_file)
            if DEBUG:
                import traceback
                traceback.print_exc()
    
    pg_conn.commit()
    log_message(f"Migración de ventas completada: {migrated_count} migradas, {skipped_count} omitidas, {error_count} errores", log_file)
    return migrated_count, skipped_count, error_count

def verify_migration(sqlite_conn, pg_conn, log_file):
    """Verifica que la migración se haya realizado correctamente"""
    log_message("Verificando migración...", log_file)
    
    cursor_sqlite = sqlite_conn.cursor()
    cursor_pg = pg_conn.cursor()
    
    # Verificar conteo de clientes
    cursor_sqlite.execute("SELECT COUNT(*) FROM clientes")
    sqlite_client_count = cursor_sqlite.fetchone()[0]
    
    cursor_pg.execute("SELECT COUNT(*) FROM clientes")
    pg_client_count = cursor_pg.fetchone()[0]
    
    # Verificar conteo de ventas
    cursor_sqlite.execute("SELECT COUNT(*) FROM ventas")
    sqlite_sales_count = cursor_sqlite.fetchone()[0]
    
    cursor_pg.execute("SELECT COUNT(*) FROM ventas")
    pg_sales_count = cursor_pg.fetchone()[0]
    
    log_message(f"Clientes en SQLite: {sqlite_client_count}", log_file)
    log_message(f"Clientes en PostgreSQL: {pg_client_count}", log_file)
    log_message(f"Ventas en SQLite: {sqlite_sales_count}", log_file)
    log_message(f"Ventas en PostgreSQL: {pg_sales_count}", log_file)
    
    # Calcular porcentajes de migración
    client_percent = (pg_client_count / sqlite_client_count * 100) if sqlite_client_count > 0 else 0
    sales_percent = (pg_sales_count / sqlite_sales_count * 100) if sqlite_sales_count > 0 else 0
    
    log_message(f"Porcentaje de migración de clientes: {client_percent:.2f}%", log_file)
    log_message(f"Porcentaje de migración de ventas: {sales_percent:.2f}%", log_file)
    
    if client_percent >= 95 and sales_percent >= 90:
        log_message("✅ Migración verificada exitosamente", log_file)
        return True
    else:
        log_message("⚠️ Migración incompleta. Se recomienda revisar errores", log_file)
        return False

def main():
    parser = argparse.ArgumentParser(description="Migración de SQLite a PostgreSQL para GestorCloud")
    parser.add_argument("--sqlite", default=DEFAULT_SQLITE_PATH, help=f"Ruta a la base de datos SQLite (por defecto: {DEFAULT_SQLITE_PATH})")
    parser.add_argument("--log", default=LOG_FILE, help=f"Archivo de registro (por defecto: {LOG_FILE})")
    parser.add_argument("--debug", action="store_true", help="Modo debug con mensajes detallados")
    
    args = parser.parse_args()
    
    if args.debug:
        global DEBUG
        DEBUG = True
        os.environ["DB_DEBUG"] = "true"
    
    # Verificar que la base de datos SQLite existe
    sqlite_path = args.sqlite
    if not os.path.exists(sqlite_path):
        print(f"Error: No se encontró la base de datos SQLite en {sqlite_path}")
        return 1
    
    with open(args.log, "a") as log_file:
        log_message("=== INICIANDO MIGRACIÓN DE SQLITE A POSTGRESQL ===", log_file)
        log_message(f"Base de datos SQLite: {sqlite_path}", log_file)
        log_message(f"PostgreSQL: {os.getenv('PG_HOST', 'localhost')}:{os.getenv('PG_PORT', '5432')}/{os.getenv('PG_DATABASE', 'gestorcloud')}", log_file)
        
        try:
            # Conectar a bases de datos
            log_message("Estableciendo conexiones...", log_file)
            sqlite_conn = get_sqlite_connection(sqlite_path)
            pg_conn = get_postgres_connection()
            
            # Crear esquema en PostgreSQL
            if not create_postgres_schema(pg_conn):
                log_message("❌ Error al crear esquema en PostgreSQL. Abortando migración.", log_file)
                return 1
            
            # Migrar datos
            clients_stats = migrate_clientes(sqlite_conn, pg_conn, log_file)
            sales_stats = migrate_ventas(sqlite_conn, pg_conn, log_file)
            
            # Verificar migración
            verify_migration(sqlite_conn, pg_conn, log_file)
            
            # Resumen
            log_message("\n=== RESUMEN DE MIGRACIÓN ===", log_file)
            log_message(f"Clientes: {clients_stats[0]} migrados, {clients_stats[1]} omitidos, {clients_stats[2]} errores", log_file)
            log_message(f"Ventas: {sales_stats[0]} migradas, {sales_stats[1]} omitidas, {sales_stats[2]} errores", log_file)
            log_message(f"Log completo disponible en: {args.log}", log_file)
            
            log_message("\n✅ Migración completada.", log_file)
            log_message("""
Próximos pasos:
1. Actualizar en web/app.py:
   from database import GestorCloudDB -> from database_postgres import GestorCloudDB
2. Configurar .env con las credenciales de PostgreSQL
3. Ejecutar la aplicación normalmente
            """, log_file)
            
        except ConnectionError as e:
            log_message(f"❌ Error de conexión: {e}", log_file)
            return 1
        except Exception as e:
            log_message(f"❌ Error inesperado: {e}", log_file)
            if DEBUG:
                import traceback
                traceback.print_exc(file=log_file)
            return 1
        finally:
            # Cerrar conexiones
            if 'sqlite_conn' in locals():
                sqlite_conn.close()
            if 'pg_conn' in locals():
                pg_conn.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())