"""
GestorCloud - Gestión de base de datos
Manejo de SQLite para persistencia de datos
"""

import sqlite3
import os
from typing import List, Optional, Tuple
from models import Cliente, Venta
from datetime import datetime

class GestorCloudDB:
    """Clase para manejar todas las operaciones de base de datos"""
    
    def __init__(self, db_path: str = "data/gestorcloud.db"):
        self.db_path = db_path
        self._crear_directorio_data()
        self._crear_tablas()
    
    def _crear_directorio_data(self):
        """Crea el directorio data si no existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _crear_tablas(self):
        """Crea las tablas necesarias en la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_completo TEXT NOT NULL,
                    edad INTEGER NOT NULL,
                    direccion TEXT NOT NULL,
                    correo TEXT UNIQUE NOT NULL,
                    telefono TEXT NOT NULL,
                    empresa TEXT DEFAULT '',
                    categoria TEXT DEFAULT 'Regular',
                    estado TEXT DEFAULT 'Activo',
                    fecha_registro TEXT NOT NULL,
                    ultima_actualizacion TEXT NOT NULL,
                    notas TEXT DEFAULT '',
                    valor_total_compras REAL DEFAULT 0.0,
                    numero_compras INTEGER DEFAULT 0,
                    ultima_compra TEXT DEFAULT '',
                    descuento_cliente REAL DEFAULT 0.0
                )
            """)
            
            # Tabla de ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cliente INTEGER NOT NULL,
                    fecha_venta TEXT NOT NULL,
                    hora_venta TEXT NOT NULL,
                    productos TEXT NOT NULL,
                    valor_total REAL NOT NULL,
                    descuento_aplicado REAL DEFAULT 0.0,
                    metodo_pago TEXT DEFAULT 'Efectivo',
                    vendedor TEXT DEFAULT '',
                    notas_venta TEXT DEFAULT '',
                    FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
                )
            """)
            
            conn.commit()
    
    # === OPERACIONES CON CLIENTES ===
    
    def agregar_cliente(self, cliente: Cliente) -> int:
        """Agrega un nuevo cliente y retorna su ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO clientes (
                        nombre_completo, edad, direccion, correo, telefono,
                        empresa, categoria, estado, fecha_registro, ultima_actualizacion,
                        notas, valor_total_compras, numero_compras, ultima_compra, descuento_cliente
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cliente.nombre_completo, cliente.edad, cliente.direccion,
                    cliente.correo, cliente.telefono, cliente.empresa,
                    cliente.categoria, cliente.estado, cliente.fecha_registro,
                    cliente.ultima_actualizacion, cliente.notas,
                    cliente.valor_total_compras, cliente.numero_compras,
                    cliente.ultima_compra, cliente.descuento_cliente
                ))
                
                cliente_id = cursor.lastrowid
                conn.commit()
                return cliente_id
                
            except sqlite3.IntegrityError:
                raise ValueError(f"Ya existe un cliente con el correo: {cliente.correo}")
    
    def obtener_cliente(self, id_cliente: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_cliente(row)
            return None
    
    def obtener_todos_clientes(self) -> List[Cliente]:
        """Obtiene todos los clientes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clientes ORDER BY nombre_completo")
            rows = cursor.fetchall()
            
            return [self._row_to_cliente(row) for row in rows]
    
    def buscar_clientes(self, termino: str) -> List[Cliente]:
        """Busca clientes por nombre, correo o empresa"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            termino_like = f"%{termino}%"
            
            cursor.execute("""
                SELECT * FROM clientes 
                WHERE nombre_completo LIKE ? 
                   OR correo LIKE ? 
                   OR empresa LIKE ?
                ORDER BY nombre_completo
            """, (termino_like, termino_like, termino_like))
            
            rows = cursor.fetchall()
            return [self._row_to_cliente(row) for row in rows]
    
    def actualizar_cliente(self, cliente: Cliente) -> bool:
        """Actualiza un cliente existente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cliente.actualizar_timestamp()
            
            cursor.execute("""
                UPDATE clientes SET
                    nombre_completo = ?, edad = ?, direccion = ?, correo = ?,
                    telefono = ?, empresa = ?, categoria = ?, estado = ?,
                    ultima_actualizacion = ?, notas = ?, valor_total_compras = ?,
                    numero_compras = ?, ultima_compra = ?, descuento_cliente = ?
                WHERE id_cliente = ?
            """, (
                cliente.nombre_completo, cliente.edad, cliente.direccion,
                cliente.correo, cliente.telefono, cliente.empresa,
                cliente.categoria, cliente.estado, cliente.ultima_actualizacion,
                cliente.notas, cliente.valor_total_compras, cliente.numero_compras,
                cliente.ultima_compra, cliente.descuento_cliente, cliente.id_cliente
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def eliminar_cliente(self, id_cliente: int) -> bool:
        """Elimina un cliente (solo si no tiene ventas)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Verificar si tiene ventas
            cursor.execute("SELECT COUNT(*) FROM ventas WHERE id_cliente = ?", (id_cliente,))
            if cursor.fetchone()[0] > 0:
                raise ValueError("No se puede eliminar un cliente con ventas registradas")
            
            cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
            conn.commit()
            return cursor.rowcount > 0
    
    # === OPERACIONES CON VENTAS ===
    
    def agregar_venta(self, venta: Venta) -> int:
        """Agrega una nueva venta y actualiza el cliente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insertar venta
            cursor.execute("""
                INSERT INTO ventas (
                    id_cliente, fecha_venta, hora_venta, productos,
                    valor_total, descuento_aplicado, metodo_pago, vendedor, notas_venta
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                venta.id_cliente, venta.fecha_venta, venta.hora_venta,
                venta.productos, venta.valor_total, venta.descuento_aplicado,
                venta.metodo_pago, venta.vendedor, venta.notas_venta
            ))
            
            venta_id = cursor.lastrowid
            
            # Actualizar cliente
            cliente = self.obtener_cliente(venta.id_cliente)
            if cliente:
                cliente.agregar_compra(venta.valor_total)
                self.actualizar_cliente(cliente)
            
            conn.commit()
            return venta_id
    
    def obtener_ventas_cliente(self, id_cliente: int) -> List[Venta]:
        """Obtiene todas las ventas de un cliente"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ventas 
                WHERE id_cliente = ? 
                ORDER BY fecha_venta DESC, hora_venta DESC
            """, (id_cliente,))
            
            rows = cursor.fetchall()
            return [self._row_to_venta(row) for row in rows]
    
    # === ESTADÍSTICAS Y REPORTES ===
    
    def obtener_estadisticas_generales(self) -> dict:
        """Obtiene estadísticas generales del negocio"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total clientes
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE estado = 'Activo'")
            total_clientes = cursor.fetchone()[0]
            
            # Total ventas del mes actual
            mes_actual = datetime.now().strftime("%Y-%m")
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(valor_total), 0) 
                FROM ventas 
                WHERE fecha_venta LIKE ?
            """, (f"{mes_actual}%",))
            
            ventas_mes, ingresos_mes = cursor.fetchone()
            
            # Clientes VIP
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE categoria = 'VIP'")
            clientes_vip = cursor.fetchone()[0]
            
            # Top 5 clientes por valor
            cursor.execute("""
                SELECT nombre_completo, valor_total_compras 
                FROM clientes 
                WHERE estado = 'Activo'
                ORDER BY valor_total_compras DESC 
                LIMIT 5
            """)
            top_clientes = cursor.fetchall()
            
            return {
                'total_clientes': total_clientes,
                'ventas_mes': ventas_mes,
                'ingresos_mes': float(ingresos_mes),
                'clientes_vip': clientes_vip,
                'top_clientes': top_clientes
            }
    
    def obtener_clientes_por_categoria(self) -> dict:
        """Obtiene conteo de clientes por categoría"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT categoria, COUNT(*) 
                FROM clientes 
                WHERE estado = 'Activo'
                GROUP BY categoria
            """)
            
            return dict(cursor.fetchall())
    
    # === MÉTODOS AUXILIARES ===
    
    def _row_to_cliente(self, row) -> Cliente:
        """Convierte una fila de DB a objeto Cliente"""
        cliente = Cliente(
            nombre_completo=row[1],
            edad=row[2],
            direccion=row[3],
            correo=row[4],
            telefono=row[5],
            empresa=row[6],
            categoria=row[7],
            estado=row[8],
            fecha_registro=row[9],
            ultima_actualizacion=row[10],
            notas=row[11],
            valor_total_compras=row[12],
            numero_compras=row[13],
            ultima_compra=row[14],
            descuento_cliente=row[15]
        )
        cliente.id_cliente = row[0]
        return cliente
    
    def _row_to_venta(self, row) -> Venta:
        """Convierte una fila de DB a objeto Venta"""
        venta = Venta(
            id_cliente=row[1],
            fecha_venta=row[2],
            hora_venta=row[3],
            productos=row[4],
            valor_total=row[5],
            descuento_aplicado=row[6],
            metodo_pago=row[7],
            vendedor=row[8],
            notas_venta=row[9]
        )
        venta.id_venta = row[0]
        return venta
        
    def obtener_todas_ventas(self) -> List[Venta]:
        """Obtiene todas las ventas registradas en el sistema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Unir con tabla clientes para obtener información del cliente
            cursor.execute("""
                SELECT v.*, c.nombre_completo, c.correo, c.categoria
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.fecha_venta DESC, v.hora_venta DESC
            """)
            
            rows = cursor.fetchall()
            ventas = []
            
            for row in rows:  # Corregido: usar rows en lugar de fetchall() de nuevo
                venta = Venta(
                    id_cliente=row[1],
                    fecha_venta=row[2],
                    hora_venta=row[3],
                    productos=row[4],
                    valor_total=row[5],
                    descuento_aplicado=row[6],
                    metodo_pago=row[7],
                    vendedor=row[8],
                    notas_venta=row[9]
                )
                venta.id_venta = row[0]
                
                # Añadir información del cliente
                venta.cliente = {
                    'nombre_completo': row[10] if row[10] else 'Cliente eliminado',
                    'correo': row[11] if row[11] else '',
                    'categoria': row[12] if row[12] else ''
                }
                
                ventas.append(venta)
                
            return ventas
            
    def obtener_estadisticas_ventas(self) -> dict:
        """Obtiene estadísticas específicas para la página de ventas"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total de ventas
            cursor.execute("SELECT COUNT(*) FROM ventas")
            total_ventas = cursor.fetchone()[0]
            
            # Ventas e ingresos del mes actual
            mes_actual = datetime.now().strftime("%Y-%m")
            cursor.execute(
                "SELECT COUNT(*), COALESCE(SUM(valor_total), 0) FROM ventas WHERE fecha_venta LIKE ?",
                (f"{mes_actual}%",)
            )
            result = cursor.fetchone()
            ventas_mes = result[0] or 0
            ingresos_mes = result[1] or 0
            
            # Promedio por venta
            cursor.execute("SELECT COALESCE(AVG(valor_total), 0) FROM ventas")
            promedio_venta = cursor.fetchone()[0] or 0
            
            return {
                'total_ventas': total_ventas,
                'ventas_mes': ventas_mes,
                'ingresos_mes': float(ingresos_mes),
                'promedio_venta': float(promedio_venta)
            }
            
    def obtener_ventas_del_dia(self, fecha: str = None) -> List[Venta]:
        """Obtiene todas las ventas de un día específico o del día actual"""
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d")
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Unir con tabla clientes para obtener información del cliente
            cursor.execute("""
                SELECT v.*, c.nombre_completo, c.correo, c.categoria
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                WHERE v.fecha_venta = ?
                ORDER BY v.hora_venta DESC
            """, (fecha,))
            
            rows = cursor.fetchall()
            ventas = []
            
            for row in rows:
                venta = Venta(
                    id_cliente=row[1],
                    fecha_venta=row[2],
                    hora_venta=row[3],
                    productos=row[4],
                    valor_total=row[5],
                    descuento_aplicado=row[6],
                    metodo_pago=row[7],
                    vendedor=row[8],
                    notas_venta=row[9]
                )
                venta.id_venta = row[0]
                
                # Añadir información del cliente
                venta.cliente = {
                    'nombre_completo': row[10] if row[10] else 'Cliente eliminado',
                    'correo': row[11] if row[11] else '',
                    'categoria': row[12] if row[12] else ''
                }
                
                ventas.append(venta)
                
            return ventas
    
    def hacer_backup(self, archivo_backup: str = None) -> str:
        """Crea un backup de la base de datos"""
        if not archivo_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_backup = f"data/backup_gestorcloud_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, archivo_backup)
        return archivo_backup