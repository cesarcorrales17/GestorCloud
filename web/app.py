"""
GestorCloud Web - Backend FastAPI
Sistema web para gestión de clientes
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List
import uvicorn
import sys
import os

# Agregar el directorio src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Cliente, Venta, CATEGORIAS_CLIENTE, ESTADOS_CLIENTE, METODOS_PAGO
from database import GestorCloudDB

# Inicializar FastAPI
app = FastAPI(
    title="GestorCloud",
    description="Sistema de gestión de clientes para pequeñas empresas",
    version="1.0.0"
)

# Configurar templates y archivos estáticos
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Inicializar base de datos
db = GestorCloudDB()

# ===== RUTAS HTML =====

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Página principal - Dashboard"""
    stats = db.obtener_estadisticas_generales()
    categorias = db.obtener_clientes_por_categoria()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "categorias": categorias,
        "page": "dashboard"
    })

@app.get("/clientes", response_class=HTMLResponse)
async def lista_clientes(request: Request):
    """Página de lista de clientes"""
    clientes = db.obtener_todos_clientes()
    
    return templates.TemplateResponse("clientes.html", {
        "request": request,
        "clientes": clientes,
        "page": "clientes"
    })

@app.get("/clientes/nuevo", response_class=HTMLResponse)
async def nuevo_cliente_form(request: Request):
    """Formulario para nuevo cliente"""
    return templates.TemplateResponse("cliente_form.html", {
        "request": request,
        "categorias": CATEGORIAS_CLIENTE,
        "estados": ESTADOS_CLIENTE,
        "page": "clientes",
        "action": "nuevo"
    })

@app.get("/clientes/{cliente_id}", response_class=HTMLResponse)
async def detalle_cliente(request: Request, cliente_id: int):
    """Página de detalles de cliente"""
    cliente = db.obtener_cliente(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    ventas = db.obtener_ventas_cliente(cliente_id)
    
    return templates.TemplateResponse("cliente_detalle.html", {
        "request": request,
        "cliente": cliente,
        "ventas": ventas,
        "page": "clientes"
    })

@app.get("/ventas", response_class=HTMLResponse)
async def lista_ventas(request: Request):
    """Página de gestión de ventas"""
    return templates.TemplateResponse("ventas.html", {
        "request": request,
        "page": "ventas"
    })

@app.get("/ventas/nueva", response_class=HTMLResponse)
async def nueva_venta_form(request: Request):
    """Formulario para nueva venta"""
    clientes = db.obtener_todos_clientes()
    
    return templates.TemplateResponse("venta_form.html", {
        "request": request,
        "clientes": clientes,
        "metodos_pago": METODOS_PAGO,
        "page": "ventas"
    })

# ===== API ENDPOINTS =====

@app.post("/api/clientes")
async def crear_cliente(
    nombre_completo: str = Form(...),
    edad: int = Form(...),
    direccion: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    empresa: str = Form(""),
    categoria: str = Form("Regular"),
    notas: str = Form("")
):
    """API para crear nuevo cliente"""
    try:
        cliente = Cliente(
            nombre_completo=nombre_completo,
            edad=edad,
            direccion=direccion,
            correo=correo,
            telefono=telefono,
            empresa=empresa,
            categoria=categoria,
            notas=notas
        )
        
        cliente_id = db.agregar_cliente(cliente)
        
        return JSONResponse({
            "success": True,
            "message": "Cliente registrado exitosamente",
            "cliente_id": cliente_id
        })
        
    except ValueError as e:
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=400)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Error inesperado: {str(e)}"
        }, status_code=500)

@app.post("/api/ventas")
async def crear_venta(
    id_cliente: int = Form(...),
    productos: str = Form(...),
    valor_total: float = Form(...),
    descuento_aplicado: float = Form(0.0),
    metodo_pago: str = Form("Efectivo"),
    vendedor: str = Form(""),
    notas_venta: str = Form("")
):
    """API para crear nueva venta"""
    try:
        venta = Venta(
            id_cliente=id_cliente,
            productos=productos,
            valor_total=valor_total,
            descuento_aplicado=descuento_aplicado,
            metodo_pago=metodo_pago,
            vendedor=vendedor,
            notas_venta=notas_venta
        )
        
        venta_id = db.agregar_venta(venta)
        
        return JSONResponse({
            "success": True,
            "message": "Venta registrada exitosamente",
            "venta_id": venta_id
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"Error: {str(e)}"
        }, status_code=500)

@app.get("/api/clientes")
async def obtener_clientes():
    """API para obtener todos los clientes"""
    clientes = db.obtener_todos_clientes()
    return [cliente.to_dict() for cliente in clientes]

@app.get("/api/clientes/buscar")
async def buscar_clientes(q: str):
    """API para buscar clientes"""
    clientes = db.buscar_clientes(q)
    return [{"id": c.id_cliente, "nombre": c.nombre_completo, "correo": c.correo} for c in clientes]

@app.get("/api/estadisticas")
async def obtener_estadisticas():
    """API para obtener estadísticas"""
    stats = db.obtener_estadisticas_generales()
    categorias = db.obtener_clientes_por_categoria()
    
    return {
        "stats": stats,
        "categorias": categorias
    }

@app.get("/api/clientes/{cliente_id}/ventas")
async def obtener_ventas_cliente_api(cliente_id: int):
    """API para obtener ventas de un cliente"""
    ventas = db.obtener_ventas_cliente(cliente_id)
    return [venta.to_dict() for venta in ventas]

# ===== CONFIGURACIÓN =====

if __name__ == "__main__":
    print("🌟 Iniciando GestorCloud Web...")
    print("📊 Dashboard disponible en: http://localhost:8000")
    print("📱 Ctrl+C para detener el servidor")
    
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )