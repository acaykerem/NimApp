import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.category import Category
from models.product import Product


class ProductDialog:
    def __init__(self, parent, db, product=None):
        self.parent = parent
        self.db = db
        self.product = product

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Ürün Ekle/Düzenle")
        self.top.geometry("500x600")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Form çerçevesi
        form_frame = ctk.CTkFrame(self.top)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form başlığı
        title = "Ürün Düzenle" if product else "Yeni Ürün Ekle"
        ctk.CTkLabel(form_frame, text=title, font=("Arial", 16)).pack(pady=10)

        # Form alanları
        ctk.CTkLabel(form_frame, text="Kategori:").pack(anchor="w", padx=5, pady=5)

        # Kategorileri çek
        categories = Category.get_all(self.db)
        category_names = [c.name for c in categories]
        self.category_ids = [c.id for c in categories]

        self.category_var = ctk.StringVar()
        self.category_combobox = ctk.CTkComboBox(form_frame, values=category_names, variable=self.category_var,
                                                 width=300)
        self.category_combobox.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Ürün Adı:").pack(anchor="w", padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(form_frame, width=300)
        self.name_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Açıklama:").pack(anchor="w", padx=5, pady=5)
        self.description_entry = ctk.CTkTextbox(form_frame, width=300, height=100)
        self.description_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Stok Miktarı:").pack(anchor="w", padx=5, pady=5)
        self.stock_entry = ctk.CTkEntry(form_frame, width=300)
        self.stock_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Stok Eşiği:").pack(anchor="w", padx=5, pady=5)
        self.threshold_entry = ctk.CTkEntry(form_frame, width=300)
        self.threshold_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Barkod:").pack(anchor="w", padx=5, pady=5)
        self.barcode_entry = ctk.CTkEntry(form_frame, width=300)
        self.barcode_entry.pack(anchor="w", padx=5, pady=5)

        # Hammadde seçeneği
        self.is_raw_var = ctk.BooleanVar()
        ctk.CTkCheckBox(form_frame, text="Hammadde/Bileşen", variable=self.is_raw_var).pack(anchor="w", padx=5, pady=10)

        # Buton çerçevesi
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="İptal", command=self.top.destroy).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Kaydet", command=self.save_product).pack(side="left", padx=10)

        # Eğer ürün düzenleme ise formu doldur
        if self.product:
            self.fill_form()

    def fill_form(self):
        """Ürün bilgileriyle formu doldurur."""
        # Kategori seç
        if self.product.category_id and self.product.category_id in self.category_ids:
            index = self.category_ids.index(self.product.category_id)
            self.category_combobox.set(self.category_combobox._values[index])

        self.name_entry.insert(0, self.product.name)
        self.description_entry.insert("1.0", self.product.description if self.product.description else "")
        self.stock_entry.insert(0, str(self.product.stock_quantity))
        self.threshold_entry.insert(0, str(self.product.stock_threshold))
        self.barcode_entry.insert(0, self.product.barcode if self.product.barcode else "")
        self.is_raw_var.set(self.product.is_raw_material)

    def save_product(self):
        """Ürünü kaydeder."""
        name = self.name_entry.get().strip()
        description = self.description_entry.get("1.0", "end-1c").strip()

        # Zorunlu alan kontrolü
        if not name:
            messagebox.showwarning("Uyarı", "Ürün adı boş olamaz.")
            return

        # Kategori ID'sini al
        category_name = self.category_var.get()
        category_id = None

        if category_name and category_name in self.category_combobox._values:
            index = self.category_combobox._values.index(category_name)
            category_id = self.category_ids[index]

        # Stok ve eşik değerlerini al
        try:
            stock_quantity = float(self.stock_entry.get()) if self.stock_entry.get() else 0
        except ValueError:
            messagebox.showwarning("Uyarı", "Stok miktarı sayısal olmalıdır.")
            return

        try:
            stock_threshold = float(self.threshold_entry.get()) if self.threshold_entry.get() else 5
        except ValueError:
            messagebox.showwarning("Uyarı", "Stok eşiği sayısal olmalıdır.")
            return

        barcode = self.barcode_entry.get().strip()
        is_raw_material = self.is_raw_var.get()

        # Ürün objesini oluştur veya güncelle
        if self.product:
            self.product.category_id = category_id
            self.product.name = name
            self.product.description = description
            self.product.stock_quantity = stock_quantity
            self.product.stock_threshold = stock_threshold
            self.product.barcode = barcode
            self.product.is_raw_material = is_raw_material
        else:
            self.product = Product(None, category_id, name, description, stock_quantity,
                                   stock_threshold, barcode, is_raw_material)

        # Kaydet
        self.product.save(self.db)
        messagebox.showinfo("Bilgi", "Ürün başarıyla kaydedildi.")
        self.top.destroy()