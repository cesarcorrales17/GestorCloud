"""
GestorCloud Web - Backend FastAPI
Sistema web para gestión de clientes
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
from datetime import datetime
import uvicorn
import sys
import os

# Agregar el directorio src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Cliente, Venta, CATEGORIAS_CLIENTE, ESTADOS_CLIENTE, METODOS_PAGO
from database_postgres import GestorCloudDB

# Inicializar FastAPI
app = FastAPI(
    title="GestorCloud",
    description="Sistema de gestión de clientes para pequeñas empresas",
    version="1.0.0"
)

# Configurar templates y archivos estáticos
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Inicializar la base de datos (desactivada en modo desarrollo para frontend)
db = None
try:
    db = GestorCloudDB()
    print("✅ Conexión a PostgreSQL establecida")
except Exception as e:
    print(f"⚠️ Error al conectar a PostgreSQL: {e}")
    print("⚠️ Funcionando en modo demo (solo UI)")

# Simulación de datos para modo demo (frontend)
def obtener_datos_demo():
    """Función para generar datos de demostración"""
    from datetime import datetime, timedelta
    import random
    
    clientes_demo = [
        Cliente(
            id_cliente=1,
            nombre_completo="Juan Pérez",
            edad=35,
            direccion="Calle 123 #45-67",
            correo="juan@example.com",
            telefono="3001234567",
            empresa="Empresa ABC",
            categoria="VIP",
            fecha_registro=(datetime.now() - timedelta(days=100)).strftime("%Y-%m-%d"),
            valor_total_compras=1200000,
            numero_compras=5,
            ultima_compra=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")
        ),
        Cliente(
            id_cliente=2,
            nombre_completo="María López",
            edad=28,
            direccion="Avenida 45 #12-34",
            correo="maria@example.com",
            telefono="3109876543",
            empresa="Empresa XYZ",
            categoria="Regular",
            fecha_registro=(datetime.now() - timedelta(days=50)).strftime("%Y-%m-%d"),
            valor_total_compras=450000,
            numero_compras=3,
            ultima_compra=(datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        )
    ]
    
    ventas_demo = [
        Venta(
            id_venta=1,
            id_cliente=1,
            fecha_venta=(datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            productos="Producto A, Producto B",
            valor_total=500000,
            metodo_pago="Tarjeta Crédito",
            vendedor="Admin"
        ),
        Venta(
            id_venta=2,
            id_cliente=1,
            fecha_venta=(datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
            productos="Producto C",
            valor_total=300000,
            metodo_pago="Efectivo",
            vendedor="Admin"
        )
    ]
    
    estadisticas = {
        "total_clientes": 12,
        "clientes_vip": 3,
        "total_ventas": 28,
        "total_ingresos": 7800000,
        "promedio_venta": 280000,
        "ventas_mes": 8,
        "ingresos_mes": 2300000
    }
    
    return {
        "clientes": clientes_demo,
        "ventas": ventas_demo,
        "estadisticas": estadisticas
    }

# Rutas para las páginas principales
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Página principal - Dashboard"""
    stats = {}
    categorias = []
    
    if db:
        # Modo con base de datos
        stats = db.obtener_estadisticas_generales()
        categorias = db.obtener_clientes_por_categoria()
    else:
        # Modo demo
        demo_data = obtener_datos_demo()
        stats = demo_data["estadisticas"]
        categorias = [
            {"categoria": "VIP", "cantidad": 3},
            {"categoria": "Regular", "cantidad": 7},
            {"categoria": "Prospecto", "cantidad": 2},
            {"categoria": "Inactivo", "cantidad": 0}
        ]
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "titulo": "Dashboard",
        "stats": stats,
        "categorias": categorias
    })

@app.get("/clientes", response_class=HTMLResponse)
async def lista_clientes(request: Request):
    """Página de lista de clientes"""
    clientes = []
    
    if db:
        clientes = db.obtener_todos_clientes()
    else:
        clientes = obtener_datos_demo()["clientes"]
    
    return templates.TemplateResponse("clientes.html", {
        "request": request,
        "titulo": "Clientes",
        "clientes": clientes
    })

