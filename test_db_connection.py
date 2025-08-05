#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos
Permite verificar que tanto SQLite como PostgreSQL funcionan correctamente
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
sys.path.append(str(project_dir / "src"))

def test_sqlite():
    """Prueba la conexión a SQLite"""
    try:
        # Forzar conexión a SQLite
        os.environ["DB_TYPE"] = "sqlite"
        from database_new import GestorCloudDB
        
        print("🔍 Probando conexión a SQLite...")
        db = GestorCloudDB()
        
        # Ejecutar una consulta simple
        num_clientes = len(db.obtener_todos_clientes())
        num_ventas = len(db.obtener_todas_ventas())
        
        print(f"✅ Conexión a SQLite exitosa!")
        print(f"📊 La base de datos contiene {num_clientes} clientes y {num_ventas} ventas")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Error al conectar con SQLite: {e}")
        return False

def test_postgres():
    """Prueba la conexión a PostgreSQL"""
    try:
        # Forzar conexión a PostgreSQL
        os.environ["DB_TYPE"] = "postgres"
        from database_new import GestorCloudDB
        
        print("🔍 Probando conexión a PostgreSQL...")
        db = GestorCloudDB()
        
        # Ejecutar una consulta simple
        try:
            num_clientes = len(db.obtener_todos_clientes())
            num_ventas = len(db.obtener_todas_ventas())
            
            print(f"✅ Conexión a PostgreSQL exitosa!")
            print(f"📊 La base de datos contiene {num_clientes} clientes y {num_ventas} ventas")
        except Exception as e:
            print(f"⚠️ Conexión establecida pero error al consultar datos: {e}")
            print("   Es posible que necesite migrar los datos desde SQLite.")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Error al conectar con PostgreSQL: {e}")
        print("   Asegúrese de que PostgreSQL esté en ejecución y las credenciales sean correctas.")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Probar conexión a bases de datos para GestorCloud")
    parser.add_argument("--sqlite", help="Probar conexión a SQLite", action="store_true")
    parser.add_argument("--postgres", help="Probar conexión a PostgreSQL", action="store_true")
    args = parser.parse_args()
    
    # Si no se especifica ninguna, probar ambas
    if not args.sqlite and not args.postgres:
        args.sqlite = True
        args.postgres = True
    
    print("🚀 GestorCloud - Test de Conexión a Base de Datos")
    print("-" * 50)
    
    results = []
    
    if args.sqlite:
        results.append(("SQLite", test_sqlite()))
        print()
        
    if args.postgres:
        results.append(("PostgreSQL", test_postgres()))
    
    print("\n" + "=" * 50)
    print("📋 Resumen de resultados:")
    for db_type, success in results:
        status = "✅ OK" if success else "❌ FALLÓ"
        print(f"{db_type}: {status}")

if __name__ == "__main__":
    main()