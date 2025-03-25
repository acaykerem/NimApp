from datetime import datetime


class PurchaseRecord:
    def __init__(self, id=None, product_id=None, supplier_id=None, quantity=0,
                 unit_type_id=None, purchase_price=0, purchase_date=None, notes=""):
        self.id = id
        self.product_id = product_id
        self.supplier_id = supplier_id
        self.quantity = quantity
        self.unit_type_id = unit_type_id
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date if purchase_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notes = notes

        # İlişkili nesne adları
        self.product_name = ""
        self.supplier_name = ""
        self.unit_type_name = ""

    @staticmethod
    def get_all(db):
        """Tüm alım kayıtlarını veritabanından çeker."""
        db.cursor.execute("""
        SELECT pr.id, pr.product_id, pr.supplier_id, pr.quantity, pr.unit_type_id, 
               pr.purchase_price, pr.purchase_date, pr.notes,
               p.name as product_name, s.name as supplier_name, ut.name as unit_type_name
        FROM purchase_records pr
        JOIN products p ON pr.product_id = p.id
        JOIN suppliers s ON pr.supplier_id = s.id
        JOIN unit_types ut ON pr.unit_type_id = ut.id
        ORDER BY pr.purchase_date DESC
        """)

        records = []
        for row in db.cursor.fetchall():
            record = PurchaseRecord(
                row['id'], row['product_id'], row['supplier_id'], row['quantity'],
                row['unit_type_id'], row['purchase_price'], row['purchase_date'], row['notes']
            )
            record.product_name = row['product_name']
            record.supplier_name = row['supplier_name']
            record.unit_type_name = row['unit_type_name']
            records.append(record)

        return records

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre alım kaydı bilgisini getirir."""
        db.cursor.execute("""
        SELECT pr.id, pr.product_id, pr.supplier_id, pr.quantity, pr.unit_type_id, 
               pr.purchase_price, pr.purchase_date, pr.notes,
               p.name as product_name, s.name as supplier_name, ut.name as unit_type_name
        FROM purchase_records pr
        JOIN products p ON pr.product_id = p.id
        JOIN suppliers s ON pr.supplier_id = s.id
        JOIN unit_types ut ON pr.unit_type_id = ut.id
        WHERE pr.id = ?
        """, (id,))

        row = db.cursor.fetchone()
        if row:
            record = PurchaseRecord(
                row['id'], row['product_id'], row['supplier_id'], row['quantity'],
                row['unit_type_id'], row['purchase_price'], row['purchase_date'], row['notes']
            )
            record.product_name = row['product_name']
            record.supplier_name = row['supplier_name']
            record.unit_type_name = row['unit_type_name']
            return record
        return None

    def save(self, db):
        """Alım kaydını veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                """INSERT INTO purchase_records 
                   (product_id, supplier_id, quantity, unit_type_id, purchase_price, purchase_date, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.product_id, self.supplier_id, self.quantity, self.unit_type_id,
                 self.purchase_price, self.purchase_date, self.notes)
            )
            self.id = db.cursor.lastrowid

            # Ürün stoğunu güncelle
            db.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                (self.quantity, self.product_id)
            )

            # Stok hareketi kaydet
            db.cursor.execute(
                """INSERT INTO stock_movements 
                   (product_id, quantity, movement_type, supplier_id, description, date) 
                   VALUES (?, ?, 'IN', ?, ?, ?)""",
                (self.product_id, self.quantity, self.supplier_id,
                 f"Satın Alma (ID: {self.id})", self.purchase_date)
            )
        else:
            # Mevcut miktarı al
            db.cursor.execute("SELECT quantity FROM purchase_records WHERE id = ?", (self.id,))
            old_quantity = db.cursor.fetchone()['quantity']

            # Kaydı güncelle
            db.cursor.execute(
                """UPDATE purchase_records 
                   SET product_id = ?, supplier_id = ?, quantity = ?, unit_type_id = ?, 
                       purchase_price = ?, purchase_date = ?, notes = ? 
                   WHERE id = ?""",
                (self.product_id, self.supplier_id, self.quantity, self.unit_type_id,
                 self.purchase_price, self.purchase_date, self.notes, self.id)
            )

            # Ürün stoğunu güncelle (fark kadar)
            quantity_diff = self.quantity - old_quantity
            if quantity_diff != 0:
                db.cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + ? WHERE id = ?",
                    (quantity_diff, self.product_id)
                )

                # Stok hareketi kaydet
                movement_type = "IN" if quantity_diff > 0 else "OUT"
                db.cursor.execute(
                    """INSERT INTO stock_movements 
                       (product_id, quantity, movement_type, supplier_id, description, date) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (self.product_id, abs(quantity_diff), movement_type, self.supplier_id,
                     f"Satın Alma Düzenleme (ID: {self.id})", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )

        db.connection.commit()
        return self.id

    def delete(self, db):
        """Alım kaydını veritabanından siler."""
        if self.id:
            # Önce stoktan düşelim
            db.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE id = ?",
                (self.quantity, self.product_id)
            )

            # Stok hareketi kaydet
            db.cursor.execute(
                """INSERT INTO stock_movements 
                   (product_id, quantity, movement_type, description, date) 
                   VALUES (?, ?, 'OUT', ?, ?)""",
                (self.product_id, self.quantity, f"Satın Alma Silme (ID: {self.id})",
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            # Kaydı sil
            db.cursor.execute("DELETE FROM purchase_records WHERE id = ?", (self.id,))
            db.connection.commit()
            return True
        return False