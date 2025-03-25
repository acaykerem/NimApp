class SalesChannel:
    def __init__(self, id=None, name="", description=""):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def get_all(db):
        """Tüm satış kanallarını veritabanından çeker."""
        db.cursor.execute("SELECT id, name, description FROM sales_channels")
        return [SalesChannel(row['id'], row['name'], row['description'])
                for row in db.cursor.fetchall()]

    @staticmethod
    def get_by_id(db, id):
        """ID'ye göre satış kanalı bilgisini getirir."""
        db.cursor.execute("SELECT id, name, description FROM sales_channels WHERE id = ?", (id,))
        row = db.cursor.fetchone()
        if row:
            return SalesChannel(row['id'], row['name'], row['description'])
        return None