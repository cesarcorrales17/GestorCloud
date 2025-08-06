"""
Script para probar la conexión a la base de datos PostgreSQL
"""
import os
import sys
import psycopg2
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

def test_connection():
    """Prueba la conexión a la base de datos PostgreSQL"""
    try:
        # Obtener configuración desde variables de entorno
        db_name = os.environ.get('DB_NAME', 'gestorcloud')
        db_user = os.environ.get('DB_USER', 'postgres')
        db_password = os.environ.get('DB_PASSWORD', '123')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')

        
        print(f"⚙️ Intentando conectar a: {db_host}:{db_port}/{db_name}")
        
        # Intentar conexión
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            client_encoding='UTF8'
        )
        
        print("✅ Conexión exitosa a la base de datos PostgreSQL!")
        
        # Probar consulta simple
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"📊 Versión de PostgreSQL: {version[0]}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Probando conexión a PostgreSQL...")
    success = test_connection()
    if not success:
        print("\n💡 Sugerencias:")
        print("1. Verifica que PostgreSQL esté instalado y en ejecución")
        print("2. Revisa las credenciales en el archivo .env")
        print("3. Verifica que exista la base de datos 'gestorcloud'")
        print("\nPara crear la base de datos manualmente:")
        print("  $ psql -U postgres")
        print("  postgres=# CREATE DATABASE gestorcloud;")
        print("  postgres=# \\q")
    sys.exit(0 if success else 1)