@app.get("/clientes/nuevo", response_class=HTMLResponse)
async def nuevo_cliente_form(request: Request):
    """Formulario para nuevo cliente"""
    return templates.TemplateResponse("cliente_form.html", {
        "request": request,
        "titulo": "Nuevo Cliente",
        "categorias": CATEGORIAS_CLIENTE,
        "estados": ESTADOS_CLIENTE,
        "accion": "nuevo"
    })

@app.get("/clientes/{cliente_id}", response_class=HTMLResponse)
async def detalle_cliente(request: Request, cliente_id: int):
    """Página de detalles de cliente"""
    cliente = None
    ventas = []
    
    if db:
        cliente = db.obtener_cliente(cliente_id)
        if cliente:
            ventas = db.obtener_ventas_por_cliente(cliente_id)
    else:
        demo_data = obtener_datos_demo()
        for c in demo_data["clientes"]:
            if c.id_cliente == cliente_id:
                cliente = c
                break
        if cliente:
            ventas = [v for v in demo_data["ventas"] if v.id_cliente == cliente_id]
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    return templates.TemplateResponse("cliente_detalle.html", {
        "request": request,
        "titulo": f"Cliente: {cliente.nombre_completo}",
        "cliente": cliente,
        "ventas": ventas
    })

@app.get("/clientes/{cliente_id}/editar", response_class=HTMLResponse)
async def editar_cliente_form(request: Request, cliente_id: int):
    """Formulario para editar cliente"""
    cliente = None
    
    if db:
        cliente = db.obtener_cliente(cliente_id)
    else:
        demo_data = obtener_datos_demo()
        for c in demo_data["clientes"]:
            if c.id_cliente == cliente_id:
                cliente = c
                break
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    return templates.TemplateResponse("cliente_form.html", {
        "request": request,
        "titulo": f"Editar Cliente: {cliente.nombre_completo}",
        "cliente": cliente,
        "categorias": CATEGORIAS_CLIENTE,
        "estados": ESTADOS_CLIENTE,
        "accion": "editar"
    })

@app.get("/ventas", response_class=HTMLResponse)
async def lista_ventas(request: Request):
    """Página de lista de ventas"""
    ventas = []
    
    if db:
        ventas = db.obtener_todas_ventas()
    else:
        ventas = obtener_datos_demo()["ventas"]
    
    return templates.TemplateResponse("ventas.html", {
        "request": request,
        "titulo": "Ventas",
        "ventas": ventas
    })

@app.get("/ventas/nuevo", response_class=HTMLResponse)
async def nueva_venta_form(request: Request):
    """Formulario para nueva venta"""
    clientes = []
    
    if db:
        clientes = db.obtener_todos_clientes()
    else:
        clientes = obtener_datos_demo()["clientes"]
    
    return templates.TemplateResponse("venta_form.html", {
        "request": request,
        "titulo": "Nueva Venta",
        "clientes": clientes,
        "metodos_pago": METODOS_PAGO,
        "accion": "nuevo"
    })

@app.get("/ventas/{venta_id}", response_class=HTMLResponse)
async def detalle_venta(request: Request, venta_id: int):
    """Página de detalles de venta"""
    venta = None
    cliente = None
    
    if db:
        venta = db.obtener_venta(venta_id)
        if venta:
            cliente = db.obtener_cliente(venta.id_cliente)
    else:
        demo_data = obtener_datos_demo()
        for v in demo_data["ventas"]:
            if v.id_venta == venta_id:
                venta = v
                for c in demo_data["clientes"]:
                    if c.id_cliente == venta.id_cliente:
                        cliente = c
                        break
                break
    
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
        
    return templates.TemplateResponse("venta_detalle.html", {
        "request": request,
        "titulo": f"Venta #{venta.id_venta}",
        "venta": venta,
        "cliente": cliente
    })

