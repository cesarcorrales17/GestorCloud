"""
GestorCloud Web - Backend FastAPI
Sistema web para gestión de clientes
"""

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from typing import Optional, List
from datetime import datetime
import uvicorn
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio src al path para importar módulos
current_dir = os.path.dirname(__file__)
src_path = os.path.join(current_dir, '..', 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

try:
    from models import Cliente, Venta, CATEGORIAS_CLIENTE, ESTADOS_CLIENTE, METODOS_PAGO
    from database_postgres import GestorCloudDB
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    raise

# Inicializar FastAPI
app = FastAPI(
    title="GestorCloud",
    description="Sistema de gestión de clientes para pequeñas empresas",
    version="1.0.0"
)

# Configurar templates y archivos estáticos
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Dependency para obtener la base de datos
def get_db():
    """Dependency para obtener conexión a la base de datos"""
    try:
        db = GestorCloudDB()
        return db
    except Exception as e:
        logger.error(f"Error conectando a la base de datos: {e}")
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

# ===== MIDDLEWARE Y MANEJADORES DE ERRORES =====

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para errores 404"""
    return templates.TemplateResponse("404.html", {
        "request": request,
        "detail": exc.detail
    }, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Manejador personalizado para errores 500"""
    return templates.TemplateResponse("500.html", {
        "request": request,
        "detail": "Error interno del servidor"
    }, status_code=500)

# ===== RUTAS HTML =====

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: GestorCloudDB = Depends(get_db)):
    """Página principal - Dashboard"""
    try:
        stats = db.obtener_estadisticas_generales()
        categorias = db.obtener_clientes_por_categoria()
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "categorias": categorias,
            "page": "dashboard"
        })
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error cargando el dashboard")

@app.get("/clientes", response_class=HTMLResponse)
async def lista_clientes(request: Request, db: GestorCloudDB = Depends(get_db)):
    """Página de lista de clientes"""
    try:
        clientes = db.obtener_todos_clientes()
        
        return templates.TemplateResponse("clientes.html", {
            "request": request,
            "clientes": clientes,
            "page": "clientes"
        })
    except Exception as e:
        logger.error(f"Error obteniendo clientes: {e}")
        raise HTTPException(status_code=500, detail="Error cargando la lista de clientes")

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
async def detalle_cliente(request: Request, cliente_id: int, db: GestorCloudDB = Depends(get_db)):
    """Página de detalles de cliente"""
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalle del cliente {cliente_id}: {e}")
        raise HTTPException(status_code=500, detail="Error cargando los detalles del cliente")

