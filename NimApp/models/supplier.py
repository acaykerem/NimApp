class Supplier:
    def __init__(self, id=None, name="", phone="", email="", address=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address

    @staticmethod
    def get_all(db):
        """Tüm tedarikçileri veritabanından çeker."""
        db.cursor.execute("SELECT id, name, phone, email, address FROM suppliers")
        return [Supplier(row['id'], row['name'], row['phone'], row['email'], row['address'])
                for row in db.cursor.fetchall()]

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre tedarikçi bilgisini getirir."""
        db.cursor.execute("SELECT id, name, phone, email, address FROM suppliers WHERE id = ?", (id,))
        row = db.cursor.fetchone()
        if row:
            return Supplier(row['id'], row['name'], row['phone'], row['email'], row['address'])
        return None

    def save(self, db):
        """Tedarikçiyi veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                "INSERT INTO suppliers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                (self.name, self.phone, self.email, self.address)
            )
            self.id = db.cursor.lastrowid
        else:
            db.cursor.execute(
                "UPDATE suppliers SET name = ?, phone = ?, email = ?, address = ? WHERE id = ?",
                (self.name, self.phone, self.email, self.address, self.id)
            )
        db.connection.commit()
        return self.id

    def delete(self, db):
        """Tedarikçiyi veritabanından siler."""
        if self.id:
            db.cursor.execute("DELETE FROM suppliers WHERE id = ?", (self.id,))
            db.connection.commit()
            return True
        return False