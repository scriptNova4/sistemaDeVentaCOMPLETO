from app import create_app, db
from app.models import User, Category, Product, Customer, Supplier
from datetime import datetime
import random

def seed_database():
    """Cargar datos iniciales en la base de datos"""
    app = create_app('development')

    with app.app_context():
        # Crear tablas si no existen
        db.create_all()

        # Verificar si ya hay datos
        if User.query.count() > 0:
            print("La base de datos ya contiene datos. No se cargarán datos iniciales.")
            return

        print("Cargando datos iniciales...")

        # =========== Usuarios ===========
        print("Creando usuarios...")

        # Administrador
        admin = User(
            username="admin",
            email="admin@example.com",
            password="admin123",
            fullname="Administrador",
            role="admin",
            position="Administrador de Sistema",
            department="TI"
        )

        # Gerente
        manager = User(
            username="gerente",
            email="gerente@example.com",
            password="gerente123",
            fullname="Gerente",
            role="manager",
            position="Gerente de Tienda",
            department="Administración"
        )

        # Cajero
        cashier = User(
            username="cajero",
            email="cajero@example.com",
            password="cajero123",
            fullname="Cajero",
            role="employee",
            position="Cajero",
            department="Ventas"
        )

        db.session.add_all([admin, manager, cashier])
        db.session.commit()

        # =========== Categorías ===========
        print("Creando categorías...")
        categories = [
            Category(name="Electrónica", description="Productos electrónicos y tecnología"),
            Category(name="Hogar", description="Productos para el hogar"),
            Category(name="Ropa", description="Prendas de vestir y accesorios"),
            Category(name="Alimentos", description="Productos alimenticios"),
            Category(name="Bebidas", description="Bebidas y refrescos"),
            Category(name="Limpieza", description="Productos de limpieza"),
            Category(name="Papelería", description="Artículos de oficina y escolares"),
            Category(name="Juguetes", description="Juguetes y entretenimiento")
        ]

        db.session.add_all(categories)
        db.session.commit()

        # =========== Proveedores ===========
        print("Creando proveedores...")
        suppliers = [
            Supplier(
                name="ElectroTech",
                contact_name="Juan Pérez",
                email="info@electrotech.com",
                phone="555-123-4567",
                address="Av. Tecnología 123, Ciudad de México",
                tax_id="TECH123456",
                payment_terms="30 días",
                notes="Proveedor principal de electrónica"
            ),
            Supplier(
                name="Distribuidora Hogar Feliz",
                contact_name="Ana López",
                email="ventas@hogarfeliz.com",
                phone="555-234-5678",
                address="Calle Hogar 456, Guadalajara",
                tax_id="HOGAR789012",
                payment_terms="15 días",
                notes="Artículos para el hogar"
            ),
            Supplier(
                name="Moda Actual",
                contact_name="Carlos Ramírez",
                email="pedidos@modaactual.com",
                phone="555-345-6789",
                address="Plaza Moda 789, Monterrey",
                tax_id="MODA345678",
                payment_terms="45 días",
                notes="Ropa y accesorios"
            ),
            Supplier(
                name="Alimentos del Valle",
                contact_name="María González",
                email="contacto@alimentosdelvalle.com",
                phone="555-456-7890",
                address="Valle Verde 234, Puebla",
                tax_id="ALIM567890",
                payment_terms="7 días",
                notes="Productos alimenticios frescos"
            )
        ]

        db.session.add_all(suppliers)
        db.session.commit()

        # =========== Productos ===========
        print("Creando productos...")

        # Productos de Electrónica
        electronica = [
            Product(
                name="Smartphone ABC",
                description="Teléfono inteligente con pantalla de 6.5 pulgadas",
                barcode="1234567890123",
                price=8499.99,
                cost=6500.00,
                tax_rate=0.16,
                stock=25,
                min_stock=5,
                max_stock=50,
                category_id=1,
                supplier_id=1
            ),
            Product(
                name="Laptop XYZ",
                description="Computadora portátil con procesador i5",
                barcode="2345678901234",
                price=15999.99,
                cost=12000.00,
                tax_rate=0.16,
                stock=10,
                min_stock=3,
                max_stock=20,
                category_id=1,
                supplier_id=1
            ),
            Product(
                name="Tablet Pro",
                description="Tablet de 10 pulgadas con 64GB de almacenamiento",
                barcode="3456789012345",
                price=6799.99,
                cost=5000.00,
                tax_rate=0.16,
                stock=15,
                min_stock=4,
                max_stock=30,
                category_id=1,
                supplier_id=1
            )
        ]

        # Productos de Hogar
        hogar = [
            Product(
                name="Juego de Sábanas",
                description="Juego de sábanas 100% algodón para cama matrimonial",
                barcode="4567890123456",
                price=899.99,
                cost=600.00,
                tax_rate=0.16,
                stock=30,
                min_stock=10,
                max_stock=50,
                category_id=2,
                supplier_id=2
            ),
            Product(
                name="Juego de Toallas",
                description="Set de 4 toallas de baño de diferentes tamaños",
                barcode="5678901234567",
                price=499.99,
                cost=300.00,
                tax_rate=0.16,
                stock=40,
                min_stock=15,
                max_stock=60,
                category_id=2,
                supplier_id=2
            ),
            Product(
                name="Lámpara de Mesa",
                description="Lámpara decorativa para mesa de noche",
                barcode="6789012345678",
                price=699.99,
                cost=450.00,
                tax_rate=0.16,
                stock=20,
                min_stock=8,
                max_stock=40,
                category_id=2,
                supplier_id=2
            )
        ]

        # Productos de Ropa
        ropa = [
            Product(
                name="Camisa Formal",
                description="Camisa de manga larga para caballero",
                barcode="7890123456789",
                price=599.99,
                cost=350.00,
                tax_rate=0.16,
                stock=50,
                min_stock=20,
                max_stock=100,
                category_id=3,
                supplier_id=3
            ),
            Product(
                name="Blusa Casual",
                description="Blusa de manga corta para dama",
                barcode="8901234567890",
                price=449.99,
                cost=250.00,
                tax_rate=0.16,
                stock=60,
                min_stock=25,
                max_stock=120,
                category_id=3,
                supplier_id=3
            ),
            Product(
                name="Pantalón de Mezclilla",
                description="Pantalón de mezclilla para caballero",
                barcode="9012345678901",
                price=749.99,
                cost=450.00,
                tax_rate=0.16,
                stock=45,
                min_stock=15,
                max_stock=90,
                category_id=3,
                supplier_id=3
            )
        ]

        # Productos de Alimentos
        alimentos = [
            Product(
                name="Arroz Premium",
                description="Arroz grano largo, bolsa de 1kg",
                barcode="0123456789012",
                price=39.99,
                cost=25.00,
                tax_rate=0.16,
                stock=100,
                min_stock=30,
                max_stock=200,
                category_id=4,
                supplier_id=4
            ),
            Product(
                name="Frijol Negro",
                description="Frijol negro, bolsa de 1kg",
                barcode="1234567890120",
                price=49.99,
                cost=30.00,
                tax_rate=0.16,
                stock=80,
                min_stock=25,
                max_stock=150,
                category_id=4,
                supplier_id=4
            ),
            Product(
                name="Aceite Vegetal",
                description="Aceite vegetal, botella de 1L",
                barcode="2345678901230",
                price=45.99,
                cost=28.00,
                tax_rate=0.16,
                stock=70,
                min_stock=20,
                max_stock=140,
                category_id=4,
                supplier_id=4
            )
        ]

        all_products = electronica + hogar + ropa + alimentos
        db.session.add_all(all_products)
        db.session.commit()

        # =========== Clientes ===========
        print("Creando clientes...")
        customers = [
            Customer(
                name="Juan García",
                email="juan.garcia@example.com",
                phone="555-111-2222",
                address="Calle Principal 123, Ciudad de México",
                tax_id="GARJ860125ABC",
                credit_limit=10000.00
            ),
            Customer(
                name="María Rodríguez",
                email="maria.rodriguez@example.com",
                phone="555-222-3333",
                address="Av. Secundaria 456, Guadalajara",
                tax_id="RODM750630XYZ",
                credit_limit=5000.00
            ),
            Customer(
                name="Roberto Hernández",
                email="roberto.hernandez@example.com",
                phone="555-333-4444",
                address="Plaza Central 789, Monterrey",
                tax_id="HERR820915DEF",
                credit_limit=8000.00
            ),
            Customer(
                name="Laura Martínez",
                email="laura.martinez@example.com",
                phone="555-444-5555",
                address="Calle Nueva 101, Puebla",
                tax_id="MARL791120GHI",
                credit_limit=3000.00
            ),
            Customer(
                name="Empresa ABC",
                email="contacto@empresaabc.com",
                phone="555-666-7777",
                address="Torre Empresarial, Piso 10, Ciudad de México",
                tax_id="ABC123456JKL",
                credit_limit=50000.00
            )
        ]

        db.session.add_all(customers)
        db.session.commit()

        print("¡Datos iniciales cargados con éxito!")

if __name__ == "__main__":
    seed_database()