@app.get("/clientes/{cliente_id}/editar", response_class=HTMLResponse)
async def editar_cliente_form(request: Request, cliente_id: int, db: GestorCloudDB = Depends(get_db)):
    """Formulario para editar cliente"""
    try:
        cliente = db.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return templates.TemplateResponse("cliente_form.html", {
            "request": request,
            "cliente": cliente,
            "categorias": CATEGORIAS_CLIENTE,
            "estados": ESTADOS_CLIENTE,
            "page": "clientes",
            "action": "editar"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cargando formulario de edición para cliente {cliente_id}: {e}")
        raise HTTPException(status_code=500, detail="Error cargando el formulario de edición")

@app.get("/ventas", response_class=HTMLResponse)
async def lista_ventas(request: Request, db: GestorCloudDB = Depends(get_db)):
    """Página de gestión de ventas"""
    try:
        ventas = db.obtener_todas_ventas()
        stats = db.obtener_estadisticas_ventas()
        
        return templates.TemplateResponse("ventas.html", {
            "request": request,
            "ventas": ventas,
            "stats": stats,
            "page": "ventas"
        })
    except Exception as e:
        logger.error(f"Error obteniendo ventas: {e}")
        raise HTTPException(status_code=500, detail="Error cargando las ventas")

@app.get("/ventas/hoy", response_class=HTMLResponse)
async def ventas_hoy(request: Request, db: GestorCloudDB = Depends(get_db)):
    """Página de ventas del día actual"""
    try:
        # Obtener fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        
        # Obtener las ventas del día
        ventas_del_dia = db.obtener_ventas_del_dia(fecha_actual)
        
        # Calcular estadísticas del día
        total_ventas = len(ventas_del_dia)
        ingresos_dia = sum(v.valor_total for v in ventas_del_dia)
        promedio_venta = ingresos_dia / total_ventas if total_ventas > 0 else 0
        
        stats_dia = {
            'total_ventas': total_ventas,
            'ingresos_dia': float(ingresos_dia),
            'promedio_venta': float(promedio_venta),
            'fecha': fecha_actual
        }
        
        return templates.TemplateResponse("ventas_hoy.html", {
            "request": request,
            "ventas": ventas_del_dia,
            "stats": stats_dia,
            "page": "ventas_hoy"
        })
    except Exception as e:
        logger.error(f"Error obteniendo ventas del día: {e}")
        raise HTTPException(status_code=500, detail="Error cargando las ventas del día")

@app.get("/ventas/nueva", response_class=HTMLResponse)
async def nueva_venta_form(request: Request, db: GestorCloudDB = Depends(get_db)):
    """Formulario para nueva venta"""
    try:
        clientes = db.obtener_todos_clientes()
        
        return templates.TemplateResponse("venta_form.html", {
            "request": request,
            "clientes": clientes,
            "metodos_pago": METODOS_PAGO,
            "page": "ventas"
        })
    except Exception as e:
        logger.error(f"Error cargando formulario de venta: {e}")
        raise HTTPException(status_code=500, detail="Error cargando el formulario de venta")

@app.get("/ventas/{venta_id}", response_class=HTMLResponse)
async def detalle_venta(request: Request, venta_id: int, db: GestorCloudDB = Depends(get_db)):
    """Página de detalle de una venta"""
    try:
        # Obtener la venta específica (método más eficiente)
        venta = db.obtener_venta(venta_id) if hasattr(db, 'obtener_venta') else None
        
        # Fallback al método actual si no existe obtener_venta
        if not venta:
            ventas = db.obtener_todas_ventas()
            venta = next((v for v in ventas if v.id_venta == venta_id), None)
        
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        
        return templates.TemplateResponse("venta_detalle.html", {
            "request": request,
            "venta": venta,
            "page": "ventas"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo detalle de venta {venta_id}: {e}")
        raise HTTPException(status_code=500, detail="Error cargando los detalles de la venta")

@app.get("/configuracion", response_class=HTMLResponse)
async def configuracion_page(request: Request):
    """Página de configuración del sistema"""
    return templates.TemplateResponse("configuracion.html", {
        "request": request,
        "page": "configuracion"
    })

@app.get("/reportes", response_class=HTMLResponse)
async def reportes_page(request: Request, db: GestorCloudDB = Depends(get_db)):
    """Página de reportes y análisis"""
    try:
        ventas = db.obtener_todas_ventas()
        clientes = db.obtener_todos_clientes()
        stats = db.obtener_estadisticas_generales()
        
        return templates.TemplateResponse("reportes.html", {
            "request": request,
            "ventas": ventas,
            "clientes": clientes,
            "stats": stats,
            "page": "reportes"
        })
    except Exception as e:
        logger.error(f"Error cargando reportes: {e}")
        raise HTTPException(status_code=500, detail="Error cargando los reportes")

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
    notas: str = Form(""),
    db: GestorCloudDB = Depends(get_db)
):
    """API para crear nuevo cliente"""
    try:
        # Validaciones básicas
        if not nombre_completo.strip():
            raise ValueError("El nombre completo es requerido")
        if edad < 0 or edad > 150:
            raise ValueError("La edad debe estar entre 0 y 150 años")
        if not correo.strip() or "@" not in correo:
            raise ValueError("El correo electrónico es inválido")
        
        cliente = Cliente(
            nombre_completo=nombre_completo.strip(),
            edad=edad,
            direccion=direccion.strip(),
            correo=correo.strip().lower(),
            telefono=telefono.strip(),
            empresa=empresa.strip(),
            categoria=categoria,
            notas=notas.strip()
        )
        
        cliente_id = db.agregar_cliente(cliente)
        
        return JSONResponse({
            "success": True,
            "message": "Cliente registrado exitosamente",
            "cliente_id": cliente_id
        })
        
    except ValueError as e:
        logger.warning(f"Error de validación creando cliente: {e}")
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=400)
    except Exception as e:
        logger.error(f"Error inesperado creando cliente: {e}")
        return JSONResponse({
            "success": False,
            "message": "Error interno del servidor"
        }, status_code=500)

@app.put("/api/clientes/{cliente_id}")
async def actualizar_cliente(
    cliente_id: int,
    nombre_completo: str = Form(...),
    edad: int = Form(...),
    direccion: str = Form(...),
    correo: str = Form(...),
    telefono: str = Form(...),
    empresa: str = Form(""),
    categoria: str = Form("Regular"),
    estado: str = Form("Activo"),
    notas: str = Form(""),
    db: GestorCloudDB = Depends(get_db)
):
    """API para actualizar un cliente"""
    try:
        # Obtener cliente existente
        cliente_existente = db.obtener_cliente(cliente_id)
        if not cliente_existente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Validaciones básicas
        if not nombre_completo.strip():
            raise ValueError("El nombre completo es requerido")
        if edad < 0 or edad > 150:
            raise ValueError("La edad debe estar entre 0 y 150 años")
        if not correo.strip() or "@" not in correo:
            raise ValueError("El correo electrónico es inválido")
        
        # Actualizar datos
        cliente_existente.nombre_completo = nombre_completo.strip()
        cliente_existente.edad = edad
        cliente_existente.direccion = direccion.strip()
        cliente_existente.correo = correo.strip().lower()
        cliente_existente.telefono = telefono.strip()
        cliente_existente.empresa = empresa.strip()
        cliente_existente.categoria = categoria
        cliente_existente.estado = estado
        cliente_existente.notas = notas.strip()
        
        # Guardar cambios
        db.actualizar_cliente(cliente_existente)
        
        return JSONResponse({
            "success": True,
            "message": "Cliente actualizado exitosamente",
            "cliente_id": cliente_id
        })
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Error de validación actualizando cliente {cliente_id}: {e}")
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=400)
    except Exception as e:
        logger.error(f"Error inesperado actualizando cliente {cliente_id}: {e}")
        return JSONResponse({
            "success": False,
            "message": "Error interno del servidor"
        }, status_code=500)

@app.delete("/api/clientes/{cliente_id}")
async def eliminar_cliente_api(cliente_id: int, db: GestorCloudDB = Depends(get_db)):
    """API para eliminar un cliente"""
    try:
        # Verificar que el cliente existe
        cliente = db.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Intentar eliminar el cliente
        result = db.eliminar_cliente(cliente_id)
        if result:
            return JSONResponse({
                "success": True,
                "message": "Cliente eliminado exitosamente"
            })
        else:
            return JSONResponse({
                "success": False,
                "message": "No se pudo eliminar el cliente"
            }, status_code=400)
            
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Error de validación eliminando cliente {cliente_id}: {e}")
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=400)
    except Exception as e:
        logger.error(f"Error inesperado eliminando cliente {cliente_id}: {e}")
        return JSONResponse({
            "success": False,
            "message": "Error interno del servidor"
        }, status_code=500)

