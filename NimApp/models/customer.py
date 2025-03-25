class Customer:
    def __init__(self, id=None, name="", phone="", email="", address="", notes=""):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.notes = notes

    @staticmethod
    def get_all(db):
        """Tüm müşterileri veritabanından çeker."""
        db.cursor.execute("SELECT id, name, phone, email, address, notes FROM customers")
        return [Customer(row['id'], row['name'], row['phone'], row['email'], row['address'], row['notes'])
                for row in db.cursor.fetchall()]

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre müşteri bilgisini getirir."""
        db.cursor.execute("SELECT id, name, phone, email, address, notes FROM customers WHERE id = ?", (id,))
        row = db.cursor.fetchone()
        if row:
            return Customer(row['id'], row['name'], row['phone'], row['email'], row['address'], row['notes'])
        return None

    def save(self, db):
        """Müşteriyi veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                "INSERT INTO customers (name, phone, email, address, notes) VALUES (?, ?, ?, ?, ?)",
                (self.name, self.phone, self.email, self.address, self.notes)
            )
            self.id = db.cursor.lastrowid
        else:
            db.cursor.execute(
                "UPDATE customers SET name = ?, phone = ?, email = ?, address = ?, notes = ? WHERE id = ?",
                (self.name, self.phone, self.email, self.address, self.notes, self.id)
            )
        db.connection.commit()
        return self.id

    def delete(self, db):
        """Müşteriyi veritabanından siler."""
        if self.id:
            db.cursor.execute("DELETE FROM customers WHERE id = ?", (self.id,))
            db.connection.commit()
            return True
        return False