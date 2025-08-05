#!/bin/bash

# Script para configurar el entorno de GestorCloud
# Configuración automática para PostgreSQL y SQLite

echo "🚀 GestorCloud - Configuración de Entorno"
echo "=========================================="
echo ""

# Verificar si estamos en un entorno virtual
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  No se detectó un entorno virtual activo."
    echo "   Se recomienda ejecutar este script dentro de un entorno virtual."
    echo ""
    read -p "¿Desea continuar de todas formas? (s/n): " continuar
    if [[ "$continuar" != "s" && "$continuar" != "S" ]]; then
        echo "Instalación cancelada. Por favor, active un entorno virtual e inténtelo de nuevo."
        exit 1
    fi
fi

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error al instalar las dependencias."
    exit 1
fi
echo "✅ Dependencias instaladas correctamente."
echo ""

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "🔧 Creando archivo .env con configuración predeterminada..."
    cp .env.example .env
    echo "✅ Archivo .env creado correctamente."
else
    echo "ℹ️ El archivo .env ya existe. Se mantiene la configuración actual."
fi
echo ""

# Verificar configuración de base de datos
source .env 2>/dev/null || true
DB_TYPE=${DB_TYPE:-"sqlite"}

echo "🔍 Configuración de base de datos actual: $DB_TYPE"
echo ""

# Preguntar si se desea ejecutar la migración de datos
if [ "$DB_TYPE" = "postgres" ]; then
    echo "ℹ️ La configuración está establecida para usar PostgreSQL."
    read -p "¿Desea ejecutar la migración de datos desde SQLite a PostgreSQL? (s/n): " migrar
    if [[ "$migrar" == "s" || "$migrar" == "S" ]]; then
        echo "🔄 Ejecutando migración de datos..."
        python migrate_to_postgres.py
        if [ $? -eq 0 ]; then
            echo "✅ Migración completada exitosamente."
        else
            echo "❌ Error en la migración."
        fi
    fi
fi
echo ""

# Realizar una prueba de conexión
echo "🧪 Realizando prueba de conexión a la base de datos..."
python test_db_connection.py
echo ""

echo "🎉 Configuración completada!"
echo "Para ejecutar la aplicación web, use: python run_web.py"
echo "Para más información, consulte README.md y README_POSTGRES.md"