@app.post("/api/ventas")
async def crear_venta(
    id_cliente: int = Form(...),
    productos: str = Form(...),
    valor_total: float = Form(...),
    descuento_aplicado: float = Form(0.0),
    metodo_pago: str = Form("Efectivo"),
    vendedor: str = Form(""),
    notas_venta: str = Form(""),
    db: GestorCloudDB = Depends(get_db)
):
    """API para crear nueva venta"""
    try:
        # Validaciones básicas
        if valor_total <= 0:
            raise ValueError("El valor total debe ser mayor a 0")
        if descuento_aplicado < 0 or descuento_aplicado > valor_total:
            raise ValueError("El descuento no puede ser negativo ni mayor al valor total")
        if not productos.strip():
            raise ValueError("Los productos son requeridos")
        
        # Verificar que el cliente existe
        cliente = db.obtener_cliente(id_cliente)
        if not cliente:
            raise ValueError("El cliente seleccionado no existe")
        
        venta = Venta(
            id_cliente=id_cliente,
            productos=productos.strip(),
            valor_total=valor_total,
            descuento_aplicado=descuento_aplicado,
            metodo_pago=metodo_pago,
            vendedor=vendedor.strip(),
            notas_venta=notas_venta.strip()
        )
        
        venta_id = db.agregar_venta(venta)
        
        return JSONResponse({
            "success": True,
            "message": "Venta registrada exitosamente",
            "venta_id": venta_id
        })
        
    except ValueError as e:
        logger.warning(f"Error de validación creando venta: {e}")
        return JSONResponse({
            "success": False,
            "message": str(e)
        }, status_code=400)
    except Exception as e:
        logger.error(f"Error inesperado creando venta: {e}")
        return JSONResponse({
            "success": False,
            "message": "Error interno del servidor"
        }, status_code=500)

