from datetime import datetime


class Product:
    def __init__(self, id=None, category_id=None, name="", description="",
                 stock_quantity=0, stock_threshold=5, barcode="", is_raw_material=False):
        self.id = id
        self.category_id = category_id
        self.name = name
        self.description = description
        self.stock_quantity = stock_quantity
        self.stock_threshold = stock_threshold
        self.barcode = barcode
        self.is_raw_material = is_raw_material
        self.category_name = ""  # Kategorinin adını tutmak için

    @staticmethod
    def get_all(db):
        """Tüm ürünleri veritabanından çeker."""
        db.cursor.execute("""
        SELECT p.id, p.category_id, p.name, p.description, 
               p.stock_quantity, p.stock_threshold, p.barcode, p.is_raw_material,
               c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        """)
        products = []
        for row in db.cursor.fetchall():
            product = Product(row['id'], row['category_id'], row['name'], row['description'],
                              row['stock_quantity'], row['stock_threshold'], row['barcode'],
                              row['is_raw_material'])
            product.category_name = row['category_name'] if row['category_name'] else ""
            products.append(product)
        return products

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre ürün bilgisini getirir."""
        db.cursor.execute("""
        SELECT p.id, p.category_id, p.name, p.description, 
               p.stock_quantity, p.stock_threshold, p.barcode, p.is_raw_material,
               c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = ?
        """, (id,))
        row = db.cursor.fetchone()
        if row:
            product = Product(row['id'], row['category_id'], row['name'], row['description'],
                              row['stock_quantity'], row['stock_threshold'], row['barcode'],
                              row['is_raw_material'])
            product.category_name = row['category_name'] if row['category_name'] else ""
            return product
        return None

    def save(self, db):
        """Ürünü veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                """INSERT INTO products (category_id, name, description, stock_quantity, 
                   stock_threshold, barcode, is_raw_material) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.category_id, self.name, self.description, self.stock_quantity,
                 self.stock_threshold, self.barcode, self.is_raw_material)
            )
            self.id = db.cursor.lastrowid
        else:
            db.cursor.execute(
                """UPDATE products SET category_id = ?, name = ?, description = ?, 
                   stock_quantity = ?, stock_threshold = ?, barcode = ?, is_raw_material = ? 
                   WHERE id = ?""",
                (self.category_id, self.name, self.description, self.stock_quantity,
                 self.stock_threshold, self.barcode, self.is_raw_material, self.id)
            )
        db.connection.commit()
        return self.id

    def delete(self, db):
        """Ürünü veritabanından siler."""
        if self.id:
            db.cursor.execute("DELETE FROM products WHERE id = ?", (self.id,))
            db.connection.commit()
            return True
        return False

    def get_components(self, db):
        """Ürün bileşenlerini getirir."""
        db.cursor.execute("""
        SELECT pc.id, pc.component_id, p.name, pc.quantity
        FROM product_components pc
        JOIN products p ON pc.component_id = p.id
        WHERE pc.product_id = ?
        """, (self.id,))
        return db.cursor.fetchall()

    def add_component(self, db, component_id, quantity):
        """Ürüne bileşen ekler."""
        db.cursor.execute(
            "INSERT INTO product_components (product_id, component_id, quantity) VALUES (?, ?, ?)",
            (self.id, component_id, quantity)
        )
        db.connection.commit()

    def remove_component(self, db, component_id):
        """Üründen bileşen çıkarır."""
        db.cursor.execute(
            "DELETE FROM product_components WHERE product_id = ? AND component_id = ?",
            (self.id, component_id)
        )
        db.connection.commit()

    def update_stock(self, db, quantity, movement_type="IN", supplier_id=None,
                     production_date=None, expiry_date=None, batch_number=None,
                     description=None, sales_channel_id=None):
        """Ürün stoğunu günceller ve stok hareketi kaydeder."""
        # Stok miktarını güncelle
        if movement_type == "IN":
            self.stock_quantity += quantity
        else:  # OUT
            self.stock_quantity -= quantity

        # Ürünü kaydet
        self.save(db)

        # Stok hareketini kaydet
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.cursor.execute(
            """INSERT INTO stock_movements (product_id, quantity, movement_type, supplier_id,
               production_date, expiry_date, batch_number, description, date, sales_channel_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (self.id, quantity, movement_type, supplier_id, production_date,
             expiry_date, batch_number, description, current_date, sales_channel_id)
        )
        db.connection.commit()

    @staticmethod
    def get_products_below_threshold(db):
        """Stok eşiğinin altındaki ürünleri getirir."""
        db.cursor.execute("""
        SELECT p.id, p.name, p.stock_quantity, p.stock_threshold
        FROM products p
        WHERE p.stock_quantity <= p.stock_threshold
        ORDER BY (p.stock_threshold - p.stock_quantity) DESC
        """)
        return db.cursor.fetchall()

    @staticmethod
    def get_expiring_products(db, days=30):
        """Son kullanma tarihi yaklaşan ürünleri getirir."""
        from datetime import datetime, timedelta

        # Bugünden itibaren belirtilen gün sayısı içindeki tarihi hesapla
        target_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        db.cursor.execute("""
            SELECT p.id, p.name, sm.expiry_date, 
                   julianday(sm.expiry_date) - julianday('now') as days_left
            FROM products p
            JOIN stock_movements sm ON p.id = sm.product_id
            WHERE sm.expiry_date IS NOT NULL 
              AND sm.expiry_date <= ?
              AND sm.expiry_date >= date('now')
            GROUP BY p.id
            ORDER BY days_left
            """, (target_date,))

        return db.cursor.fetchall()