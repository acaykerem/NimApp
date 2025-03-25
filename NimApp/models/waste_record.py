from datetime import datetime


class WasteRecord:
    def __init__(self, id=None, product_id=None, quantity=0, unit_type_id=None,
                 waste_date=None, reason="", notes=""):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_type_id = unit_type_id
        self.waste_date = waste_date if waste_date else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.reason = reason
        self.notes = notes

        # İlişkili nesne adları
        self.product_name = ""
        self.unit_type_name = ""

    @staticmethod
    def get_all(db):
        """Tüm zayi kayıtlarını veritabanından çeker."""
        db.cursor.execute("""
        SELECT wr.id, wr.product_id, wr.quantity, wr.unit_type_id, 
               wr.waste_date, wr.reason, wr.notes,
               p.name as product_name, ut.name as unit_type_name
        FROM waste_records wr
        JOIN products p ON wr.product_id = p.id
        JOIN unit_types ut ON wr.unit_type_id = ut.id
        ORDER BY wr.waste_date DESC
        """)

        records = []
        for row in db.cursor.fetchall():
            record = WasteRecord(
                row['id'], row['product_id'], row['quantity'], row['unit_type_id'],
                row['waste_date'], row['reason'], row['notes']
            )
            record.product_name = row['product_name']
            record.unit_type_name = row['unit_type_name']
            records.append(record)

        return records

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre zayi kaydı bilgisini getirir."""
        db.cursor.execute("""
        SELECT wr.id, wr.product_id, wr.quantity, wr.unit_type_id, 
               wr.waste_date, wr.reason, wr.notes,
               p.name as product_name, ut.name as unit_type_name
        FROM waste_records wr
        JOIN products p ON wr.product_id = p.id
        JOIN unit_types ut ON wr.unit_type_id = ut.id
        WHERE wr.id = ?
        """, (id,))

        row = db.cursor.fetchone()
        if row:
            record = WasteRecord(
                row['id'], row['product_id'], row['quantity'], row['unit_type_id'],
                row['waste_date'], row['reason'], row['notes']
            )
            record.product_name = row['product_name']
            record.unit_type_name = row['unit_type_name']
            return record
        return None

    def save(self, db):
        """Zayi kaydını veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                """INSERT INTO waste_records 
                   (product_id, quantity, unit_type_id, waste_date, reason, notes) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (self.product_id, self.quantity, self.unit_type_id,
                 self.waste_date, self.reason, self.notes)
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
                   (product_id, quantity, movement_type, description, date) 
                   VALUES (?, ?, 'OUT', ?, ?)""",
                (self.product_id, self.quantity, f"Zayi (Sebep: {self.reason})", self.waste_date)
            )
        else:
            # Mevcut miktarı al
            db.cursor.execute("SELECT quantity FROM waste_records WHERE id = ?", (self.id,))
            old_quantity = db.cursor.fetchone()['quantity']

            # Kaydı güncelle
            db.cursor.execute(
                """UPDATE waste_records 
                   SET product_id = ?, quantity = ?, unit_type_id = ?, 
                       waste_date = ?, reason = ?, notes = ? 
                   WHERE id = ?""",
                (self.product_id, self.quantity, self.unit_type_id,
                 self.waste_date, self.reason, self.notes, self.id)
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
                       (product_id, quantity, movement_type, description, date) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (self.product_id, abs(quantity_diff), movement_type,
                     f"Zayi Düzenleme (Sebep: {self.reason})", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )

        db.connection.commit()
        return self.id

    def delete(self, db):
        """Zayi kaydını veritabanından siler."""
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
                (self.product_id, self.quantity, f"Zayi Silme (ID: {self.id})",
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            # Kaydı sil
            db.cursor.execute("DELETE FROM waste_records WHERE id = ?", (self.id,))
            db.connection.commit()
            return True
        return False