# ===== API ENDPOINTS DE CONSULTA =====

@app.get("/api/clientes")
async def obtener_clientes(db: GestorCloudDB = Depends(get_db)):
    """API para obtener todos los clientes"""
    try:
        clientes = db.obtener_todos_clientes()
        return [cliente.to_dict() for cliente in clientes]
    except Exception as e:
        logger.error(f"Error obteniendo clientes API: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo los clientes")

@app.get("/api/clientes/buscar")
async def buscar_clientes(q: str, db: GestorCloudDB = Depends(get_db)):
    """API para buscar clientes"""
    try:
        if not q.strip():
            return []
        
        clientes = db.buscar_clientes(q.strip())
        return [{"id": c.id_cliente, "nombre": c.nombre_completo, "correo": c.correo} for c in clientes]
    except Exception as e:
        logger.error(f"Error buscando clientes: {e}")
        raise HTTPException(status_code=500, detail="Error en la búsqueda")

@app.get("/api/estadisticas")
async def obtener_estadisticas(db: GestorCloudDB = Depends(get_db)):
    """API para obtener estadísticas"""
    try:
        stats = db.obtener_estadisticas_generales()
        categorias = db.obtener_clientes_por_categoria()
        
        return {
            "stats": stats,
            "categorias": categorias
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo las estadísticas")

@app.get("/api/clientes/{cliente_id}/ventas")
async def obtener_ventas_cliente_api(cliente_id: int, db: GestorCloudDB = Depends(get_db)):
    """API para obtener ventas de un cliente"""
    try:
        # Verificar que el cliente existe
        cliente = db.obtener_cliente(cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        ventas = db.obtener_ventas_cliente(cliente_id)
        return [venta.to_dict() for venta in ventas]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo ventas del cliente {cliente_id}: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo las ventas del cliente")

@app.get("/api/ventas")
async def obtener_ventas(db: GestorCloudDB = Depends(get_db)):
    """API para obtener todas las ventas"""
    try:
        ventas = db.obtener_todas_ventas()
        return [venta.to_dict() for venta in ventas]
    except Exception as e:
        logger.error(f"Error obteniendo ventas API: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo las ventas")

# ===== ENDPOINTS DE UTILIDAD =====

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    try:
        db = GestorCloudDB()
        # Intentar una operación simple para verificar la conexión
        db.obtener_estadisticas_generales()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "database": "error",
            "error": str(e)
        }, status_code=503)

# ===== CONFIGURACIÓN Y STARTUP =====

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("🌟 Iniciando GestorCloud Web...")
    try:
        # Verificar conexión a la base de datos
        db = GestorCloudDB()
        stats = db.obtener_estadisticas_generales()
        logger.info(f"✅ Conexión a base de datos exitosa. Clientes: {stats.get('total_clientes', 0)}")
    except Exception as e:
        logger.error(f"❌ Error conectando a la base de datos: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("🔴 Cerrando GestorCloud Web...")

# ===== CONFIGURACIÓN PRINCIPAL =====

if __name__ == "__main__":
    print("🌟 Iniciando GestorCloud Web...")
    print("📊 Dashboard disponible en: http://localhost:8000")
    print("🔗 API docs en: http://localhost:8000/docs")
    print("📱 Ctrl+C para detener el servidor")
    
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )