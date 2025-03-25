import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.product import Product
from models.customer import Customer
from models.sales_channel import SalesChannel
from models.unit_type import UnitType
from models.sales_record import SalesRecord


class SalesDialog:
    def __init__(self, parent, db, sales_record=None, sale_type="SALE"):
        self.parent = parent
        self.db = db
        self.sales_record = sales_record
        self.sale_type = sale_type if not sales_record else sales_record.sale_type

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)

        # Başlık belirleme
        if sales_record:
            title = "Satış Kaydı Düzenle"
        else:
            if sale_type == "SALE":
                title = "Yeni Satış Kaydı"
            elif sale_type == "SAMPLE":
                title = "Numune Kaydı"
            else:  # GIFT
                title = "Hediye Kaydı"

        self.top.title(title)
        self.top.geometry("600x650")
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
        product_names = [f"{p.name} (Stok: {p.stock_quantity})" for p in self.products]

        self.product_var = ctk.StringVar()
        self.product_combobox = ctk.CTkComboBox(form_frame, values=product_names, variable=self.product_var, width=400)
        self.product_combobox.pack(anchor="w", padx=5, pady=5)

        # Müşteri seçimi
        ctk.CTkLabel(form_frame, text="Müşteri:").pack(anchor="w", padx=5, pady=5)

        # Müşterileri çek
        self.customers = Customer.get_all(self.db)
        customer_names = [c.name for c in self.customers]

        self.customer_var = ctk.StringVar()
        self.customer_combobox = ctk.CTkComboBox(form_frame, values=customer_names, variable=self.customer_var,
                                                 width=400)
        self.customer_combobox.pack(anchor="w", padx=5, pady=5)

        # Satış kanalı seçimi
        ctk.CTkLabel(form_frame, text="Satış Kanalı:").pack(anchor="w", padx=5, pady=5)

        # Satış kanallarını çek
        self.sales_channels = SalesChannel.get_all(self.db)
        channel_names = [sc.name for sc in self.sales_channels]

        self.channel_var = ctk.StringVar()
        self.channel_combobox = ctk.CTkComboBox(form_frame, values=channel_names, variable=self.channel_var, width=400)
        self.channel_combobox.pack(anchor="w", padx=5, pady=5)

        # Birim tipi seçimi
        ctk.CTkLabel(form_frame, text="Birim Tipi:").pack(anchor="w", padx=5, pady=5)

        # Birim tiplerini çek
        self.unit_types = UnitType.get_all(self.db)
        unit_type_names = [ut.name for ut in self.unit_types]

        self.unit_type_var = ctk.StringVar()
        self.unit_type_combobox = ctk.CTkComboBox(form_frame, values=unit_type_names, variable=self.unit_type_var,
                                                  width=400)
        self.unit_type_combobox.pack(anchor="w", padx=5, pady=5)

        # Miktar
        ctk.CTkLabel(form_frame, text="Miktar:").pack(anchor="w", padx=5, pady=5)
        self.quantity_entry = ctk.CTkEntry(form_frame, width=400)
        self.quantity_entry.pack(anchor="w", padx=5, pady=5)

        # Satış Fiyatı (sadece satış için)
        if self.sale_type == "SALE":
            ctk.CTkLabel(form_frame, text="Satış Fiyatı:").pack(anchor="w", padx=5, pady=5)
            self.price_entry = ctk.CTkEntry(form_frame, width=400)
            self.price_entry.pack(anchor="w", padx=5, pady=5)

        # Satış Tarihi
        ctk.CTkLabel(form_frame, text="Satış Tarihi:").pack(anchor="w", padx=5, pady=5)

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
        self.notes_entry = ctk.CTkTextbox(form_frame, width=400, height=80)
        self.notes_entry.pack(anchor="w", padx=5, pady=5)

        # Buton çerçevesi
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="İptal", command=self.top.destroy).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Kaydet", command=self.save_sales).pack(side="left", padx=10)

        # Eğer satış kaydı düzenleme ise formu doldur
        if self.sales_record:
            self.fill_form()

    def fill_form(self):
        """Satış kaydı bilgileriyle formu doldurur."""
        # Ürün seç
        product_index = next((i for i, p in enumerate(self.products) if p.id == self.sales_record.product_id), -1)
        if product_index >= 0:
            self.product_combobox.set(self.product_combobox._values[product_index])

        # Müşteri seç
        customer_index = next((i for i, c in enumerate(self.customers) if c.id == self.sales_record.customer_id), -1)
        if customer_index >= 0:
            self.customer_combobox.set(self.customer_combobox._values[customer_index])

        # Satış kanalı seç
        channel_index = next(
            (i for i, sc in enumerate(self.sales_channels) if sc.id == self.sales_record.sales_channel_id), -1)
        if channel_index >= 0:
            self.channel_combobox.set(self.channel_combobox._values[channel_index])

        # Birim tipi seç
        unit_type_index = next((i for i, ut in enumerate(self.unit_types) if ut.id == self.sales_record.unit_type_id),
                               -1)
        if unit_type_index >= 0:
            self.unit_type_combobox.set(self.unit_type_combobox._values[unit_type_index])

        # Miktar
        self.quantity_entry.insert(0, str(self.sales_record.quantity))

        # Fiyat (sadece satış için)
        if self.sale_type == "SALE" and hasattr(self, 'price_entry'):
            self.price_entry.insert(0, str(self.sales_record.sale_price))

        # Tarih
        if self.sales_record.sale_date:
            try:
                date = datetime.strptime(self.sales_record.sale_date, "%Y-%m-%d %H:%M:%S")
                self.day_var.set(str(date.day))
                self.month_var.set(str(date.month))
                self.year_var.set(str(date.year))
            except:
                # Tarih formatı farklıysa, bugünü göster
                pass

        # Notlar
        self.notes_entry.insert("1.0", self.sales_record.notes if self.sales_record.notes else "")

    def save_sales(self):
        """Satış kaydını kaydeder."""
        # Ürün seçimi kontrolü
        product_index = next((i for i, name in enumerate(self.product_combobox._values)
                              if name == self.product_var.get()), -1)
        if product_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
            return

        # Müşteri seçimi kontrolü
        customer_index = self.customer_combobox._values.index(
            self.customer_var.get()) if self.customer_var.get() in self.customer_combobox._values else -1
        if customer_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen bir müşteri seçin.")
            return

        # Satış kanalı seçimi kontrolü
        channel_index = self.channel_combobox._values.index(
            self.channel_var.get()) if self.channel_var.get() in self.channel_combobox._values else -1
        if channel_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen bir satış kanalı seçin.")
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

        # Mevcut stok kontrolü
        product = self.products[product_index]
        current_stock = product.stock_quantity

        # Düzenleme ise, mevcut kaydın miktarını stoka ekle (çünkü ürün silme işlemi olacak)
        if self.sales_record:
            current_stock += self.sales_record.quantity

        if quantity > current_stock:
            messagebox.showwarning("Uyarı", f"Stokta yeterli ürün yok. Mevcut stok: