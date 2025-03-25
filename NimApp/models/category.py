class Category:
    def __init__(self, id=None, name="", description=""):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_all(db):
        """Tüm kategorileri veritabanından çeker."""
        db.cursor.execute("SELECT id, name, description FROM categories")
        return [Category(row['id'], row['name'], row['description']) for row in db.cursor.fetchall()]

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre kategori bilgisini getirir."""
        db.cursor.execute("SELECT id, name, description FROM categories WHERE id = ?", (id,))
        row = db.cursor.fetchone()
        if row:
            return Category(row['id'], row['name'], row['description'])
        return None

    def save(self, db):
        """Kategoriyi veritabanına kaydeder."""
        if self.id is None:
            db.cursor.execute(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (self.name, self.description)
            )
            self.id = db.cursor.lastrowid
        else:
            db.cursor.execute(
                "UPDATE categories SET name = ?, description = ? WHERE id = ?",
                (self.name, self.description, self.id)
            )
        db.connection.commit()
        return self.id

    def delete(self, db):
        """Kategoriyi veritabanından siler."""
        if self.id:
            db.cursor.execute("DELETE FROM categories WHERE id = ?", (self.id,))
            db.connection.commit()
            return True
        return False