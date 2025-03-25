import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.product import Product
from models.supplier import Supplier
from models.unit_type import UnitType
from models.purchase_record import PurchaseRecord


class PurchaseDialog:
    def __init__(self, parent, db, purchase_record=None):
        self.parent = parent
        self.db = db
        self.purchase_record = purchase_record

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        title = "Alım Kaydı Düzenle" if purchase_record else "Yeni Alım Kaydı"
        self.top.title(title)
        self.top.geometry("600x600")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Form çerçevesi
        form_frame = ctk.CTkFrame(self.top)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form başlığı
        ctk.CTkLabel(form_frame, text=title, font=("Arial", 16)).pack(pady=10)

        # Ürün seçimi
        ctk.CTkLabel(form_frame, text="Ürün:").pack(anchor="w", padx=5, pady=5)

        # Ürünleri çek
        self.products = Product.get_all(self.db)
        product_names = [p.name for p in self.products]

        self.product_var = ctk.StringVar()
        self.product_combobox = ctk.CTkComboBox(form_frame, values=product_names, variable=self.product_var, width=300)
        self.product_combobox.pack(anchor="w", padx=5, pady=5)

        # Tedarikçi seçimi
        ctk.CTkLabel(form_frame, text="Tedarikçi:").pack(anchor="w", padx=5, pady=5)

        # Tedarikçileri çek
        self.suppliers = Supplier.get_all(self.db)
        supplier_names = [s.name for s in self.suppliers]

        self.supplier_var = ctk.StringVar()
        self.supplier_combobox = ctk.CTkComboBox(form_frame, values=supplier_names, variable=self.supplier_var,
                                                 width=300)
        self.supplier_combobox.pack(anchor="w", padx=5, pady=5)

        # Birim tipi seçimi
        ctk.CTkLabel(form_frame, text="Birim Tipi:").pack(anchor="w", padx=5, pady=5)

        # Birim tiplerini çek
        self.unit_types = UnitType.get_all(self.db)
        unit_type_names = [ut.name for ut in self.unit_types]

        self.unit_type_var = ctk.StringVar()
        self.unit_type_combobox = ctk.CTkComboBox(form_frame, values=unit_type_names, variable=self.unit_type_var,
                                                  width=300)
        self.unit_type_combobox.pack(anchor="w", padx=5, pady=5)

        # Miktar
        ctk.CTkLabel(form_frame, text="Miktar:").pack(anchor="w", padx=5, pady=5)
        self.quantity_entry = ctk.CTkEntry(form_frame, width=300)
        self.quantity_entry.pack(anchor="w", padx=5, pady=5)

        # Alım Fiyatı
        ctk.CTkLabel(form_frame, text="Alım Fiyatı:").pack(anchor="w", padx=5, pady=5)
        self.price_entry = ctk.CTkEntry(form_frame, width=300)
        self.price_entry.pack(anchor="w", padx=5, pady=5)

        # Alım Tarihi
        ctk.CTkLabel(form_frame, text="Alım Tarihi:").pack(anchor="w", padx=5, pady=5)

        date_frame = ctk.CTkFrame(form_frame)
        date_frame.pack(anchor="w", padx=5, pady=5)

        today = datetime.now()
        self.day_var = ctk.StringVar(value=str(today.day))
        self.month_var = ctk.StringVar(value=str(today.month))
        self.year_var = ctk.StringVar(value=str(today.year))

        self.day_entry = ctk.CTkEntry(date_frame, width=50, textvariable=self.day_var)
        self.day_entry.pack(side="left", padx=2)
        ctk.CTkLabel(date_frame, text="/").pack(side="left")
        self.month_entry = ctk.CTkEntry(date_frame, width=50, textvariable=self.month_var)
        self.month_entry.pack(side="left", padx=2)
        ctk.CTkLabel(date_frame, text="/").pack(side="left")
        self.year_entry = ctk.CTkEntry(date_frame, width=80, textvariable=self.year_var)
        self.year_entry.pack(side="left", padx=2)

        # Notlar
        ctk.CTkLabel(form_frame, text="Notlar:").pack(anchor="w", padx=5, pady=5)
        self.notes_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.notes_entry.pack(anchor="w", padx=5, pady=5)

        # Buton çerçevesi
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="İptal", command=self.top.destroy).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Kaydet", command=self.save_purchase).pack(side="left", padx=10)

        # Eğer alım kaydı düzenleme ise formu doldur
        if self.purchase_record:
            self.fill_form()

    def fill_form(self):
        """Alım kaydı bilgileriyle formu doldurur."""
        # Ürün seç
        product_index = next((i for i, p in enumerate(self.products) if p.id == self.purchase_record.product_id), -1)
        if product_index >= 0:
            self.product_combobox.set(self.product_combobox._values[product_index])

        # Tedarikçi seç
        supplier_index = next((i for i, s in enumerate(self.suppliers) if s.id == self.purchase_record.supplier_id), -1)
        if supplier_index >= 0:
            self.supplier_combobox.set(self.supplier_combobox._values[supplier_index])

        # Birim tipi seç
        unit_type_index = next(
            (i for i, ut in enumerate(self.unit_types) if ut.id == self.purchase_record.unit_type_id), -1)
        if unit_type_index >= 0:
            self.unit_type_combobox.set(self.unit_type_combobox._values[unit_type_index])

        # Miktar ve fiyat
        self.quantity_entry.insert(0, str(self.purchase_record.quantity))
        self.price_entry.insert(0, str(self.purchase_record.purchase_price))

        # Tarih
        if self.purchase_record.purchase_date:
            try:
                date = datetime.strptime(self.purchase_record.purchase_date, "%Y-%m-%d %H:%M:%S")
                self.day_var.set(str(date.day))
                self.month_var.set(str(date.month))
                self.year_var.set(str(date.year))
            except:
                # Tarih formatı farklıysa, bugünü göster
                pass

        # Notlar
        self.notes_entry.insert("1.0", self.purchase_record.notes if self.purchase_record.notes else "")

    def save_purchase(self):
        """Alım kaydını kaydeder."""
        # Ürün seçimi kontrolü
        product_index = self.product_combobox._values.index(
            self.product_var.get()) if self.product_var.get() in self.product_combobox._values else -1
        if product_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
            return

        # Tedarikçi seçimi kontrolü
        supplier_index = self.supplier_combobox._values.index(
            self.supplier_var.get()) if self.supplier_var.get() in self.supplier_combobox._values else -1
        if supplier_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen bir tedarikçi seçin.")
            return

        # Birim tipi seçimi kontrolü
        unit_type_index = self.unit_type_combobox._values.index(
            self.unit_type_var.get()) if self.unit_type_var.get() in self.unit_type_combobox._values else -1
        if unit_type_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen bir birim tipi seçin.")
            return

        # Miktar kontrolü
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError()
        except:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir miktar girin.")
            return

        # Fiyat kontrolü
        try:
            price = float(self.price_entry.get())
            if price < 0:
                raise ValueError()
        except:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir fiyat girin.")
            return

        # Tarih kontrolü
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            purchase_date = datetime(year, month, day).strftime("%Y-%m-%d %H:%M:%S")
        except:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir tarih girin.")
            return

        # Notlar
        notes = self.notes_entry.get("1.0", "end-1c").strip()

        # Alım kaydı objesini oluştur veya güncelle
        if self.purchase_record:
            self.purchase_record.product_id = self.products[product_index].id
            self.purchase_record.supplier_id = self.suppliers[supplier_index].id
            self.purchase_record.unit_type_id = self.unit_types[unit_type_index].id
            self.purchase_record.quantity = quantity
            self.purchase_record.purchase_price = price
            self.purchase_record.purchase_date = purchase_date
            self.purchase_record.notes = notes
        else:
            self.purchase_record = PurchaseRecord(
                None,
                self.products[product_index].id,
                self.suppliers[supplier_index].id,
                quantity,
                self.unit_types[unit_type_index].id,
                price,
                purchase_date,
                notes
            )

        # Kaydet
        self.purchase_record.save(self.db)
        messagebox.showinfo("Bilgi", "Alım kaydı başarıyla kaydedildi.")
        self.top.destroy()