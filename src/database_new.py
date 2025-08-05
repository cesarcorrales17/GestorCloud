"""
GestorCloud - Gestión de base de datos mejorada
Soporte para SQLite y PostgreSQL
"""

import os
import sqlite3
import psycopg2
from psycopg2 import pool
from typing import List, Optional, Tuple, Dict, Any, Union
from models import Cliente, Venta
from datetime import datetime
import dotenv
from pathlib import Path

# Load environment variables
dotenv.load_dotenv()

class DatabaseConnection:
    """Clase abstracta para manejar conexiones a la base de datos"""
    
    def __init__(self):
        pass
    
    def connect(self):
        """Debe retornar una conexión a la base de datos"""
        raise NotImplementedError
    
    def execute_query(self, query: str, params: tuple = None) -> List[tuple]:
        """Ejecuta una consulta y retorna los resultados"""
        raise NotImplementedError
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Ejecuta una operación de inserción o actualización"""
        raise NotImplementedError
    
    def create_tables(self):
        """Crea las tablas necesarias si no existen"""
        raise NotImplementedError
    
    def get_last_insert_id(self) -> int:
        """Retorna el ID del último registro insertado"""
        raise NotImplementedError
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        pass

class SQLiteConnection(DatabaseConnection):
    """Implementación para SQLite"""
    
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path
        self._crear_directorio_data()
        self.conn = None
        self.cursor = None
        self.last_id = None
    
    def _crear_directorio_data(self):
        """Crea el directorio data si no existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def connect(self):
        """Crea una conexión a SQLite"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Acceso por nombre
            self.cursor = self.conn.cursor()
        return self.conn
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Ejecuta una consulta y retorna los resultados como diccionarios"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        result = [dict(row) for row in cursor.fetchall()]
        return result
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Ejecuta una operación de inserción o actualización"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        self.last_id = cursor.lastrowid
        conn.commit()
        return cursor.rowcount
    
    def get_last_insert_id(self) -> int:
        """Retorna el ID del último registro insertado"""
        return self.last_id
    
    def create_tables(self):
        """Crea las tablas necesarias en SQLite"""
        conn = self.connect()
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
    
    def close(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

class PostgreSQLConnection(DatabaseConnection):
    """Implementación para PostgreSQL usando pool de conexiones"""
    
    def __init__(self, dbname: str, user: str, password: str, host: str, port: str):
        super().__init__()
        self.conn_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.conn = None
        self.cursor = None
        self.last_id = None
    
    def connect(self):
        """Obtiene una conexión del pool"""
        if not self.conn:
            self.conn = self.conn_pool.getconn()
            self.cursor = self.conn.cursor()
        return self.conn
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Ejecuta una consulta y retorna los resultados como diccionarios"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # Obtener nombres de columnas
        if cursor.description:
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return result
        
        return []
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Ejecuta una operación de inserción o actualización"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # Para obtener el último ID insertado en PostgreSQL
        if "RETURNING" in query:
            self.last_id = cursor.fetchone()[0]
        
        conn.commit()
        return cursor.rowcount
    
    def get_last_insert_id(self) -> int:
        """Retorna el ID del último registro insertado"""
        return self.last_id
    
    def create_tables(self):
        """Crea las tablas necesarias en PostgreSQL"""
        conn = self.connect()
        cursor = conn.cursor()
        
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
                id_venta SERIAL PRIMARY KEY,
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
    
    def close(self):
        """Retorna la conexión al pool"""
        if self.conn:
            self.conn_pool.putconn(self.conn)
            self.conn = None
            self.cursor = None
            
    def __del__(self):
        """Cierra el pool de conexiones"""
        if hasattr(self, 'conn_pool') and self.conn_pool:
            self.conn_pool.closeall()

class GestorCloudDB:
    """Clase para manejar todas las operaciones de base de datos"""
    
    def __init__(self, db_path: str = None):
        self.db_type = os.getenv("DB_TYPE", "sqlite").lower()
        
        if self.db_type == "postgres":
            # Conexión a PostgreSQL
            self.db = PostgreSQLConnection(
                dbname=os.getenv("PG_DATABASE", "gestorcloud"),
                user=os.getenv("PG_USER", "postgres"),
                password=os.getenv("PG_PASSWORD", "postgres"),
                host=os.getenv("PG_HOST", "localhost"),
                port=os.getenv("PG_PORT", "5432")
            )
        else:
            # Conexión a SQLite
            if db_path is None:
                db_path = os.getenv("SQLITE_PATH", "data/gestorcloud.db")
            self.db = SQLiteConnection(db_path)
        
        # Crear tablas
        self.db.create_tables()
    
    # === OPERACIONES CON CLIENTES ===
    
    def agregar_cliente(self, cliente: Cliente) -> int:
        """Agrega un nuevo cliente y retorna su ID"""
        try:
            if self.db_type == "postgres":
                query = """
                    INSERT INTO clientes (
                        nombre_completo, edad, direccion, correo, telefono,
                        empresa, categoria, estado, fecha_registro, ultima_actualizacion,
                        notas, valor_total_compras, numero_compras, ultima_compra, descuento_cliente
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_cliente
                """
            else:
                query = """
                    INSERT INTO clientes (
                        nombre_completo, edad, direccion, correo, telefono,
                        empresa, categoria, estado, fecha_registro, ultima_actualizacion,
                        notas, valor_total_compras, numero_compras, ultima_compra, descuento_cliente
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            
            self.db.execute_update(query, (
                cliente.nombre_completo, cliente.edad, cliente.direccion,
                cliente.correo, cliente.telefono, cliente.empresa,
                cliente.categoria, cliente.estado, cliente.fecha_registro,
                cliente.ultima_actualizacion, cliente.notas,
                cliente.valor_total_compras, cliente.numero_compras,
                cliente.ultima_compra, cliente.descuento_cliente
            ))
            
            return self.db.get_last_insert_id()
                
        except (sqlite3.IntegrityError, psycopg2.errors.UniqueViolation):
            raise ValueError(f"Ya existe un cliente con el correo: {cliente.correo}")
    
    def obtener_cliente(self, id_cliente: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        if self.db_type == "postgres":
            query = "SELECT * FROM clientes WHERE id_cliente = %s"
        else:
            query = "SELECT * FROM clientes WHERE id_cliente = ?"
            
        rows = self.db.execute_query(query, (id_cliente,))
        
        if rows:
            return self._dict_to_cliente(rows[0])
        return None
    
    def obtener_todos_clientes(self) -> List[Cliente]:
        """Obtiene todos los clientes"""
        query = "SELECT * FROM clientes ORDER BY nombre_completo"
        rows = self.db.execute_query(query)
        
        return [self._dict_to_cliente(row) for row in rows]
    
    def buscar_clientes(self, termino: str) -> List[Cliente]:
        """Busca clientes por nombre, correo o empresa"""
        termino_like = f"%{termino}%"
        
        if self.db_type == "postgres":
            query = """
                SELECT * FROM clientes 
                WHERE nombre_completo ILIKE %s 
                   OR correo ILIKE %s 
                   OR empresa ILIKE %s
                ORDER BY nombre_completo
            """
        else:
            query = """
                SELECT * FROM clientes 
                WHERE nombre_completo LIKE ? 
                   OR correo LIKE ? 
                   OR empresa LIKE ?
                ORDER BY nombre_completo
            """
            
        rows = self.db.execute_query(query, (termino_like, termino_like, termino_like))
        return [self._dict_to_cliente(row) for row in rows]
    
    def actualizar_cliente(self, cliente: Cliente) -> bool:
        """Actualiza un cliente existente"""
        cliente.actualizar_timestamp()
        
        if self.db_type == "postgres":
            query = """
                UPDATE clientes SET
                    nombre_completo = %s, edad = %s, direccion = %s, correo = %s,
                    telefono = %s, empresa = %s, categoria = %s, estado = %s,
                    ultima_actualizacion = %s, notas = %s, valor_total_compras = %s,
                    numero_compras = %s, ultima_compra = %s, descuento_cliente = %s
                WHERE id_cliente = %s
            """
        else:
            query = """
                UPDATE clientes SET
                    nombre_completo = ?, edad = ?, direccion = ?, correo = ?,
                    telefono = ?, empresa = ?, categoria = ?, estado = ?,
                    ultima_actualizacion = ?, notas = ?, valor_total_compras = ?,
                    numero_compras = ?, ultima_compra = ?, descuento_cliente = ?
                WHERE id_cliente = ?
            """
            
        rows_affected = self.db.execute_update(query, (
            cliente.nombre_completo, cliente.edad, cliente.direccion,
            cliente.correo, cliente.telefono, cliente.empresa,
            cliente.categoria, cliente.estado, cliente.ultima_actualizacion,
            cliente.notas, cliente.valor_total_compras, cliente.numero_compras,
            cliente.ultima_compra, cliente.descuento_cliente, cliente.id_cliente
        ))
        
        return rows_affected > 0
    
    def eliminar_cliente(self, id_cliente: int) -> bool:
        """Elimina un cliente (solo si no tiene ventas)"""
        # Verificar si tiene ventas
        if self.db_type == "postgres":
            query = "SELECT COUNT(*) AS count FROM ventas WHERE id_cliente = %s"
        else:
            query = "SELECT COUNT(*) AS count FROM ventas WHERE id_cliente = ?"
            
        result = self.db.execute_query(query, (id_cliente,))
        
        if result[0]['count'] > 0:
            raise ValueError("No se puede eliminar un cliente con ventas registradas")
        
        # Eliminar cliente
        if self.db_type == "postgres":
            query = "DELETE FROM clientes WHERE id_cliente = %s"
        else:
            query = "DELETE FROM clientes WHERE id_cliente = ?"
            
        rows_affected = self.db.execute_update(query, (id_cliente,))
        return rows_affected > 0
    
    # === OPERACIONES CON VENTAS ===
    
    def agregar_venta(self, venta: Venta) -> int:
        """Agrega una nueva venta y actualiza el cliente"""
        # Insertar venta
        if self.db_type == "postgres":
            query = """
                INSERT INTO ventas (
                    id_cliente, fecha_venta, hora_venta, productos,
                    valor_total, descuento_aplicado, metodo_pago, vendedor, notas_venta
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_venta
            """
        else:
            query = """
                INSERT INTO ventas (
                    id_cliente, fecha_venta, hora_venta, productos,
                    valor_total, descuento_aplicado, metodo_pago, vendedor, notas_venta
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
        self.db.execute_update(query, (
            venta.id_cliente, venta.fecha_venta, venta.hora_venta,
            venta.productos, venta.valor_total, venta.descuento_aplicado,
            venta.metodo_pago, venta.vendedor, venta.notas_venta
        ))
        
        venta_id = self.db.get_last_insert_id()
        
        # Actualizar cliente
        cliente = self.obtener_cliente(venta.id_cliente)
        if cliente:
            cliente.agregar_compra(venta.valor_total)
            self.actualizar_cliente(cliente)
        
        return venta_id
    
    def obtener_ventas_cliente(self, id_cliente: int) -> List[Venta]:
        """Obtiene todas las ventas de un cliente"""
        if self.db_type == "postgres":
            query = """
                SELECT * FROM ventas 
                WHERE id_cliente = %s 
                ORDER BY fecha_venta DESC, hora_venta DESC
            """
        else:
            query = """
                SELECT * FROM ventas 
                WHERE id_cliente = ? 
                ORDER BY fecha_venta DESC, hora_venta DESC
            """
            
        rows = self.db.execute_query(query, (id_cliente,))
        return [self._dict_to_venta(row) for row in rows]
    
    # === ESTADÍSTICAS Y REPORTES ===
    
    def obtener_estadisticas_generales(self) -> dict:
        """Obtiene estadísticas generales del negocio"""
        # Total clientes
        query = "SELECT COUNT(*) AS total FROM clientes WHERE estado = 'Activo'"
        result = self.db.execute_query(query)
        total_clientes = result[0]['total'] if result else 0
        
        # Total ventas del mes actual
        mes_actual = datetime.now().strftime("%Y-%m")
        
        if self.db_type == "postgres":
            query = """
                SELECT COUNT(*) AS ventas_mes, COALESCE(SUM(valor_total), 0) AS ingresos_mes 
                FROM ventas 
                WHERE fecha_venta LIKE %s
            """
        else:
            query = """
                SELECT COUNT(*) AS ventas_mes, COALESCE(SUM(valor_total), 0) AS ingresos_mes 
                FROM ventas 
                WHERE fecha_venta LIKE ?
            """
            
        result = self.db.execute_query(query, (f"{mes_actual}%",))
        ventas_mes = result[0]['ventas_mes'] if result else 0
        ingresos_mes = float(result[0]['ingresos_mes']) if result else 0.0
        
        # Clientes VIP
        query = "SELECT COUNT(*) AS total FROM clientes WHERE categoria = 'VIP'"
        result = self.db.execute_query(query)
        clientes_vip = result[0]['total'] if result else 0
        
        # Top 5 clientes por valor
        query = """
            SELECT nombre_completo, valor_total_compras 
            FROM clientes 
            WHERE estado = 'Activo'
            ORDER BY valor_total_compras DESC 
            LIMIT 5
        """
        top_clientes = self.db.execute_query(query)
        
        return {
            'total_clientes': total_clientes,
            'ventas_mes': ventas_mes,
            'ingresos_mes': ingresos_mes,
            'clientes_vip': clientes_vip,
            'top_clientes': [(c['nombre_completo'], c['valor_total_compras']) for c in top_clientes]
        }
    
    def obtener_clientes_por_categoria(self) -> dict:
        """Obtiene conteo de clientes por categoría"""
        query = """
            SELECT categoria, COUNT(*) AS total
            FROM clientes 
            WHERE estado = 'Activo'
            GROUP BY categoria
        """
        
        result = self.db.execute_query(query)
        return {row['categoria']: row['total'] for row in result}
    
    # === MÉTODOS AUXILIARES ===
    
    def _dict_to_cliente(self, row: dict) -> Cliente:
        """Convierte un diccionario a objeto Cliente"""
        cliente = Cliente(
            nombre_completo=row['nombre_completo'],
            edad=row['edad'],
            direccion=row['direccion'],
            correo=row['correo'],
            telefono=row['telefono'],
            empresa=row['empresa'],
            categoria=row['categoria'],
            estado=row['estado'],
            fecha_registro=row['fecha_registro'],
            ultima_actualizacion=row['ultima_actualizacion'],
            notas=row['notas'],
            valor_total_compras=row['valor_total_compras'],
            numero_compras=row['numero_compras'],
            ultima_compra=row['ultima_compra'],
            descuento_cliente=row['descuento_cliente']
        )
        cliente.id_cliente = row['id_cliente']
        return cliente
    
    def _dict_to_venta(self, row: dict) -> Venta:
        """Convierte un diccionario a objeto Venta"""
        venta = Venta(
            id_cliente=row['id_cliente'],
            fecha_venta=row['fecha_venta'],
            hora_venta=row['hora_venta'],
            productos=row['productos'],
            valor_total=row['valor_total'],
            descuento_aplicado=row['descuento_aplicado'],
            metodo_pago=row['metodo_pago'],
            vendedor=row['vendedor'],
            notas_venta=row['notas_venta']
        )
        venta.id_venta = row['id_venta']
        return venta
        
    def obtener_todas_ventas(self) -> List[Venta]:
        """Obtiene todas las ventas registradas en el sistema"""
        # Unir con tabla clientes para obtener información del cliente
        if self.db_type == "postgres":
            query = """
                SELECT v.*, c.nombre_completo, c.correo, c.categoria
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.fecha_venta DESC, v.hora_venta DESC
            """
        else:
            query = """
                SELECT v.*, c.nombre_completo, c.correo, c.categoria
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                ORDER BY v.fecha_venta DESC, v.hora_venta DESC
            """
            
        rows = self.db.execute_query(query)
        ventas = []
        
        for row in rows:
            venta = Venta(
                id_cliente=row['id_cliente'],
                fecha_venta=row['fecha_venta'],
                hora_venta=row['hora_venta'],
                productos=row['productos'],
                valor_total=row['valor_total'],
                descuento_aplicado=row['descuento_aplicado'],
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
        # Total de ventas
        query = "SELECT COUNT(*) AS total FROM ventas"
        result = self.db.execute_query(query)
        total_ventas = result[0]['total'] if result else 0
        
        # Ventas e ingresos del mes actual
        mes_actual = datetime.now().strftime("%Y-%m")
        
        if self.db_type == "postgres":
            query = """
                SELECT COUNT(*) AS ventas_mes, COALESCE(SUM(valor_total), 0) AS ingresos_mes 
                FROM ventas 
                WHERE fecha_venta LIKE %s
            """
        else:
            query = """
                SELECT COUNT(*) AS ventas_mes, COALESCE(SUM(valor_total), 0) AS ingresos_mes 
                FROM ventas 
                WHERE fecha_venta LIKE ?
            """
            
        result = self.db.execute_query(query, (f"{mes_actual}%",))
        ventas_mes = result[0]['ventas_mes'] if result else 0
        ingresos_mes = float(result[0]['ingresos_mes']) if result else 0.0
        
        # Promedio por venta
        query = "SELECT COALESCE(AVG(valor_total), 0) AS promedio FROM ventas"
        result = self.db.execute_query(query)
        promedio_venta = float(result[0]['promedio']) if result else 0.0
        
        return {
            'total_ventas': total_ventas,
            'ventas_mes': ventas_mes,
            'ingresos_mes': ingresos_mes,
            'promedio_venta': promedio_venta
        }
            
    def obtener_ventas_del_dia(self, fecha: str = None) -> List[Venta]:
        """Obtiene todas las ventas de un día específico o del día actual"""
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d")
            
        # Unir con tabla clientes para obtener información del cliente
        if self.db_type == "postgres":
            query = """
                SELECT v.*, c.nombre_completo, c.correo, c.categoria
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                WHERE v.fecha_venta = %s
                ORDER BY v.hora_venta DESC
            """
        else:
            query = """
                SELECT v.*, c.nombre_completo, c.correo, c.categoria
                FROM ventas v
                LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
                WHERE v.fecha_venta = ?
                ORDER BY v.hora_venta DESC
            """
            
        rows = self.db.execute_query(query, (fecha,))
        ventas = []
        
        for row in rows:
            venta = Venta(
                id_cliente=row['id_cliente'],
                fecha_venta=row['fecha_venta'],
                hora_venta=row['hora_venta'],
                productos=row['productos'],
                valor_total=row['valor_total'],
                descuento_aplicado=row['descuento_aplicado'],
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
    
    def hacer_backup(self, archivo_backup: str = None) -> str:
        """Crea un backup de la base de datos"""
        if self.db_type != "sqlite":
            raise NotImplementedError("La función de backup solo está disponible para SQLite")
            
        if not archivo_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_backup = f"data/backup_gestorcloud_{timestamp}.db"
        
        import shutil
        shutil.copy2(os.getenv("SQLITE_PATH", "data/gestorcloud.db"), archivo_backup)
        return archivo_backup
    
    def migrar_desde_sqlite(self, sqlite_path: str):
        """Migra los datos desde una base de datos SQLite a PostgreSQL"""
        if self.db_type != "postgres":
            raise ValueError("Esta función solo está disponible para PostgreSQL")
            
        # Crear una conexión temporal a SQLite
        sqlite_db = SQLiteConnection(sqlite_path)
        
        # Migrar clientes
        rows = sqlite_db.execute_query("SELECT * FROM clientes")
        for row in rows:
            cliente = self._dict_to_cliente(row)
            try:
                self.agregar_cliente(cliente)
            except ValueError:
                # Si ya existe, actualizar
                self.actualizar_cliente(cliente)
        
        # Migrar ventas
        rows = sqlite_db.execute_query("SELECT * FROM ventas")
        for row in rows:
            venta = self._dict_to_venta(row)
            self.agregar_venta(venta)
            
        sqlite_db.close()
        return len(rows)
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'db'):
            self.db.close()