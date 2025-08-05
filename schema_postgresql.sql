-- GestorCloud - Esquema Optimizado para PostgreSQL

-- Creación de tablas con tipos de datos optimizados para PostgreSQL

-- Tabla de clientes
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
    ultima_compra DATE DEFAULT NULL,
    descuento_cliente DECIMAL(4,2) DEFAULT 0.0
);

-- Tabla de ventas
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
);

-- Índices para optimización de consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_cliente_nombre ON clientes(nombre_completo);
CREATE INDEX IF NOT EXISTS idx_cliente_correo ON clientes(correo);
CREATE INDEX IF NOT EXISTS idx_cliente_categoria ON clientes(categoria);
CREATE INDEX IF NOT EXISTS idx_cliente_estado ON clientes(estado);
CREATE INDEX IF NOT EXISTS idx_venta_fecha ON ventas(fecha_venta);
CREATE INDEX IF NOT EXISTS idx_venta_cliente ON ventas(id_cliente);

-- Vista para consultas frecuentes de ventas con información de cliente
CREATE OR REPLACE VIEW vista_ventas_completa AS
SELECT 
    v.id_venta,
    v.id_cliente,
    v.fecha_venta,
    v.hora_venta,
    v.productos,
    v.valor_total,
    v.descuento_aplicado,
    v.metodo_pago,
    v.vendedor,
    v.notas_venta,
    c.nombre_completo,
    c.correo,
    c.categoria
FROM 
    ventas v
LEFT JOIN 
    clientes c ON v.id_cliente = c.id_cliente;

-- Vista para estadísticas y dashboard
CREATE OR REPLACE VIEW vista_estadisticas AS
SELECT 
    COUNT(DISTINCT c.id_cliente) AS total_clientes,
    COUNT(DISTINCT CASE WHEN c.categoria = 'VIP' THEN c.id_cliente END) AS clientes_vip,
    COUNT(v.id_venta) AS total_ventas,
    COALESCE(SUM(v.valor_total), 0) AS total_ingresos,
    COALESCE(AVG(v.valor_total), 0) AS promedio_venta
FROM 
    clientes c
LEFT JOIN 
    ventas v ON c.id_cliente = v.id_cliente
WHERE 
    c.estado = 'Activo';

-- Vista para ventas del mes actual
CREATE OR REPLACE VIEW vista_ventas_mes_actual AS
SELECT 
    COUNT(*) AS ventas_mes,
    COALESCE(SUM(valor_total), 0) AS ingresos_mes 
FROM 
    ventas 
WHERE 
    fecha_venta >= date_trunc('month', CURRENT_DATE)
    AND fecha_venta < date_trunc('month', CURRENT_DATE) + INTERVAL '1 month';

-- Vista para top clientes
CREATE OR REPLACE VIEW vista_top_clientes AS
SELECT 
    c.id_cliente,
    c.nombre_completo,
    c.valor_total_compras
FROM 
    clientes c
WHERE 
    c.estado = 'Activo'
ORDER BY 
    c.valor_total_compras DESC
LIMIT 5;

-- Función para actualizar cliente después de una venta
CREATE OR REPLACE FUNCTION actualizar_cliente_tras_venta()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar valor total de compras
    UPDATE clientes
    SET 
        valor_total_compras = valor_total_compras + NEW.valor_total,
        numero_compras = numero_compras + 1,
        ultima_compra = NEW.fecha_venta,
        ultima_actualizacion = CURRENT_TIMESTAMP,
        -- Auto-promoción a VIP si supera cierto valor
        categoria = CASE 
                      WHEN valor_total_compras + NEW.valor_total >= 1000000 THEN 'VIP'
                      ELSE categoria
                    END,
        -- Aplicar descuento si es VIP
        descuento_cliente = CASE 
                              WHEN valor_total_compras + NEW.valor_total >= 1000000 THEN 0.05
                              ELSE descuento_cliente
                            END
    WHERE 
        id_cliente = NEW.id_cliente;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar cliente después de insertar una venta
CREATE TRIGGER tr_actualizar_cliente_tras_venta
AFTER INSERT ON ventas
FOR EACH ROW
EXECUTE FUNCTION actualizar_cliente_tras_venta();

-- Comentarios sobre las tablas para documentación
COMMENT ON TABLE clientes IS 'Almacena información de los clientes del negocio';
COMMENT ON TABLE ventas IS 'Registro de ventas realizadas a los clientes';
COMMENT ON COLUMN clientes.categoria IS 'Categoría del cliente: VIP, Regular, Prospecto o Inactivo';
COMMENT ON COLUMN ventas.productos IS 'Descripción de los productos vendidos, separados por coma';