@app.get("/reportes", response_class=HTMLResponse)
async def reportes(request: Request):
    """Página de reportes"""
    stats = {}
    
    if db:
        stats = db.obtener_estadisticas_generales()
    else:
        stats = obtener_datos_demo()["estadisticas"]
    
    return templates.TemplateResponse("reportes.html", {
        "request": request,
        "titulo": "Reportes",
        "stats": stats
    })

# Rutas para autenticación y perfil (solo frontend)
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Página de inicio de sesión"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "titulo": "Iniciar Sesión"
    })

@app.get("/registro", response_class=HTMLResponse)
async def registro_form(request: Request):
    """Página de registro de usuario"""
    return templates.TemplateResponse("registro.html", {
        "request": request,
        "titulo": "Registrarse"
    })

@app.get("/perfil", response_class=HTMLResponse)
async def perfil_usuario(request: Request):
    """Página de perfil de usuario"""
    # Datos de usuario de demostración
    usuario_demo = {
        "nombre": "Admin",
        "email": "admin@gestorcloud.com",
        "rol": "Administrador",
        "fecha_registro": "2024-06-01"
    }
    
    return templates.TemplateResponse("perfil.html", {
        "request": request,
        "titulo": "Mi Perfil",
        "usuario": usuario_demo
    })

@app.get("/configuracion", response_class=HTMLResponse)
async def configuracion(request: Request):
    """Página de configuración"""
    return templates.TemplateResponse("configuracion.html", {
        "request": request,
        "titulo": "Configuración"
    })

# Rutas API para AJAX
@app.post("/api/clientes/nuevo", response_class=JSONResponse)
async def crear_cliente_api(cliente: dict):
    """API para crear cliente"""
    if not db:
        return {"success": True, "id_cliente": 3, "mensaje": "Cliente creado (modo demo)"}
    
    try:
        nuevo_cliente = Cliente.from_dict(cliente)
        id_cliente = db.insertar_cliente(nuevo_cliente)
        return {"success": True, "id_cliente": id_cliente, "mensaje": "Cliente creado correctamente"}
    except Exception as e:
        return {"success": False, "mensaje": f"Error al crear cliente: {str(e)}"}

@app.put("/api/clientes/{cliente_id}", response_class=JSONResponse)
async def actualizar_cliente_api(cliente_id: int, cliente: dict):
    """API para actualizar cliente"""
    if not db:
        return {"success": True, "mensaje": "Cliente actualizado (modo demo)"}
    
    try:
        cliente_obj = Cliente.from_dict(cliente)
        db.actualizar_cliente(cliente_id, cliente_obj)
        return {"success": True, "mensaje": "Cliente actualizado correctamente"}
    except Exception as e:
        return {"success": False, "mensaje": f"Error al actualizar cliente: {str(e)}"}

@app.delete("/api/clientes/{cliente_id}", response_class=JSONResponse)
async def eliminar_cliente_api(cliente_id: int):
    """API para eliminar cliente"""
    if not db:
        return {"success": True, "mensaje": "Cliente eliminado (modo demo)"}
    
    try:
        db.eliminar_cliente(cliente_id)
        return {"success": True, "mensaje": "Cliente eliminado correctamente"}
    except Exception as e:
        return {"success": False, "mensaje": f"Error al eliminar cliente: {str(e)}"}

@app.post("/api/ventas/nuevo", response_class=JSONResponse)
async def crear_venta_api(venta: dict):
    """API para crear venta"""
    if not db:
        return {"success": True, "id_venta": 3, "mensaje": "Venta registrada (modo demo)"}
    
    try:
        nueva_venta = Venta(**venta)
        id_venta = db.insertar_venta(nueva_venta)
        return {"success": True, "id_venta": id_venta, "mensaje": "Venta registrada correctamente"}
    except Exception as e:
        return {"success": False, "mensaje": f"Error al registrar venta: {str(e)}"}

# Función para iniciar la aplicación (usado por run_web.py)
def start():
    """Inicia la aplicación FastAPI"""
    uvicorn.run(app, host="localhost", port=8000, reload=True)

if __name__ == "__main__":
    start()