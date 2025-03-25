import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime, timedelta

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.product import Product
from models.supplier import Supplier
from models.sales_channel import SalesChannel


class StockDialog:
    def __init__(self, parent, db, movement_type="IN"):
        self.parent = parent
        self.db = db
        self.movement_type = movement_type  # IN: Giriş, OUT: Çıkış

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        title = "Stok Girişi" if movement_type == "IN" else "Stok Çıkışı"
        self.top.title(title)
        self.top.geometry("600x600")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Ana çerçeve
        main_frame = ctk.CTkFrame(self.top)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form başlığı
        ctk.CTkLabel(main_frame, text=title, font=("Arial", 16)).pack(pady=10)

        # Form içeriği
        form_frame = ctk.CTkScrollableFrame(main_frame, width=550, height=450)
        form_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Ürün seçimi
        ctk.CTkLabel(form_frame, text="Ürün:").pack(anchor="w", padx=5, pady=5)

        # Ürünleri çek
        self.products = Product.get_all(self.db)
        product_names = [f"{p.name} (Stok: {p.stock_quantity})" for p in self.products]

        self.product_var = ctk.StringVar()
        self.product_combobox = ctk.CTkComboBox(form_frame, values=product_names, variable=self.product_var, width=400)
        self.product_combobox.pack(anchor="w", padx=5, pady=5)

        # Miktar
        ctk.CTkLabel(form_frame, text="Miktar:").pack(anchor="w", padx=5, pady=5)
        self.quantity_entry = ctk.CTkEntry(form_frame, width=200)
        self.quantity_entry.pack(anchor="w", padx=5, pady=5)

        # Tedarikçi/Satış Kanalı seçimi
        if movement_type == "IN":
            ctk.CTkLabel(form_frame, text="Tedarikçi:").pack(anchor="w", padx=5, pady=5)

            # Tedarikçileri çek
            self.suppliers = Supplier.get_all(self.db)
            supplier_names = [s.name for s in self.suppliers]

            self.supplier_var = ctk.StringVar()
            self.supplier_combobox = ctk.CTkComboBox(form_frame, values=supplier_names, variable=self.supplier_var,
                                                     width=400)
            self.supplier_combobox.pack(anchor="w", padx=5, pady=5)

            # Üretim tarihi
            ctk.CTkLabel(form_frame, text="Üretim Tarihi:").pack(anchor="w", padx=5, pady=5)
            date_frame = ctk.CTkFrame(form_frame)
            date_frame.pack(anchor="w", padx=5, pady=5)

            self.prod_day_var = ctk.StringVar(value=str(datetime.now().day))
            self.prod_month_var = ctk.StringVar(value=str(datetime.now().month))
            self.prod_year_var = ctk.StringVar(value=str(datetime.now().year))

            ctk.CTkEntry(date_frame, width=50, textvariable=self.prod_day_var).pack(side="left", padx=2)
            ctk.CTkLabel(date_frame, text="/").pack(side="left")
            ctk.CTkEntry(date_frame, width=50, textvariable=self.prod_month_var).pack(side="left", padx=2)
            ctk.CTkLabel(date_frame, text="/").pack(side="left")
            ctk.CTkEntry(date_frame, width=80, textvariable=self.prod_year_var).pack(side="left", padx=2)

            # Son kullanma tarihi
            ctk.CTkLabel(form_frame, text="Son Kullanma Tarihi:").pack(anchor="w", padx=5, pady=5)
            date_frame = ctk.CTkFrame(form_frame)
            date_frame.pack(anchor="w", padx=5, pady=5)

            # Varsayılan olarak 1 yıl sonrasını ayarla
            next_year = datetime.now() + timedelta(days=365)
            self.exp_day_var = ctk.StringVar(value=str(next_year.day))
            self.exp_month_var = ctk.StringVar(value=str(next_year.month))
            self.exp_year_var = ctk.StringVar(value=str(next_year.year))

            ctk.CTkEntry(date_frame, width=50, textvariable=self.exp_day_var).pack(side="left", padx=2)
            ctk.CTkLabel(date_frame, text="/").pack(side="left")
            ctk.CTkEntry(date_frame, width=50, textvariable=self.exp_month_var).pack(side="left", padx=2)
            ctk.CTkLabel(date_frame, text="/").pack(side="left")
            ctk.CTkEntry(date_frame, width=80, textvariable=self.exp_year_var).pack(side="left", padx=2)

            # Parti numarası
            ctk.CTkLabel(form_frame, text="Parti Numarası:").pack(anchor="w", padx=5, pady=5)
            self.batch_entry = ctk.CTkEntry(form_frame, width=200)
            self.batch_entry.pack(anchor="w", padx=5, pady=5)
        else:  # OUT
            ctk.CTkLabel(form_frame, text="Satış Kanalı:").pack(anchor="w", padx=5, pady=5)

            # Satış kanallarını çek
            self.channels = SalesChannel.get_all(self.db)
            channel_names = [c.name for c in self.channels]

            self.channel_var = ctk.StringVar()
            self.channel_combobox = ctk.CTkComboBox(form_frame, values=channel_names, variable=self.channel_var,
                                                    width=400)
            self.channel_combobox.pack(anchor="w", padx=5, pady=5)

        # Açıklama
        ctk.CTkLabel(form_frame, text="Açıklama:").pack(anchor="w", padx=5, pady=5)
        self.description_entry = ctk.CTkTextbox(form_frame, width=400, height=100)
        self.description_entry.pack(anchor="w", padx=5, pady=5)

        # Buton çerçevesi
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)

        ctk.CTkButton(button_frame, text="İptal", command=self.top.destroy).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Kaydet", command=self.save_stock_movement).pack(side="left", padx=10)

    def save_stock_movement(self):
        """Stok hareketini kaydeder."""
        # Ürün seçimi kontrolü
        product_index = self.product_combobox._values.index(self.product_var.get()) if self.product_var.get() else -1
        if product_index == -1:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
            return

        product = self.products[product_index]

        # Miktar kontrolü
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Miktar pozitif olmalıdır.")
        except ValueError as e:
            messagebox.showwarning("Uyarı", f"Geçersiz miktar: {str(e)}")
            return

        # Stok çıkışında yeterli stok kontrolü
        if self.movement_type == "OUT" and quantity > product.stock_quantity:
            messagebox.showwarning("Uyarı", f"Stokta yeterli ürün yok. Mevcut stok: {product.stock_quantity}")
            return

        # Açıklama
        description = self.description_entry.get("1.0", "end-1c").strip()

        # Hareket tipine göre ek bilgileri al
        supplier_id = None
        production_date = None
        expiry_date = None
        batch_number = None
        sales_channel_id = None

        if self.movement_type == "IN":
            # Tedarikçi kontrolü
            supplier_index = self.supplier_combobox._values.index(
                self.supplier_var.get()) if self.supplier_var.get() else -1
            if supplier_index == -1:
                messagebox.showwarning("Uyarı", "Lütfen bir tedarikçi seçin.")
                return

            supplier_id = self.suppliers[supplier_index].id

            # Tarihleri kontrol et ve formatla
            try:
                prod_day = int(self.prod_day_var.get())
                prod_month = int(self.prod_month_var.get())
                prod_year = int(self.prod_year_var.get())
                production_date = f"{prod_year:04d}-{prod_month:02d}-{prod_day:02d}"

                # Geçerli tarih kontrolü
                datetime(prod_year, prod_month, prod_day)
            except ValueError:
                messagebox.showwarning("Uyarı", "Geçersiz üretim tarihi.")
                return

            try:
                exp_day = int(self.exp_day_var.get())
                exp_month = int(self.exp_month_var.get())
                exp_year = int(self.exp_year_var.get())
                expiry_date = f"{exp_year:04d}-{exp_month:02d}-{exp_day:02d}"

                # Geçerli tarih kontrolü
                datetime(exp_year, exp_month, exp_day)
            except ValueError:
                messagebox.showwarning("Uyarı", "Geçersiz son kullanma tarihi.")
                return

            batch_number = self.batch_entry.get().strip()
        else:  # OUT
            # Satış kanalı kontrolü
            channel_index = self.channel_combobox._values.index(
                self.channel_var.get()) if self.channel_var.get() else -1
            if channel_index == -1:
                messagebox.showwarning("Uyarı", "Lütfen bir satış kanalı seçin.")
                return

            sales_channel_id = self.channels[channel_index].id

        # Stok güncellemesi yap
        product.update_stock(
            self.db,
            quantity,
            self.movement_type,
            supplier_id,
            production_date,
            expiry_date,
            batch_number,
            description,
            sales_channel_id
        )

        messagebox.showinfo("Bilgi", "Stok hareketi başarıyla kaydedildi.")
        self.top.destroy()