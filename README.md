# 🌟 GestorCloud

> **Software de gestión de relaciones con clientes (CRM) para organizar y automatizar las interacciones con los clientes**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/cesarcorrales17/GestorCloud)

## 📋 Descripción

**GestorCloud** es un sistema completo de gestión de clientes diseñado específicamente para pequeñas empresas. Permite registrar, organizar y hacer seguimiento de clientes, ventas y estadísticas de negocio de manera sencilla y eficiente.

### ✨ Características Principales

- 👥 **Gestión Completa de Clientes**: Registro, búsqueda, edición y categorización
- 💰 **Control de Ventas**: Registro de transacciones con historial detallado
- 📊 **Reportes y Estadísticas**: Dashboard con métricas importantes del negocio
- ⚙️ **Configuración del Sistema**: Personalización de negocio y preferencias
- 🌟 **Sistema VIP**: Descuentos automáticos para clientes premium
- 💾 **Persistencia de Datos**: Base de datos SQLite local
- 🔒 **Validaciones Robustas**: Email, teléfono y datos empresariales
- 📈 **Escalable**: Arquitectura preparada para crecimiento

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8 o superior
- Git

### Pasos de instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/cesarcorrales17/GestorCloud.git
cd GestorCloud

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# 3. Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar GestorCloud
python main.py
```

## 🎯 Uso

### 🖥️ Interfaz Web (Recomendada)

GestorCloud incluye una moderna interfaz web con dashboard interactivo:

```bash
# Ejecutar la aplicación web
python run_web.py

# O manualmente
cd web
python app.py
```

Luego abre tu navegador en: **http://localhost:8000**

#### Características de la interfaz web:
- 📊 **Dashboard interactivo** con estadísticas en tiempo real
- 👥 **Gestión visual de clientes** con búsqueda y filtros
- 💰 **Registro de ventas** con interfaz intuitiva
- 📊 **Sistema de reportes** con filtros avanzados y exportación
- ⚙️ **Panel de configuración** para personalizar el sistema
- 📱 **Diseño responsive** para móvil y tablet
- 🎨 **Interfaz moderna** con animaciones suaves
- 🔍 **Búsqueda en tiempo real** y filtros avanzados

### 💻 Interfaz de Línea de Comandos

También disponible la versión CLI completa:

```bash
# Desde la raíz del proyecto
python -m src.main

# O directamente
cd src
python main.py
```

### Funcionalidades Disponibles

#### 👥 Gestión de Clientes
- ➕ Registrar nuevos clientes
- 📋 Ver todos los clientes
- 🔍 Buscar por nombre, correo o empresa  
- 📊 Ver detalles completos con historial
- 🏷️ Categorización automática (Regular/VIP)

#### 💰 Gestión de Ventas
- 💳 Registrar nuevas ventas
- 🌟 Descuentos automáticos para clientes VIP
- 📅 Historial de transacciones
- 💳 Múltiples métodos de pago

#### 📊 Reportes
- 📈 Estadísticas generales del negocio
- 🏆 Top clientes por valor
- 📊 Distribución por categorías
- 💰 Ingresos mensuales

## 🏗️ Arquitectura del Proyecto

```
GestorCloud/
├── README.md              # Documentación del proyecto
├── requirements.txt       # Dependencias Python
├── run_web.py            # 🌐 Ejecutar aplicación web
├── src/                  # 💻 Código fuente CLI
│   ├── __init__.py
│   ├── main.py          # Aplicación principal CLI
│   ├── models.py        # Modelos de datos
│   └── database.py      # Gestión de SQLite
├── web/                 # 🌐 Aplicación web
│   ├── app.py          # FastAPI backend
│   ├── templates/      # Templates HTML
│   │   ├── base.html   # Layout base
│   │   ├── dashboard.html
│   │   ├── clientes.html
│   │   ├── cliente_form.html
│   │   ├── cliente_detalle.html
│   │   ├── ventas.html
│   │   ├── ventas_hoy.html
│   │   ├── venta_form.html
│   │   ├── venta_detalle.html
│   │   ├── reportes.html
│   │   └── configuracion.html
│   └── static/         # Archivos estáticos
│       ├── css/        # Estilos personalizados
│       ├── js/         # JavaScript
│       └── img/        # Imágenes
├── data/               # 💾 Base de datos local
│   └── gestorcloud.db  # SQLite database
└── tests/              # 🧪 Pruebas unitarias
    └── test_models.py
