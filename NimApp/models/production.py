from datetime import datetime


class ProductionOrder:
    def __init__(self, id=None, product_id=None, quantity=0, status="PENDING", date=None, notes=""):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.status = status
        self.date = date if date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes = notes
        self.product_name = ""  # Ürün adını tutmak için
        self.components = []  # Bileşenleri tutmak için

    @staticmethod
    def get_all(db):
        """Tüm üretim emirlerini getirir."""
        db.cursor.execute("""
        SELECT po.id, po.product_id, po.quantity, po.status, po.date, po.notes, p.name as product_name
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        ORDER BY po.date DESC
        """)

        orders = []
        for row in db.cursor.fetchall():
            order = ProductionOrder(
                row['id'], row['product_id'], row['quantity'],
                row['status'], row['date'], row['notes']
            )
            order.product_name = row['product_name']
            orders.append(order)

        return orders

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre üretim emrini getirir."""
        db.cursor.execute("""
        SELECT po.id, po.product_id, po.quantity, po.status, po.date, po.notes, p.name as product_name
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        WHERE po.id = ?
        """, (id,))

        row = db.cursor.fetchone()
        if not row:
            return None

        order = ProductionOrder(
            row['id'], row['product_id'], row['quantity'],
            row['status'], row['date'], row['notes']
        )
        order.product_name = row['product_name']

        # Bileşenleri de yükle
        db.cursor.execute("""
        SELECT pd.id, pd.component_id, pd.quantity_needed, pd.quantity_used, p.name as component_name
        FROM production_details pd
        JOIN products p ON pd.component_id = p.id
        WHERE pd.production_order_id = ?
        """, (id,))

        order.components = [dict(row) for row in db.cursor.fetchall()]

        return order

    def save(self, db):
        """Üretim emrini kaydeder."""
        if self.id is None:
            # Yeni kayıt
            db.cursor.execute(
                """INSERT INTO production_orders 
                   (product_id, quantity, status, date, notes) 
                   VALUES (?, ?, ?, ?, ?)""",
                (self.product_id, self.quantity, self.status, self.date, self.notes)
            )
            self.id = db.cursor.lastrowid
        else:
            # Güncelleme
            db.cursor.execute(
                """UPDATE production_orders 
                   SET product_id = ?, quantity = ?, status = ?, date = ?, notes = ? 
                   WHERE id = ?""",
                (self.product_id, self.quantity, self.status, self.date, self.notes, self.id)
            )

        db.connection.commit()
        return self.id

    def add_component(self, db, component_id, quantity_needed):
        """Üretim emrine bileşen ekler."""
        db.cursor.execute(
            """INSERT INTO production_details 
               (production_order_id, component_id, quantity_needed, quantity_used) 
               VALUES (?, ?, ?, 0)""",
            (self.id, component_id, quantity_needed)
        )
        db.connection.commit()

    def update_component(self, db, component_id, quantity_used):
        """Bileşenin kullanılan miktarını günceller."""
        db.cursor.execute(
            """UPDATE production_details 
               SET quantity_used = ? 
               WHERE production_order_id = ? AND component_id = ?""",
            (quantity_used, self.id, component_id)
        )
        db.connection.commit()

    def process(self, db):
        """Üretim emrini işler (hammaddeleri kullanır ve ürün üretir)."""
        # Üretim durumunu kontrol et
        if self.status != "PENDING":
            raise ValueError("Bu üretim emri zaten işlenmiş.")

        # Bileşenleri kontrol et
        db.cursor.execute("""
        SELECT pd.component_id, pd.quantity_needed, p.stock_quantity, p.name
        FROM production_details pd
        JOIN products p ON pd.component_id = p.id
        WHERE pd.production_order_id = ?
        """, (self.id,))

        components = db.cursor.fetchall()

        # Yeterli hammadde var mı kontrol et
        for component in components:
            if component['stock_quantity'] < component['quantity_needed']:
                raise ValueError(
                    f"Yetersiz stok: {component['name']} - Mevcut: {component['stock_quantity']}, Gereken: {component['quantity_needed']}")

        # Veritabanı işlemi başlat
        db.connection.execute("BEGIN TRANSACTION")

        try:
            # Hammaddeleri stoktan düş
            for component in components:
                # Hammadde stoğunu güncelle
                db.cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                    (component['quantity_needed'], component['component_id'])
                )

                # Stok hareketi kaydet
                db.cursor.execute(
                    """INSERT INTO stock_movements 
                      (product_id, quantity, movement_type, description, date) 
                      VALUES (?, ?, 'OUT', ?, ?)""",
                    (
                        component['component_id'],
                        component['quantity_needed'],
                        f"Üretim Kullanımı (Üretim No: {self.id})",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )

                # Bileşen kullanım miktarını güncelle
                db.cursor.execute(
                    """UPDATE production_details 
                       SET quantity_used = ? 
                       WHERE production_order_id = ? AND component_id = ?""",
                    (component['quantity_needed'], self.id, component['component_id'])
                )

            # Üretilen ürünü stoğa ekle
            db.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (self.quantity, self.product_id)
            )

            # Stok hareketi kaydet
            db.cursor.execute(
                """INSERT INTO stock_movements 
                  (product_id, quantity, movement_type, description, date) 
                  VALUES (?, ?, 'IN', ?, ?)""",
                (
                    self.product_id,
                    self.quantity,
                    f"Üretim Girişi (Üretim No: {self.id})",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )

            # Üretim durumunu güncelle
            self.status = "COMPLETED"
            db.cursor.execute(
                "UPDATE production_orders SET status = 'COMPLETED' WHERE id = ?",
                (self.id,)
            )

            # İşlemi onayla
            db.connection.commit()

        except Exception as e:
            # Hata durumunda geri al
            db.connection.rollback()
            raise e