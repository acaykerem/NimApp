class UnitType:
    def __init__(self, id=None, name="", description=""):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_all(db):
        """Tüm birim tiplerini veritabanından çeker."""
        db.cursor.execute("SELECT id, name, description FROM unit_types")
        return [UnitType(row['id'], row['name'], row['description'])
                for row in db.cursor.fetchall()]

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre birim tipi bilgisini getirir."""
        db.cursor.execute("SELECT id, name, description FROM unit_types WHERE id = ?", (id,))
        row = db.cursor.fetchone()
        if row:
            return UnitType(row['id'], row['name'], row['description'])
        return None

    def save(self, db):
        """Birim tipini veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                "INSERT INTO unit_types (name, description) VALUES (?, ?)",
                (self.name, self.description)
            )
            self.id = db.cursor.lastrowid
        else:
            db.cursor.execute(
                "UPDATE unit_types SET name = ?, description = ? WHERE id = ?",
                (self.name, self.description, self.id)
            )
        db.connection.commit()
        return self.id