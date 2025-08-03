"""
GestorCloud v1.0
Sistema de gestión de clientes para pequeñas empresas
Versión CLI (Línea de comandos)
"""

import os
import sys
from typing import Optional
from models import Cliente, Venta, CATEGORIAS_CLIENTE, ESTADOS_CLIENTE, METODOS_PAGO
from database import GestorCloudDB

class GestorCloud:
    """Clase principal del sistema GestorCloud"""
    
    def __init__(self):
        self.db = GestorCloudDB()
        self.version = "1.0.0"
    
    def mostrar_banner(self):
        """Muestra el banner de bienvenida"""
        print("=" * 60)
        print("🌟 GestorCloud v{} - CRM para Pequeñas Empresas 🌟".format(self.version))
        print("=" * 60)
        print("📊 Gestiona tus clientes desde cualquier lugar")
        print("=" * 60)
    
    def menu_principal(self):
        """Muestra el menú principal"""
        print("\n" + "─" * 50)
        print("📋 MENÚ PRINCIPAL")
        print("─" * 50)
        print("1. 👥 Gestión de Clientes")
        print("2. 💰 Gestión de Ventas")
        print("3. 📊 Reportes y Estadísticas")
        print("4. 🔧 Configuración")
        print("5. ❌ Salir")
        print("─" * 50)
    
    def menu_clientes(self):
        """Muestra el menú de gestión de clientes"""
        print("\n" + "─" * 50)
        print("👥 GESTIÓN DE CLIENTES")
        print("─" * 50)
        print("1. ➕ Registrar nuevo cliente")
        print("2. 📋 Ver todos los clientes")
        print("3. 🔍 Buscar cliente")
        print("4. ✏️  Editar cliente")
        print("5. 🗑️  Eliminar cliente")
        print("6. 📊 Ver detalles de cliente")
        print("7. 🔙 Volver al menú principal")
        print("─" * 50)
    
    def menu_ventas(self):
        """Muestra el menú de gestión de ventas"""
        print("\n" + "─" * 50)
        print("💰 GESTIÓN DE VENTAS")
        print("─" * 50)
        print("1. 💳 Registrar nueva venta")
        print("2. 📋 Ver ventas por cliente")
        print("3. 📊 Ventas del día")
        print("4. 🔙 Volver al menú principal")
        print("─" * 50)
    
    def registrar_cliente(self):
        """Registra un nuevo cliente"""
        print("\n" + "═" * 50)
        print("➕ REGISTRO DE NUEVO CLIENTE")
        print("═" * 50)
        
        try:
            # Datos básicos
            nombre = input("📝 Nombre completo: ").strip()
            if not nombre:
                print("❌ El nombre es obligatorio")
                return
            
            # Edad con validación
            while True:
                try:
                    edad = int(input("🎂 Edad: "))
                    if 0 < edad < 120:
                        break
                    else:
                        print("❌ Edad debe estar entre 1 y 119 años")
                except ValueError:
                    print("❌ Por favor, ingrese un número válido para la edad")
            
            direccion = input("🏠 Dirección: ").strip()
            if not direccion:
                print("❌ La dirección es obligatoria")
                return
            
            # Correo con validación
            while True:
                correo = input("📧 Correo electrónico: ").strip().lower()
                if correo:
                    try:
                        # Crear cliente temporal para validar correo
                        Cliente(nombre, edad, direccion, correo, "1234567")
                        break
                    except ValueError as e:
                        print(f"❌ {e}")
                else:
                    print("❌ El correo es obligatorio")
            
            # Teléfono con validación
            while True:
                telefono = input("📱 Teléfono: ").strip()
                if telefono:
                    try:
                        # Crear cliente temporal para validar teléfono
                        Cliente(nombre, edad, direccion, correo, telefono)
                        break
                    except ValueError as e:
                        print(f"❌ {e}")
                else:
                    print("❌ El teléfono es obligatorio")
            
            # Datos empresariales opcionales
            empresa = input("🏢 Empresa (opcional): ").strip()
            
            print(f"\n📂 Categorías disponibles: {', '.join(CATEGORIAS_CLIENTE)}")
            categoria = input("🏷️  Categoría (presiona Enter para 'Regular'): ").strip()
            if categoria not in CATEGORIAS_CLIENTE:
                categoria = "Regular"
            
            notas = input("📝 Notas adicionales (opcional): ").strip()
            
            # Crear y guardar cliente
            cliente = Cliente(
                nombre_completo=nombre,
                edad=edad,
                direccion=direccion,
                correo=correo,
                telefono=telefono,
                empresa=empresa,
                categoria=categoria,
                notas=notas
            )
            
            cliente_id = self.db.agregar_cliente(cliente)
            cliente.id_cliente = cliente_id
            
            print("\n" + "✅" * 20)
            print(f"✅ Cliente registrado exitosamente con ID: {cliente_id}")
            print(f"📋 Nombre: {nombre}")
            print(f"🏷️  Categoría: {categoria}")
            print("✅" * 20)
            
        except ValueError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def mostrar_todos_clientes(self):
        """Muestra todos los clientes registrados"""
        print("\n" + "═" * 70)
        print("📋 TODOS LOS CLIENTES REGISTRADOS")
        print("═" * 70)
        
        clientes = self.db.obtener_todos_clientes()
        
        if not clientes:
            print("📭 No hay clientes registrados todavía.")
            return
        
        for cliente in clientes:
            self._mostrar_cliente_resumido(cliente)
        
        print(f"\n📊 Total de clientes: {len(clientes)}")
    
    def buscar_cliente(self):
        """Busca clientes por nombre, correo o empresa"""
        print("\n" + "═" * 50)
        print("🔍 BUSCAR CLIENTE")
        print("═" * 50)
        
        termino = input("🔍 Ingrese nombre, correo o empresa: ").strip()
        if not termino:
            print("❌ Debe ingresar un término de búsqueda")
            return
        
        clientes = self.db.buscar_clientes(termino)
        
        if not clientes:
            print(f"📭 No se encontraron clientes que coincidan con '{termino}'")
            return
        
        print(f"\n📋 Resultados de búsqueda para '{termino}':")
        print("─" * 50)
        
        for cliente in clientes:
            self._mostrar_cliente_resumido(cliente)
        
        print(f"\n📊 Se encontraron {len(clientes)} cliente(s)")
    
    def ver_detalles_cliente(self):
        """Muestra los detalles completos de un cliente"""
        print("\n" + "═" * 50)
        print("📊 DETALLES DE CLIENTE")
        print("═" * 50)
        
        try:
            id_cliente = int(input("🆔 Ingrese el ID del cliente: "))
            cliente = self.db.obtener_cliente(id_cliente)
            
            if not cliente:
                print(f"❌ No se encontró cliente con ID: {id_cliente}")
                return
            
            self._mostrar_cliente_detallado(cliente)
            
            # Mostrar historial de ventas
            ventas = self.db.obtener_ventas_cliente(id_cliente)
            if ventas:
                print("\n" + "─" * 50)
                print("💰 HISTORIAL DE VENTAS")
                print("─" * 50)
                for venta in ventas[:5]:  # Últimas 5 ventas
                    print(f"📅 {venta.fecha_venta} - ${venta.valor_total:,.0f} - {venta.metodo_pago}")
                if len(ventas) > 5:
                    print(f"... y {len(ventas) - 5} ventas más")
            
        except ValueError:
            print("❌ Por favor, ingrese un ID válido (número)")
    
    def registrar_venta(self):
        """Registra una nueva venta"""
        print("\n" + "═" * 50)
        print("💳 REGISTRO NUEVA VENTA")
        print("═" * 50)
        
        try:
            # Buscar cliente
            print("🔍 Primero, busquemos al cliente:")
            termino = input("📝 Nombre, correo o ID del cliente: ").strip()
            
            # Intentar buscar por ID primero
            cliente = None
            if termino.isdigit():
                cliente = self.db.obtener_cliente(int(termino))
            
            # Si no es ID o no se encontró, buscar por texto
            if not cliente:
                clientes = self.db.buscar_clientes(termino)
                if not clientes:
                    print(f"❌ No se encontró cliente para '{termino}'")
                    return
                elif len(clientes) == 1:
                    cliente = clientes[0]
                else:
                    print(f"\n📋 Se encontraron {len(clientes)} clientes:")
                    for i, c in enumerate(clientes, 1):
                        print(f"{i}. {c.nombre_completo} - {c.correo}")
                    
                    seleccion = int(input("📝 Seleccione cliente (número): ")) - 1
                    if 0 <= seleccion < len(clientes):
                        cliente = clientes[seleccion]
                    else:
                        print("❌ Selección inválida")
                        return
            
            print(f"\n✅ Cliente seleccionado: {cliente.nombre_completo}")
            if cliente.categoria == "VIP":
                print(f"🌟 Cliente VIP - Descuento disponible: {cliente.descuento_cliente*100:.0f}%")
            
            # Datos de la venta
            productos = input("🛍️  Productos/Servicios: ").strip()
            if not productos:
                print("❌ Debe especificar los productos o servicios")
                return
            
            while True:
                try:
                    valor_total = float(input("💰 Valor total: $").replace(",", ""))
                    if valor_total > 0:
                        break
                    else:
                        print("❌ El valor debe ser mayor a 0")
                except ValueError:
                    print("❌ Por favor, ingrese un valor numérico válido")
            
            # Aplicar descuento VIP automáticamente
            descuento = 0.0
            if cliente.categoria == "VIP" and cliente.descuento_cliente > 0:
                aplicar_desc = input(f"💎 ¿Aplicar descuento VIP {cliente.descuento_cliente*100:.0f}%? (s/n): ").lower()
                if aplicar_desc in ['s', 'si', 'sí', 'y', 'yes']:
                    descuento = valor_total * cliente.descuento_cliente
                    print(f"💰 Descuento aplicado: ${descuento:,.0f}")
                    print(f"💳 Total a pagar: ${valor_total - descuento:,.0f}")
            
            print(f"\n💳 Métodos de pago: {', '.join(METODOS_PAGO)}")
            metodo_pago = input("💳 Método de pago: ").strip()
            if metodo_pago not in METODOS_PAGO:
                metodo_pago = "Efectivo"
            
            vendedor = input("👤 Vendedor (opcional): ").strip()
            notas = input("📝 Notas de venta (opcional): ").strip()
            
            # Crear y guardar venta
            venta = Venta(
                id_cliente=cliente.id_cliente,
                productos=productos,
                valor_total=valor_total,
                descuento_aplicado=descuento,
                metodo_pago=metodo_pago,
                vendedor=vendedor,
                notas_venta=notas
            )
            
            venta_id = self.db.agregar_venta(venta)
            
            print("\n" + "✅" * 25)
            print(f"✅ Venta registrada exitosamente - ID: {venta_id}")
            print(f"👤 Cliente: {cliente.nombre_completo}")
            print(f"💰 Total: ${valor_total:,.0f}")
            if descuento > 0:
                print(f"💎 Descuento: ${descuento:,.0f}")
                print(f"💳 Pagado: ${valor_total - descuento:,.0f}")
            print(f"💳 Método: {metodo_pago}")
            print("✅" * 25)
            
        except ValueError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas generales del negocio"""
        print("\n" + "═" * 60)
        print("📊 ESTADÍSTICAS GENERALES")
        print("═" * 60)
        
        stats = self.db.obtener_estadisticas_generales()
        categorias = self.db.obtener_clientes_por_categoria()
        
        print(f"👥 Total clientes activos: {stats['total_clientes']}")
        print(f"🌟 Clientes VIP: {stats['clientes_vip']}")
        print(f"💰 Ventas este mes: {stats['ventas_mes']}")
        print(f"💵 Ingresos este mes: ${stats['ingresos_mes']:,.0f}")
        
        print("\n📊 Clientes por categoría:")
        for categoria, cantidad in categorias.items():
            print(f"   {categoria}: {cantidad}")
        
        if stats['top_clientes']:
            print("\n🏆 Top 5 clientes por valor:")
            for i, (nombre, valor) in enumerate(stats['top_clientes'], 1):
                print(f"   {i}. {nombre}: ${valor:,.0f}")
    
    def hacer_backup(self):
        """Crea un backup de la base de datos"""
        try:
            archivo = self.db.hacer_backup()
            print(f"✅ Backup creado exitosamente: {archivo}")
        except Exception as e:
            print(f"❌ Error al crear backup: {e}")
    
    def _mostrar_cliente_resumido(self, cliente: Cliente):
        """Muestra información resumida de un cliente"""
        estado_icon = "✅" if cliente.estado == "Activo" else "⏸️"
        categoria_icon = "🌟" if cliente.categoria == "VIP" else "👤"
        
        print(f"\n{estado_icon} ID: {cliente.id_cliente} | {categoria_icon} {cliente.nombre_completo}")
        print(f"📧 {cliente.correo} | 📱 {cliente.telefono}")
        if cliente.empresa:
            print(f"🏢 {cliente.empresa}")
        print(f"💰 Total compras: ${cliente.valor_total_compras:,.0f} | 🛒 {cliente.numero_compras} compras")
        print("─" * 50)
    
    def _mostrar_cliente_detallado(self, cliente: Cliente):
        """Muestra información detallada de un cliente"""
        print(f"\n👤 CLIENTE ID: {cliente.id_cliente}")
        print("═" * 50)
        print(f"📝 Nombre: {cliente.nombre_completo}")
        print(f"🎂 Edad: {cliente.edad} años")
        print(f"🏠 Dirección: {cliente.direccion}")
        print(f"📧 Correo: {cliente.correo}")
        print(f"📱 Teléfono: {cliente.telefono}")
        if cliente.empresa:
            print(f"🏢 Empresa: {cliente.empresa}")
        print(f"🏷️  Categoría: {cliente.categoria}")
        print(f"📊 Estado: {cliente.estado}")
        print(f"📅 Registrado: {cliente.fecha_registro}")
        print(f"🔄 Última actualización: {cliente.ultima_actualizacion}")
        print(f"💰 Total compras: ${cliente.valor_total_compras:,.0f}")
        print(f"🛒 Número de compras: {cliente.numero_compras}")
        if cliente.ultima_compra:
            dias = cliente.dias_desde_ultima_compra()
            print(f"🗓️  Última compra: {cliente.ultima_compra} ({dias} días atrás)")
        if cliente.descuento_cliente > 0:
            print(f"💎 Descuento VIP: {cliente.descuento_cliente*100:.0f}%")
        if cliente.notas:
            print(f"📝 Notas: {cliente.notas}")
    
    def ejecutar(self):
        """Ejecuta el programa principal"""
        self.mostrar_banner()
        
        while True:
            try:
                self.menu_principal()
                opcion = input("🎯 Seleccione una opción: ").strip()
                
                if opcion == "1":
                    self._gestionar_clientes()
                elif opcion == "2":
                    self._gestionar_ventas()
                elif opcion == "3":
                    self.mostrar_estadisticas()
                elif opcion == "4":
                    self._configuracion()
                elif opcion == "5":
                    print("\n👋 ¡Gracias por usar GestorCloud!")
                    print("💾 Todos los datos han sido guardados automáticamente")
                    print("🌟 ¡Hasta pronto!")
                    break
                else:
                    print("❌ Opción no válida. Intente nuevamente.")
                
                input("\n⏸️  Presione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Saliendo de GestorCloud...")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
    
    def _gestionar_clientes(self):
        """Submenú de gestión de clientes"""
        while True:
            self.menu_clientes()
            opcion = input("🎯 Seleccione una opción: ").strip()
            
            if opcion == "1":
                self.registrar_cliente()
            elif opcion == "2":
                self.mostrar_todos_clientes()
            elif opcion == "3":
                self.buscar_cliente()
            elif opcion == "4":
                print("⚠️  Función de edición en desarrollo")
            elif opcion == "5":
                print("⚠️  Función de eliminación en desarrollo")
            elif opcion == "6":
                self.ver_detalles_cliente()
            elif opcion == "7":
                break
            else:
                print("❌ Opción no válida")
            
            if opcion != "7":
                input("\n⏸️  Presione Enter para continuar...")
    
    def _gestionar_ventas(self):
        """Submenú de gestión de ventas"""
        while True:
            self.menu_ventas()
            opcion = input("🎯 Seleccione una opción: ").strip()
            
            if opcion == "1":
                self.registrar_venta()
            elif opcion == "2":
                print("⚠️  Ver ventas por cliente en desarrollo")
            elif opcion == "3":
                print("⚠️  Ventas del día en desarrollo")
            elif opcion == "4":
                break
            else:
                print("❌ Opción no válida")
            
            if opcion != "4":
                input("\n⏸️  Presione Enter para continuar...")
    
    def _configuracion(self):
        """Submenú de configuración"""
        print("\n" + "═" * 50)
        print("🔧 CONFIGURACIÓN")
        print("═" * 50)
        print("1. 💾 Crear backup")
        print("2. ℹ️  Información del sistema")
        print("3. 🔙 Volver")
        
        opcion = input("🎯 Seleccione una opción: ").strip()
        
        if opcion == "1":
            self.hacer_backup()
        elif opcion == "2":
            self._mostrar_info_sistema()
        elif opcion == "3":
            return
        else:
            print("❌ Opción no válida")
    
    def _mostrar_info_sistema(self):
        """Muestra información del sistema"""
        print(f"\n🌟 GestorCloud v{self.version}")
        print("📊 Sistema de gestión de clientes para pequeñas empresas")
        print(f"💾 Base de datos: {self.db.db_path}")
        print("🐍 Desarrollado en Python")
        print("📧 Soporte: tu-email@ejemplo.com")

def main():
    """Función principal"""
    try:
        app = GestorCloud()
        app.ejecutar()
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()