```

## 💡 Ejemplos de Uso

### Registrar un Cliente

```python
from models import Cliente
from database import GestorCloudDB

# Crear instancia de base de datos
db = GestorCloudDB()

# Crear nuevo cliente
cliente = Cliente(
    nombre_completo="Juan Pérez",
    edad=35,
    direccion="Calle 123 #45-67",
    correo="juan@empresa.com",
    telefono="3001234567",
    empresa="Empresa ABC",
    categoria="Regular"
)

# Guardar en base de datos
cliente_id = db.agregar_cliente(cliente)
print(f"Cliente registrado con ID: {cliente_id}")
```

### Registrar una Venta

```python
from models import Venta

# Crear nueva venta
venta = Venta(
    id_cliente=1,
    productos="Producto A, Producto B",
    valor_total=150000,
    metodo_pago="Tarjeta Crédito"
)

# Guardar venta (actualiza automáticamente el cliente)
venta_id = db.agregar_venta(venta)
```

## 🔧 Configuración

### Variables de Entorno

Puedes personalizar la configuración creando un archivo `.env`:

```env
DB_PATH=data/mi_empresa.db
BACKUP_PATH=backups/
DEFAULT_DISCOUNT_VIP=0.05
MIN_VIP_AMOUNT=1000000
```

### Configuración de Base de Datos

Por defecto, GestorCloud usa SQLite con la base de datos en `data/gestorcloud.db`. La base de datos se crea automáticamente en la primera ejecución.

## 📊 Dashboard y Reportes

GestorCloud incluye un sistema de reportes que muestra:

- 📈 **Métricas Clave**: Total clientes, ventas del mes, ingresos
- 🌟 **Clientes VIP**: Conteo y beneficios aplicados
- 🏆 **Top Clientes**: Los 5 mejores clientes por valor
- 📊 **Distribución**: Clientes por categoría y estado

## 🔒 Seguridad y Validaciones

- ✅ **Validación de Email**: Formato RFC compliant
- ✅ **Validación de Teléfono**: Números nacionales e internacionales
- ✅ **Prevención de Duplicados**: Control por email único
- ✅ **Integridad de Datos**: Claves foráneas y constraints
- ✅ **Backups Automáticos**: Sistema de respaldo integrado

## 🚧 Roadmap

### Versión 1.1 (Actual)
- [x] 🌐 Interfaz web con FastAPI
- [x] 📱 Diseño responsive
- [x] ⚙️ Panel de configuración del sistema
- [x] 📊 Sistema de reportes y análisis
- [ ] 🌓 Modo claro/oscuro

### Versión 1.2 (Próximamente)
- [ ] 🔐 Sistema de autenticación de usuarios
- [ ] 📧 Envío de emails automáticos
- [ ] 📊 Gráficos interactivos avanzados
- [ ] 💾 Sistema de respaldo y restauración

### Versión 1.3 (Futuro)
- [ ] 📅 Sistema de citas y recordatorios
- [ ] 💳 Integración con pasarelas de pago
- [ ] 📱 API REST completa
- [ ] 🔐 Gestión avanzada de roles y permisos

### Versión 2.0 (Visión)
- [ ] ☁️ Versión SaaS multi-empresa
- [ ] 🤖 Integración con WhatsApp Business
- [ ] 📈 Machine Learning para predicciones
- [ ] 🌍 Soporte multi-idioma

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Guías de Contribución

- Sigue las convenciones de código Python (PEP 8)
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación según sea necesario
- Usa mensajes de commit descriptivos

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**César Corrales**
- GitHub: [@cesarcorrales17](https://github.com/cesarcorrales17)
- Email: cesarcorrales17@ejemplo.com
- LinkedIn: [César Corrales](https://linkedin.com/in/cesarcorrales17)

## 🙏 Agradecimientos

- Inspirado en las necesidades reales de pequeñas empresas
- Desarrollado con Python y amor ❤️
- Comunidad de desarrolladores por el feedback

## 📞 Soporte

Si tienes preguntas, problemas o sugerencias:

1. 🐛 **Reportar bugs**: [Issues en GitHub](https://github.com/cesarcorrales17/GestorCloud/issues)
2. 💬 **Preguntas**: [Discussions](https://github.com/cesarcorrales17/GestorCloud/discussions)
3. 📧 **Email**: cesarcorrales17@ejemplo.com

---

<div align="center">

**¿Te gusta GestorCloud?** ⭐ ¡Dale una estrella al repositorio!

**[⬆ Volver arriba](#-gestorcloud)**

</div>