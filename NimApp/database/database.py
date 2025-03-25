import os
import sqlite3


class Database:
    def __init__(self, db_name='stok_takip.db'):
        # Veritabanı dosyasının tam yolunu belirleme
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, db_name)
        self.connection = None
        self.cursor = None

    def connect(self):
        """Veritabanına bağlanır ve tablolar yoksa oluşturur."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Sonuçları sözlük olarak al
        self.cursor = self.connection.cursor()
        self._create_tables()
        return self.connection

    def close(self):
        """Veritabanı bağlantısını kapatır."""
        if self.connection:
            self.connection.close()

    def _create_tables(self):
        """Veritabanında gerekli tabloları oluşturur."""
        # Kategoriler tablosu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
        ''')

        # Tedarikçiler tablosu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT
        )
        ''')

        # Ürünler tablosu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            stock_quantity REAL DEFAULT 0,
            stock_threshold REAL DEFAULT 5,
            barcode TEXT,
            is_raw_material BOOLEAN DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        ''')

        # Ürün Bileşenleri tablosu (Ürün Ağacı)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            component_id INTEGER,
            quantity REAL,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (component_id) REFERENCES products (id)
        )
        ''')

        # Stok Hareketleri tablosu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity REAL,
            movement_type TEXT,
            supplier_id INTEGER,
            production_date TEXT,
            expiry_date TEXT,
            batch_number TEXT,
            description TEXT,
            date TEXT,
            sales_channel_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
            FOREIGN KEY (sales_channel_id) REFERENCES sales_channels (id)
        )
        ''')

        # Satış Kanalları tablosu
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
        ''')

        # Üretim Emirleri tablosu
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity REAL,
                status TEXT DEFAULT 'PENDING',
                date TEXT,
                notes TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            ''')

        # Üretim Detayları tablosu (hammadde kullanımı)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS production_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                production_order_id INTEGER,
                component_id INTEGER,
                quantity_needed REAL,
                quantity_used REAL,
                FOREIGN KEY (production_order_id) REFERENCES production_orders (id),
                FOREIGN KEY (component_id) REFERENCES products (id)
            )
            ''')

        # Ürün Birim Tipleri tablosu
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS unit_types (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               description TEXT
           )
           ''')

        # Müşteriler tablosu
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS customers (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT NOT NULL,
               phone TEXT,
               email TEXT,
               address TEXT,
               notes TEXT
           )
           ''')

        # Alım Kayıtları tablosu
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS purchase_records (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               product_id INTEGER,
               supplier_id INTEGER,
               quantity REAL,
               unit_type_id INTEGER,
               purchase_price REAL,
               purchase_date TEXT,
               notes TEXT,
               FOREIGN KEY (product_id) REFERENCES products (id),
               FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
               FOREIGN KEY (unit_type_id) REFERENCES unit_types (id)
           )
           ''')

        # Satış Kayıtları tablosu
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS sales_records (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               product_id INTEGER,
               customer_id INTEGER,
               sales_channel_id INTEGER,
               quantity REAL,
               unit_type_id INTEGER,
               sale_price REAL,
               sale_date TEXT,
               sale_type TEXT,  -- 'SALE', 'SAMPLE', 'GIFT'
               notes TEXT,
               FOREIGN KEY (product_id) REFERENCES products (id),
               FOREIGN KEY (customer_id) REFERENCES customers (id),
               FOREIGN KEY (sales_channel_id) REFERENCES sales_channels (id),
               FOREIGN KEY (unit_type_id) REFERENCES unit_types (id)
           )
           ''')

        # Zayi Kayıtları tablosu
        self.cursor.execute('''
           CREATE TABLE IF NOT EXISTS waste_records (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               product_id INTEGER,
               quantity REAL,
               unit_type_id INTEGER,
               waste_date TEXT,
               reason TEXT,
               notes TEXT,
               FOREIGN KEY (product_id) REFERENCES products (id),
               FOREIGN KEY (unit_type_id) REFERENCES unit_types (id)
           )
           ''')

        # Varsayılan birim tiplerini ekle
        self.cursor.execute("SELECT COUNT(*) FROM unit_types")
        count = self.cursor.fetchone()[0]

        if count == 0:
            unit_types = [
                ("Adet", "Birim adet olarak sayılır"),
                ("Kg", "Kilogram cinsinden ölçülür"),
                ("Gr", "Gram cinsinden ölçülür"),
                ("Lt", "Litre cinsinden ölçülür"),
                ("ML", "Mililitre cinsinden ölçülür"),
                ("Paket", "Paket olarak sayılır")
            ]

            for unit_type in unit_types:
                self.cursor.execute(
                    "INSERT INTO unit_types (name, description) VALUES (?, ?)",
                    unit_type
                )

        self.connection.commit()

        # Önceden tanımlanmış satış kanallarını ekleyelim
        self.cursor.execute("SELECT COUNT(*) FROM sales_channels")
        count = self.cursor.fetchone()[0]

        if count == 0:
            sales_channels = [
                ("Trendyol", "Trendyol pazaryeri"),
                ("Pazarama", "Pazarama pazaryeri"),
                ("N11", "N11 pazaryeri"),
                ("Hepsiburada", "Hepsiburada pazaryeri"),
                ("Ticimax", "Ticimax pazaryeri"),
                ("Amazon", "Amazon pazaryeri"),
                ("Hipicon", "Hipicon pazaryeri"),
                ("İdefix", "İdefix pazaryeri"),
                ("Milagron", "Milagron pazaryeri"),
                ("Mağaza", "Fiziksel mağaza satışları")
            ]

            for channel in sales_channels:
                self.cursor.execute(
                    "INSERT INTO sales_channels (name, description) VALUES (?, ?)",
                    channel
                )

        self.connection.commit()