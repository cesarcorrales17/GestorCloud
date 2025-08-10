"""
GestorCloud - Modelos de datos
Sistema de gestión de clientes para pequeñas empresas
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import re

@dataclass
class Cliente:
    """Modelo de cliente empresarial mejorado"""
    # Datos básicos
    nombre_completo: str
    edad: int
    direccion: str
    correo: str
    telefono: str
    
    # Nuevos campos CRM
    id_cliente: Optional[int] = None
    empresa: str = ""
    categoria: str = "Regular"  # VIP, Regular, Prospecto, Inactivo
    estado: str = "Activo"     # Activo, Inactivo, Prospecto
    fecha_registro: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    ultima_actualizacion: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    notas: str = ""
    valor_total_compras: float = 0.0
    numero_compras: int = 0
    ultima_compra: Optional[str] = None  # Cambiado de "" a None para PostgreSQL
    descuento_cliente: float = 0.0
    
    def __post_init__(self):
        """Validaciones automáticas al crear el cliente"""
        if not self.es_correo_valido():
            raise ValueError(f"Correo electrónico inválido: {self.correo}")
        
        if not self.es_telefono_valido():
            raise ValueError(f"Teléfono inválido: {self.telefono}")
    
    def es_correo_valido(self) -> bool:
        """Valida el formato del correo electrónico"""
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, self.correo) is not None
    
    def es_telefono_valido(self) -> bool:
        """Valida el formato del teléfono"""
        # Acepta números con 7-15 dígitos, con o sin espacios/guiones
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', str(self.telefono))
        return telefono_limpio.isdigit() and 7 <= len(telefono_limpio) <= 15
    
    def actualizar_timestamp(self):
        """Actualiza la fecha de última modificación"""
        self.ultima_actualizacion = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def agregar_compra(self, valor: float):
        """Registra una nueva compra del cliente"""
        self.valor_total_compras += valor
        self.numero_compras += 1
        self.ultima_compra = datetime.now().strftime("%Y-%m-%d")
        self.actualizar_timestamp()
        
        # Auto-promoción a VIP si supera cierto valor
        if self.valor_total_compras >= 1000000 and self.categoria != "VIP":  # 1M COP
            self.categoria = "VIP"
            self.descuento_cliente = 0.05  # 5% descuento
    
    def es_cliente_vip(self) -> bool:
        """Verifica si el cliente es VIP"""
        return self.categoria == "VIP"
    
    def dias_desde_ultima_compra(self) -> int:
        """Calcula días desde la última compra"""
        if not self.ultima_compra:
            return -1
        
        try:
            fecha_ultima = datetime.strptime(self.ultima_compra, "%Y-%m-%d")
            return (datetime.now() - fecha_ultima).days
        except:
            return -1
    
    def to_dict(self) -> dict:
        """Convierte el cliente a diccionario para JSON/DB"""
        return {
            'id_cliente': self.id_cliente,
            'nombre_completo': self.nombre_completo,
            'edad': self.edad,
            'direccion': self.direccion,
            'correo': self.correo,
            'telefono': self.telefono,
            'empresa': self.empresa,
            'categoria': self.categoria,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro,
            'ultima_actualizacion': self.ultima_actualizacion,
            'notas': self.notas,
            'valor_total_compras': self.valor_total_compras,
            'numero_compras': self.numero_compras,
            'ultima_compra': self.ultima_compra,
            'descuento_cliente': self.descuento_cliente
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un cliente desde un diccionario"""
        return cls(**data)

@dataclass
class Venta:
    """Modelo para registrar ventas"""
    id_venta: Optional[int] = None
    id_cliente: int = 0
    fecha_venta: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    hora_venta: str = field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    productos: str = ""
    valor_total: float = 0.0
    descuento_aplicado: float = 0.0
    metodo_pago: str = "Efectivo"  # Efectivo, Tarjeta, Transferencia
    vendedor: str = ""
    notas_venta: str = ""
    cliente: dict = field(default_factory=dict)  # Información del cliente para mostrar en la lista
    
    @property
    def fecha(self):
        """Devuelve la fecha como objeto datetime para facilitar el formateo en las plantillas"""
        try:
            return datetime.strptime(f"{self.fecha_venta} {self.hora_venta}", "%Y-%m-%d %H:%M")
        except:
            return datetime.now()
    
    def to_dict(self) -> dict:
        """Convierte la venta a diccionario"""
        return {
            'id_venta': self.id_venta,
            'id_cliente': self.id_cliente,
            'fecha_venta': self.fecha_venta,
            'hora_venta': self.hora_venta,
            'productos': self.productos,
            'valor_total': self.valor_total,
            'descuento_aplicado': self.descuento_aplicado,
            'metodo_pago': self.metodo_pago,
            'vendedor': self.vendedor,
            'notas_venta': self.notas_venta,
            'cliente': self.cliente
        }

# Constantes para categorías y estados
CATEGORIAS_CLIENTE = ["Prospecto", "Regular", "VIP", "Inactivo"]
ESTADOS_CLIENTE = ["Activo", "Inactivo", "Prospecto"]
METODOS_PAGO = ["Efectivo", "Tarjeta Débito", "Tarjeta Crédito", "Transferencia"]