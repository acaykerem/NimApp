from datetime import datetime


class SalesRecord:
    def __init__(self, id=None, product_id=None, customer_id=None, sales_channel_id=None,
                 quantity=0, unit_type_id=None, sale_price=0, sale_date=None, sale_type="SALE", notes=""):
        self.id = id
        self.product_id = product_id
        self.customer_id = customer_id
        self.sales_channel_id = sales_channel_id
        self.quantity = quantity
        self.unit_type_id = unit_type_id
        self.sale_price = sale_price
        self.sale_date = sale_date if sale_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sale_type = sale_type  # 'SALE', 'SAMPLE', 'GIFT'
        self.notes = notes

        # İlişkili nesne adları
        self.product_name = ""
        self.customer_name = ""
        self.sales_channel_name = ""
        self.unit_type_name = ""

    @staticmethod
    def get_all(db):
        """Tüm satış kayıtlarını veritabanından çeker."""
        db.cursor.execute("""
        SELECT sr.id, sr.product_id, sr.customer_id, sr.sales_channel_id, sr.quantity, 
               sr.unit_type_id, sr.sale_price, sr.sale_date, sr.sale_type, sr.notes,
               p.name as product_name, c.name as customer_name, 
               sc.name as sales_channel_name, ut.name as unit_type_name
        FROM sales_records sr
        JOIN products p ON sr.product_id = p.id
        JOIN customers c ON sr.customer_id = c.id
        JOIN sales_channels sc ON sr.sales_channel_id = sc.id
        JOIN unit_types ut ON sr.unit_type_id = ut.id
        ORDER BY sr.sale_date DESC
        """)

        records = []
        for row in db.cursor.fetchall():
            record = SalesRecord(
                row['id'], row['product_id'], row['customer_id'], row['sales_channel_id'],
                row['quantity'], row['unit_type_id'], row['sale_price'],
                row['sale_date'], row['sale_type'], row['notes']
            )
            record.product_name = row['product_name']
            record.customer_name = row['customer_name']
            record.sales_channel_name = row['sales_channel_name']
            record.unit_type_name = row['unit_type_name']
            records.append(record)

        return records

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre satış kaydı bilgisini getirir."""
        db.cursor.execute("""
        SELECT sr.id, sr.product_id, sr.customer_id, sr.sales_channel_id, sr.quantity, 
               sr.unit_type_id, sr.sale_price, sr.sale_date, sr.sale_type, sr.notes,
               p.name as product_name, c.name as customer_name, 
               sc.name as sales_channel_name, ut.name as unit_type_name
        FROM sales_records sr
        JOIN products p ON sr.product_id = p.id
        JOIN customers c ON sr.customer_id = c.id
        JOIN sales_channels sc ON sr.sales_channel_id = sc.id
        JOIN unit_types ut ON sr.unit_type_id = ut.id
        WHERE sr.id = ?
        """, (id,))

        row = db.cursor.fetchone()
        if row:
            record = SalesRecord(
                row['id'], row['product_id'], row['customer_id'], row['sales_channel_id'],
                row['quantity'], row['unit_type_id'], row['sale_price'],
                row['sale_date'], row['sale_type'], row['notes']
            )
            record.product_name = row['product_name']
            record.customer_name = row['customer_name']
            record.sales_channel_name = row['sales_channel_name']
            record.unit_type_name = row['unit_type_name']
            return record
        return None

    def save(self, db):
        """Satış kaydını veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                """INSERT INTO sales_records 
                   (product_id, customer_id, sales_channel_id, quantity, unit_type_id, 
                    sale_price, sale_date, sale_type, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (self.product_id, self.customer_id, self.sales_channel_id, self.quantity,
                 self.unit_type_id, self.sale_price, self.sale_date, self.sale_type, self.notes)
            )
            self.id = db.cursor.lastrowid

            # Ürün stoğunu güncelle
            db.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (self.quantity, self.product_id)
            )

            # Stok hareketi kaydet
            db.cursor.execute(
                """INSERT INTO stock_movements 
                   (product_id, quantity, movement_type, sales_channel_id, description, date) 
                   VALUES (?, ?, 'OUT', ?, ?, ?)""",
                (self.product_id, self.quantity, self.sales_channel_id,
                 f"{self.sale_type} (ID: {self.id})", self.sale_date)
            )
        else:
            # Mevcut miktarı al
            db.cursor.execute("SELECT quantity FROM sales_records WHERE id = ?", (self.id,))
            old_quantity = db.cursor.fetchone()['quantity']

            # Kaydı güncelle
            db.cursor.execute(
                """UPDATE sales_records 
                   SET product_id = ?, customer_id = ?, sales_channel_id = ?, quantity = ?, 
                       unit_type_id = ?, sale_price = ?, sale_date = ?, sale_type = ?, notes = ? 
                   WHERE id = ?""",
                (self.product_id, self.customer_id, self.sales_channel_id, self.quantity,
                 self.unit_type_id, self.sale_price, self.sale_date, self.sale_type, self.notes, self.id)
            )

            # Ürün stoğunu güncelle (fark kadar)
            quantity_diff = self.quantity - old_quantity
            if quantity_diff != 0:
                db.cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                    (quantity_diff, self.product_id)
                )

                # Stok hareketi kaydet
                movement_type = "OUT" if quantity_diff > 0 else "IN"
                db.cursor.execute(
                    """INSERT INTO stock_movements 
                       (product_id, quantity, movement_type, sales_channel_id, description, date) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (self.product_id, abs(quantity_diff), movement_type, self.sales_channel_id,
                     f"{self.sale_type} Düzenleme (ID: {self.id})", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )

        db.connection.commit()
        return self.id

    def delete(self, db):
        """Satış kaydını veritabanından siler."""
        if self.id:
            # Önce stok güncelleyelim
            db.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (self.quantity, self.product_id)
            )

            # Stok hareketi kaydet
            db.cursor.execute(
                """INSERT INTO stock_movements 
                   (product_id, quantity, movement_type, description, date) 
                   VALUES (?, ?, 'IN', ?, ?)""",
                (self.product_id, self.quantity, f"{self.sale_type} Silme (ID: {self.id})",
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            # Kaydı sil
            db.cursor.execute("DELETE FROM sales_records WHERE id = ?", (self.id,))
            db.connection.commit()
            return True
        return False