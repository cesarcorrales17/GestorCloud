"""
GestorCloud - Gestión de base de datos
Implementación para PostgreSQL
"""

import os
import psycopg2
import psycopg2.extras
from typing import List, Optional, Dict, Any
from models import Cliente, Venta
from datetime import datetime
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

class GestorCloudDB:
    """Clase para manejar todas las operaciones de base de datos en PostgreSQL"""
    
    def __init__(self):
        # Obtener configuración desde variables de entorno
        self.db_name = os.environ.get('PG_DATABASE', 'gestorcloud')
        self.db_user = os.environ.get('PG_USER', 'postgres')
        self.db_password = os.environ.get('PG_PASSWORD', 'postgres')
        self.db_host = os.environ.get('PG_HOST', 'localhost')
        self.db_port = os.environ.get('PG_PORT', '5432')
        
        # Inicializar la base de datos
        self._crear_tablas()
        
    def _get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )
    
    def _crear_tablas(self):
        """Crea las tablas necesarias en la base de datos"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Tabla de clientes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clientes (
                        id_cliente SERIAL PRIMARY KEY,
                        nombre_completo TEXT NOT NULL,
                        edad INTEGER NOT NULL,
                        direccion TEXT NOT NULL,
                        correo TEXT UNIQUE NOT NULL,
                        telefono TEXT NOT NULL,
                        empresa TEXT DEFAULT '',
                        categoria TEXT DEFAULT 'Regular',
                        estado TEXT DEFAULT 'Activo',
                        fecha_registro DATE NOT NULL,
                        ultima_actualizacion TIMESTAMP NOT NULL,
                        notas TEXT DEFAULT '',
                        valor_total_compras DECIMAL(12,2) DEFAULT 0.0,
                        numero_compras INTEGER DEFAULT 0,
                        ultima_compra DATE,
                        descuento_cliente DECIMAL(4,2) DEFAULT 0.0
                    )
                """)
                
                # Tabla de ventas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ventas (
                        id_venta SERIAL PRIMARY KEY,
                        id_cliente INTEGER NOT NULL,
                        fecha_venta DATE NOT NULL,
                        hora_venta TIME NOT NULL,
                        productos TEXT NOT NULL,
                        valor_total DECIMAL(12,2) NOT NULL,
                        descuento_aplicado DECIMAL(4,2) DEFAULT 0.0,
                        metodo_pago TEXT DEFAULT 'Efectivo',
                        vendedor TEXT DEFAULT '',
                        notas_venta TEXT DEFAULT '',
                        FOREIGN KEY (id_cliente) REFERENCES clientes (id_cliente)
                    )
                """)
                
                # Crear índices para mejorar el rendimiento
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente_nombre ON clientes(nombre_completo)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente_correo ON clientes(correo)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente_categoria ON clientes(categoria)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_venta_fecha ON ventas(fecha_venta)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_venta_cliente ON ventas(id_cliente)")
                
                conn.commit()
    
    # === OPERACIONES CON CLIENTES ===
    
    def agregar_cliente(self, cliente: Cliente) -> int:
        """Agrega un nuevo cliente y retorna su ID"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                
                try:
                    cursor.execute("""
                        INSERT INTO clientes (
                            nombre_completo, edad, direccion, correo, telefono,
                            empresa, categoria, estado, fecha_registro, ultima_actualizacion,
                            notas, valor_total_compras, numero_compras, ultima_compra, descuento_cliente
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id_cliente
                    """, (
                        cliente.nombre_completo, cliente.edad, cliente.direccion,
                        cliente.correo, cliente.telefono, cliente.empresa,
                        cliente.categoria, cliente.estado, cliente.fecha_registro,
                        cliente.ultima_actualizacion, cliente.notas,
                        cliente.valor_total_compras, cliente.numero_compras,
                        cliente.ultima_compra, cliente.descuento_cliente
                    ))
                    
                    cliente_id = cursor.fetchone()[0]
                    conn.commit()
                    return cliente_id
                    
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    raise ValueError(f"Ya existe un cliente con el correo: {cliente.correo}")
    
    def obtener_cliente(self, id_cliente: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_cliente(row)
                return None
    
    def obtener_todos_clientes(self) -> List[Cliente]:
        """Obtiene todos los clientes"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("SELECT * FROM clientes ORDER BY nombre_completo")
                rows = cursor.fetchall()
                
                return [self._row_to_cliente(row) for row in rows]
    
    def buscar_clientes(self, termino: str) -> List[Cliente]:
        """Busca clientes por nombre, correo o empresa"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                termino_like = f"%{termino}%"
                
                cursor.execute("""
                    SELECT * FROM clientes 
                    WHERE nombre_completo ILIKE %s 
                       OR correo ILIKE %s 
                       OR empresa ILIKE %s
                    ORDER BY nombre_completo
                """, (termino_like, termino_like, termino_like))
                
                rows = cursor.fetchall()
                return [self._row_to_cliente(row) for row in rows]
    
    def actualizar_cliente(self, cliente: Cliente) -> bool:
        """Actualiza un cliente existente"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                
                cliente.actualizar_timestamp()
                
                cursor.execute("""
                    UPDATE clientes SET
                        nombre_completo = %s, edad = %s, direccion = %s, correo = %s,
                        telefono = %s, empresa = %s, categoria = %s, estado = %s,
                        ultima_actualizacion = %s, notas = %s, valor_total_compras = %s,
                        numero_compras = %s, ultima_compra = %s, descuento_cliente = %s
                    WHERE id_cliente = %s
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
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Verificar si tiene ventas
                cursor.execute("SELECT COUNT(*) FROM ventas WHERE id_cliente = %s", (id_cliente,))
                if cursor.fetchone()[0] > 0:
                    raise ValueError("No se puede eliminar un cliente con ventas registradas")
                
                cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
                conn.commit()
                return cursor.rowcount > 0
    
    # === OPERACIONES CON VENTAS ===
    
    def agregar_venta(self, venta: Venta) -> int:
        """Agrega una nueva venta y actualiza el cliente"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Insertar venta
                cursor.execute("""
                    INSERT INTO ventas (
                        id_cliente, fecha_venta, hora_venta, productos,
                        valor_total, descuento_aplicado, metodo_pago, vendedor, notas_venta
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_venta
                """, (
                    venta.id_cliente, venta.fecha_venta, venta.hora_venta,
                    venta.productos, venta.valor_total, venta.descuento_aplicado,
                    venta.metodo_pago, venta.vendedor, venta.notas_venta
                ))
                
                venta_id = cursor.fetchone()[0]
                
                # Actualizar cliente
                cliente = self.obtener_cliente(venta.id_cliente)
                if cliente:
                    cliente.agregar_compra(venta.valor_total)
                    self.actualizar_cliente(cliente)
                
                conn.commit()
                return venta_id
    
    def obtener_ventas_cliente(self, id_cliente: int) -> List[Venta]:
        """Obtiene todas las ventas de un cliente"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM ventas 
                    WHERE id_cliente = %s 
                    ORDER BY fecha_venta DESC, hora_venta DESC
                """, (id_cliente,))
                
                rows = cursor.fetchall()
                return [self._row_to_venta(row) for row in rows]
    
    # === ESTADÍSTICAS Y REPORTES ===
    
    def obtener_estadisticas_generales(self) -> dict:
        """Obtiene estadísticas generales del negocio"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Total clientes
                cursor.execute("SELECT COUNT(*) FROM clientes WHERE estado = 'Activo'")
                total_clientes = cursor.fetchone()[0]
                
                # Total ventas del mes actual
                mes_actual = datetime.now().strftime("%Y-%m")
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(valor_total), 0) 
                    FROM ventas 
                    WHERE TO_CHAR(fecha_venta, 'YYYY-MM') = %s
                """, (mes_actual,))
                
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
                    'ventas_mes': ventas_mes or 0,
                    'ingresos_mes': float(ingresos_mes or 0),
                    'clientes_vip': clientes_vip,
                    'top_clientes': top_clientes
                }
    
    def obtener_clientes_por_categoria(self) -> dict:
        """Obtiene conteo de clientes por categoría"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
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
            nombre_completo=row['nombre_completo'],
            edad=row['edad'],
            direccion=row['direccion'],
            correo=row['correo'],
            telefono=row['telefono'],
            empresa=row['empresa'],
            categoria=row['categoria'],
            estado=row['estado'],
            fecha_registro=str(row['fecha_registro']),
            ultima_actualizacion=str(row['ultima_actualizacion']),
            notas=row['notas'],
            valor_total_compras=float(row['valor_total_compras']) if row['valor_total_compras'] else 0.0,
            numero_compras=row['numero_compras'],
            ultima_compra=str(row['ultima_compra']) if row['ultima_compra'] else '',
            descuento_cliente=float(row['descuento_cliente']) if row['descuento_cliente'] else 0.0
        )
        cliente.id_cliente = row['id_cliente']
        return cliente
    
    def _row_to_venta(self, row) -> Venta:
        """Convierte una fila de DB a objeto Venta"""
        venta = Venta(
            id_cliente=row['id_cliente'],
            fecha_venta=str(row['fecha_venta']),
            hora_venta=str(row['hora_venta']),
            productos=row['productos'],
            valor_total=float(row['valor_total']),
            descuento_aplicado=float(row['descuento_aplicado']),
            metodo_pago=row['metodo_pago'],
            vendedor=row['vendedor'],
            notas_venta=row['notas_venta']
        )
        venta.id_venta = row['id_venta']
        return venta
        
    def obtener_todas_ventas(self) -> List[Venta]:
        """Obtiene todas las ventas registradas en el sistema"""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                
                # Unir con tabla clientes para obtener información del cliente
                cursor.execute("""
                    SELECT v.*, c.nombre_completo, c.correo, c.categoria
                    FROM ventas v
                    LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                    ORDER BY v.fecha_venta DESC, v.hora_venta DESC
                """)
                
                rows = cursor.fetchall()
                ventas = []
                
                for row in rows:
                    venta = Venta(
                        id_cliente=row['id_cliente'],
                        fecha_venta=str(row['fecha_venta']),
                        hora_venta=str(row['hora_venta']),
                        productos=row['productos'],
                        valor_total=float(row['valor_total']),
                        descuento_aplicado=float(row['descuento_aplicado']),
                        metodo_pago=row['metodo_pago'],
                        vendedor=row['vendedor'],
                        notas_venta=row['notas_venta']
                    )
                    venta.id_venta = row['id_venta']
                    
                    # Añadir información del cliente
                    venta.cliente = {
                        'nombre_completo': row['nombre_completo'] if row['nombre_completo'] else 'Cliente eliminado',
                        'correo': row['correo'] if row['correo'] else '',
                        'categoria': row['categoria'] if row['categoria'] else ''
                    }
                    
                    ventas.append(venta)
                    
                return ventas
            
    def obtener_estadisticas_ventas(self) -> dict:
        """Obtiene estadísticas específicas para la página de ventas"""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Total de ventas
                cursor.execute("SELECT COUNT(*) FROM ventas")
                total_ventas = cursor.fetchone()[0]
                
                # Ventas e ingresos del mes actual
                mes_actual = datetime.now().strftime("%Y-%m")
                cursor.execute("""
                    SELECT COUNT(*), COALESCE(SUM(valor_total), 0)
                    FROM ventas
                    WHERE TO_CHAR(fecha_venta, 'YYYY-MM') = %s
                """, (mes_actual,))
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
            
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                
                # Unir con tabla clientes para obtener información del cliente
                cursor.execute("""
                    SELECT v.*, c.nombre_completo, c.correo, c.categoria
                    FROM ventas v
                    LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                    WHERE v.fecha_venta = %s
                    ORDER BY v.hora_venta DESC
                """, (fecha,))
                
                rows = cursor.fetchall()
                ventas = []
                
                for row in rows:
                    venta = Venta(
                        id_cliente=row['id_cliente'],
                        fecha_venta=str(row['fecha_venta']),
                        hora_venta=str(row['hora_venta']),
                        productos=row['productos'],
                        valor_total=float(row['valor_total']),
                        descuento_aplicado=float(row['descuento_aplicado']),
                        metodo_pago=row['metodo_pago'],
                        vendedor=row['vendedor'],
                        notas_venta=row['notas_venta']
                    )
                    venta.id_venta = row['id_venta']
                    
                    # Añadir información del cliente
                    venta.cliente = {
                        'nombre_completo': row['nombre_completo'] if row['nombre_completo'] else 'Cliente eliminado',
                        'correo': row['correo'] if row['correo'] else '',
                        'categoria': row['categoria'] if row['categoria'] else ''
                    }
                    
                    ventas.append(venta)
                    
                return ventas