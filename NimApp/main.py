import customtkinter as ctk
import os
import sys
from tkinter import messagebox

# Veritabanı ve modelleri içe aktarma
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database.database import Database
from views.main_window import MainWindow

# Uygulama teması
ctk.set_appearance_mode("System")  # Sistem temasını kullan (dark/light)
ctk.set_default_color_theme("blue")  # Mavi tema


class App:
    def __init__(self):
        self.db = Database()
        self.db.connect()

        # Ana pencere oluştur
        self.root = ctk.CTk()
        self.root.title("Stok Takip Sistemi")
        self.root.geometry("1200x700")

        # Ana pencere içeriğini yükle
        self.main_window = MainWindow(self.root, self.db)

        # Pencere kapatıldığında temizlik yap
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def run(self):
        self.root.mainloop()

    def on_closing(self):
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinize emin misiniz?"):
            self.db.close()
            self.root.destroy()


if __name__ == "__main__":
    app = App()
    app.run()