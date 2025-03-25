import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys
from datetime import datetime

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.product import Product
from models.production import ProductionOrder


class ProductionDialog:
    def __init__(self, parent, db, production_id=None):
        self.parent = parent
        self.db = db

        # Üretim emrini yükle veya yeni oluştur
        self.production_order = None
        if production_id:
            self.production_order = ProductionOrder.get_by_id(db, production_id)

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        title = "Üretim Emri Düzenle" if self.production_order else "Yeni Üretim Emri"
        self.top.title(title)
        self.top.geometry("700x600")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Ana çerçeve
        main_frame = ctk.CTkFrame(self.top)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form çerçevesi
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", padx=5, pady=5)

        # Ürün seçimi
        ctk.CTkLabel(form_frame, text="Üretilecek Ürün:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Hammadde OLMAYAN ürünleri çek
        self.products = [p for p in Product.get_all(self.db) if not p.is_raw_material]
        product_names = [p.name for p in self.products]

        self.product_var = ctk.StringVar()
        self.product_combobox = ctk.CTkComboBox(form_frame, values=product_names, variable=self.product_var, width=300)
        self.product_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Miktar
        ctk.CTkLabel(form_frame, text="Üretim Miktarı:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.quantity_entry = ctk.CTkEntry(form_frame, width=150)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Notlar
        ctk.CTkLabel(form_frame, text="Notlar:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.notes_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.notes_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Bileşenler bölümü
        components_frame = ctk.CTkFrame(main_frame)
        components_frame.pack(fill="both", expand=True, padx=5, pady=10)

        ctk.CTkLabel(components_frame, text="Ürün Bileşenleri", font=("Arial", 14, "bold")).pack(pady=5)

        # Ürün bilgi çerçevesi
        self.info_frame = ctk.CTkFrame(components_frame)
        self.info_frame.pack(fill="x", padx=5, pady=5)

        self.component_info_label = ctk.CTkLabel(self.info_frame, text="Üretim için hammadde gereksinimi")
        self.component_info_label.pack(pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(components_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("component_id", "name", "stock", "needed", "status")
        self.component_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.component_tree.heading("component_id", text="ID")
        self.component_tree.heading("name", text="Bileşen Adı")
        self.component_tree.heading("stock", text="Mevcut Stok")
        self.component_tree.heading("needed", text="Gereken Miktar")
        self.component_tree.heading("status", text="Durum")

        # Sütun genişlikleri
        self.component_tree.column("component_id", width=50)
        self.component_tree.column("name", width=200)
        self.component_tree.column("stock", width=100)
        self.component_tree.column("needed", width=100)
        self.component_tree.column("status", width=100)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.component_tree.yview)
        self.component_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.component_tree.pack(fill="both", expand=True)

        # Butonlar çerçevesi
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=10)

        self.calculate_btn = ctk.CTkButton(button_frame, text="Bileşenleri Hesapla", command=self.calculate_components)
        self.calculate_btn.pack(side="left", padx=5)

        self.create_btn = ctk.CTkButton(button_frame, text="Üretim Emri Oluştur", command=self.create_production_order,
                                        state="disabled")
        self.create_btn.pack(side="left", padx=5)

        self.process_btn = ctk.CTkButton(button_frame, text="Üretimi Gerçekleştir", command=self.process_production,
                                         state="disabled")
        self.process_btn.pack(side="left", padx=5)

        ctk.CTkButton(button_frame, text="İptal", command=self.top.destroy).pack(side="right", padx=5)

        # Mevcut bir üretim emri varsa formu doldur
        if self.production_order:
            self.fill_form()

    def fill_form(self):
        """Üretim emri bilgileriyle formu doldurur."""
        # Ürün seç
        product_index = next((i for i, p in enumerate(self.products) if p.id == self.production_order.product_id), -1)
        if product_index >= 0:
            self.product_combobox.set(self.product_combobox._values[product_index])

        # Miktar
        self.quantity_entry.insert(0, str(self.production_order.quantity))

        # Notlar
        self.notes_entry.insert("1.0", self.production_order.notes)

        # Durum kontrolü
        if self.production_order.status == "PENDING":
            # Bileşenleri yükle
            self.load_components()
            self.create_btn.configure(state="disabled")
            self.process_btn.configure(state="normal")
        else:
            # Tamamlanmış üretim
            self.load_components()
            self.product_combobox.configure(state="disabled")
            self.quantity_entry.configure(state="disabled")
            self.notes_entry.configure(state="disabled")
            self.calculate_btn.configure(state="disabled")
            self.create_btn.configure(state="disabled")
            self.process_btn.configure(state="disabled")
            messagebox.showinfo("Bilgi", "Bu üretim emri tamamlanmış ve değiştirilemez.")

    def calculate_components(self):
        """Ürün bileşenlerini hesaplar ve gösterir."""
        # Tabloyu temizle
        for item in self.component_tree.get_children():
            self.component_tree.delete(item)

        # Üretilecek ürünü kontrol et
        product_index = self.product_combobox._values.index(
            self.product_var.get()) if self.product_var.get() in self.product_combobox._values else -1
        if product_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen üretilecek ürün seçin.")
            return

        product = self.products[product_index]

        # Üretim miktarını kontrol et
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir üretim miktarı girin.")
            return

        # Ürün bileşenlerini al
        self.db.cursor.execute("""
        SELECT pc.component_id, p.name, p.stock_quantity, pc.quantity
        FROM product_components pc
        JOIN products p ON pc.component_id = p.id
        WHERE pc.product_id = ?
        """, (product.id,))

        components = self.db.cursor.fetchall()

        if not components:
            messagebox.showinfo("Bilgi", "Bu ürünün tanımlanmış bileşeni bulunmamaktadır.")
            return

        # Bileşenleri tabloya ekle
        all_components_available = True
        for component in components:
            component_id = component['component_id']
            name = component['name']
            stock = component['stock_quantity']
            needed = component['quantity'] * quantity

            if stock >= needed:
                status = "Yeterli"
                tag = "ok"
            else:
                status = "Yetersiz"
                tag = "error"
                all_components_available = False

            self.component_tree.insert("", "end", values=(
                component_id, name, stock, needed, status
            ), tags=(tag,))

        # Yeşil ve kırmızı renk etiketleri
        self.component_tree.tag_configure("ok", background="#CCFFCC")
        self.component_tree.tag_configure("error", background="#FFCCCC")

        # Üretim oluşturma butonunu aktif/pasif yap
        self.create_btn.configure(state="normal" if all_components_available else "disabled")

        # Bilgi mesajı güncelle
        if all_components_available:
            self.component_info_label.configure(
                text=f"{quantity} adet {product.name} üretimi için tüm hammaddeler mevcut")
        else:
            self.component_info_label.configure(text=f"{quantity} adet {product.name} üretimi için yetersiz hammadde")

    def load_components(self):
        """Üretim emrinin bileşenlerini yükler ve gösterir."""
        if not self.production_order:
            return

        # Tabloyu temizle
        for item in self.component_tree.get_children():
            self.component_tree.delete(item)

        # Bileşenleri al
        components = self.production_order.components

        # Bileşenleri tabloya ekle
        all_components_available = True
        for component in components:
            # Güncel stok durumunu kontrol et
            self.db.cursor.execute("SELECT stock_quantity FROM products WHERE id = ?", (component['component_id'],))
            stock = self.db.cursor.fetchone()['stock_quantity']

            needed = component['quantity_needed']

            if stock >= needed:
                status = "Yeterli"
                tag = "ok"
            else:
                status = "Yetersiz"
                tag = "error"
                all_components_available = False

            self.component_tree.insert("", "end", values=(
                component['component_id'],
                component['component_name'],
                stock,
                needed,
                status
            ), tags=(tag,))

        # Yeşil ve kırmızı renk etiketleri
        self.component_tree.tag_configure("ok", background="#CCFFCC")
        self.component_tree.tag_configure("error", background="#FFCCCC")

        # Üretim butonunu aktif/pasif yap
        self.process_btn.configure(state="normal" if all_components_available else "disabled")

        # Bilgi mesajı güncelle
        product_name = self.production_order.product_name
        quantity = self.production_order.quantity

        if all_components_available:
            self.component_info_label.configure(
                text=f"{quantity} adet {product_name} üretimi için tüm hammaddeler mevcut")
        else:
            self.component_info_label.configure(text=f"{quantity} adet {product_name} üretimi için yetersiz hammadde")

    def create_production_order(self):
        """Üretim emri oluşturur."""
        # Üretilecek ürünü kontrol et
        product_index = self.product_combobox._values.index(
            self.product_var.get()) if self.product_var.get() in self.product_combobox._values else -1
        if product_index < 0:
            messagebox.showwarning("Uyarı", "Lütfen üretilecek ürün seçin.")
            return

        product = self.products[product_index]

        # Üretim miktarını kontrol et
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir üretim miktarı girin.")
            return

        # Notlar
        notes = self.notes_entry.get("1.0", "end-1c")

        # Ürün bileşenlerini al
        self.db.cursor.execute("""
        SELECT pc.component_id, p.name, p.stock_quantity, pc.quantity
        FROM product_components pc
        JOIN products p ON pc.component_id = p.id
        WHERE pc.product_id = ?
        """, (product.id,))

        components = self.db.cursor.fetchall()

        if not components:
            messagebox.showinfo("Bilgi", "Bu ürünün tanımlanmış bileşeni bulunmamaktadır.")
            return

        # Bileşenleri kontrol et (tekrar)
        all_components_available = True
        for component in components:
            if component['stock_quantity'] < component['quantity'] * quantity:
                all_components_available = False
                break

        if not all_components_available:
            if not messagebox.askyesno("Uyarı",
                                       "Bazı bileşenler için yeterli stok bulunmuyor. Yine de üretim emri oluşturmak istiyor musunuz?"):
                return

        try:
            # Üretim emrini oluştur
            production_order = ProductionOrder(
                product_id=product.id,
                quantity=quantity,
                status="PENDING",
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                notes=notes
            )

            # Kaydet
            production_id = production_order.save(self.db)

            # Bileşenleri ekle
            for component in components:
                production_order.add_component(
                    self.db,
                    component['component_id'],
                    component['quantity'] * quantity
                )

            # Eğer tüm bileşenler mevcutsa, üretim emrini hemen işlemek ister misiniz diye sor
            if all_components_available:
                if messagebox.askyesno("Bilgi",
                                       "Üretim emri oluşturuldu. Hemen üretimi gerçekleştirmek istiyor musunuz?"):
                    self.production_order = production_order
                    self.process_production()
                    return

            messagebox.showinfo("Bilgi", "Üretim emri başarıyla oluşturuldu.")
            self.top.destroy()

        except Exception as e:
            messagebox.showerror("Hata", f"Üretim emri oluşturulurken bir hata oluştu: {str(e)}")

    def process_production(self):
        """Üretimi gerçekleştirir."""
        if not self.production_order:
            messagebox.showwarning("Uyarı", "İşlenecek üretim emri bulunamadı.")
            return

        # Üretim durumunu kontrol et
        if self.production_order.status != "PENDING":
            messagebox.showinfo("Bilgi", "Bu üretim emri zaten tamamlanmış.")
            return

        # Kullanıcı onayı
        if not messagebox.askyesno("Onay",
                                   f"{self.production_order.quantity} adet {self.production_order.product_name} üretimini gerçekleştirmek istiyor musunuz?"):
            return

        try:
            # Üretimi gerçekleştir
            self.production_order.process(self.db)

            messagebox.showinfo("Bilgi", "Üretim başarıyla gerçekleştirildi.")
            self.top.destroy()

        except Exception as e:
            messagebox.showerror("Hata", f"Üretim gerçekleştirilirken bir hata oluştu: {str(e)}")