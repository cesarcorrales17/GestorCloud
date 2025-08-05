#!/usr/bin/env python3
"""
GestorCloud - Migración de SQLite a PostgreSQL
Script para migrar la base de datos existente a PostgreSQL
"""

import os
import sys
import argparse
import dotenv
from pathlib import Path

# Configuración de rutas
project_dir = Path(__file__).parent
os.chdir(project_dir)

# Cargar variables de entorno
dotenv.load_dotenv()

# Importar desde src
sys.path.append(str(project_dir))
from src.database_new import GestorCloudDB

def setup_env_file():
    """Configura el archivo .env si no existe"""
    env_file = project_dir / ".env"
    example_file = project_dir / ".env.example"
    
    if not env_file.exists() and example_file.exists():
        print("📝 Creando archivo .env desde .env.example")
        with open(example_file, "r") as src:
            with open(env_file, "w") as dest:
                dest.write(src.read())
        print("✅ Archivo .env creado. Por favor edítelo con sus credenciales de PostgreSQL.")
        return False
    return True

def check_postgres_connection():
    """Verifica la conexión con PostgreSQL"""
    try:
        # Forzar conexión a PostgreSQL
        os.environ["DB_TYPE"] = "postgres"
        db = GestorCloudDB()
        
        # Intentar ejecutar una consulta simple
        result = db.db.execute_query("SELECT 1 AS check")
        if result and result[0]['check'] == 1:
            db.close()
            return True
        
        db.close()
        return False
    except Exception as e:
        print(f"❌ Error al conectar con PostgreSQL: {e}")
        return False

def migrate_data(sqlite_path):
    """Migra los datos desde SQLite a PostgreSQL"""
    try:
        print(f"🔄 Iniciando migración desde {sqlite_path} a PostgreSQL...")
        
        # Forzar conexión a PostgreSQL
        os.environ["DB_TYPE"] = "postgres"
        db = GestorCloudDB()
        
        # Migrar datos
        db.migrar_desde_sqlite(sqlite_path)
        
        # Verificar la migración
        clientes = db.obtener_todos_clientes()
        ventas = db.obtener_todas_ventas()
        
        print(f"✅ Migración completada exitosamente.")
        print(f"📊 Datos migrados: {len(clientes)} clientes, {len(ventas)} ventas")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Migración de SQLite a PostgreSQL para GestorCloud")
    parser.add_argument("--sqlite", help="Ruta al archivo SQLite (por defecto: data/gestorcloud.db)", 
                        default="data/gestorcloud.db")
    parser.add_argument("--check", help="Solo verificar la conexión PostgreSQL sin migrar",
                        action="store_true")
    args = parser.parse_args()
    
    print("🚀 GestorCloud - Migración a PostgreSQL")
    print("-" * 50)
    
    # Verificar archivo .env
    if not setup_env_file():
        print("\n⚠️ Por favor configure sus credenciales de PostgreSQL en el archivo .env")
        print("   y ejecute este script nuevamente.")
        return
    
    # Si solo es verificación de conexión
    if args.check:
        print("🔍 Verificando conexión a PostgreSQL...")
        if check_postgres_connection():
            print("✅ Conexión a PostgreSQL establecida correctamente.")
        else:
            print("❌ No se pudo conectar a PostgreSQL. Verifique sus credenciales en .env")
        return
    
    # Verificar que existe el archivo SQLite
    if not os.path.exists(args.sqlite):
        print(f"❌ Error: No se encontró el archivo SQLite en {args.sqlite}")
        return
    
    # Verificar conexión a PostgreSQL
    print("🔍 Verificando conexión a PostgreSQL...")
    if not check_postgres_connection():
        print("❌ No se pudo conectar a PostgreSQL. Verifique sus credenciales en .env")
        return
    
    # Migrar datos
    if migrate_data(args.sqlite):
        print("\n🎉 Migración completada exitosamente.")
        print("\nPara utilizar PostgreSQL en la aplicación:")
        print("1. Asegúrese de que DB_TYPE=postgres en su archivo .env")
        print("2. Reinicie la aplicación")
    else:
        print("\n❌ La migración falló. Revise los errores anteriores.")

if __name__ == "__main__":
    main()