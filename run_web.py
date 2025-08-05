#!/usr/bin/env python3
"""
Servidor web para GestorCloud
Ejecuta la aplicación FastAPI en modo desarrollo
"""

import uvicorn
import sys
import os

# Cargar variables de entorno
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    print("⚠️ dotenv no está instalado. Las variables de entorno no se cargarán.")
    print("   Instale dotenv con: pip install python-dotenv")

# Agregar el directorio web al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

def main():
    """Función principal para ejecutar el servidor"""
    try:
        print("🚀 Iniciando GestorCloud Web Server...")
        print("📁 Directorio de trabajo:", os.getcwd())
        print("🌐 Servidor corriendo en: http://localhost:8000")
        print("⏹️  Para detener el servidor presiona Ctrl+C")
        print("-" * 50)
        
        # Ejecutar el servidor FastAPI
        uvicorn.run(
            "web.app:app",  # Ruta al archivo app.py en la carpeta web
            host="localhost",
            port=8000,
            reload=True,  # Recarga automática en desarrollo
            log_level="info",
            reload_dirs=["web"]  # Solo observar cambios en la carpeta web
        )
        
    except ImportError as e:
        print("❌ Error: No se pudo importar uvicorn o FastAPI")
        print("💡 Instala las dependencias con: pip install fastapi uvicorn")
        print(f"   Detalle del error: {e}")
        
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo web/app.py")
        print("💡 Asegúrate de que el archivo web/app.py existe")
        
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()