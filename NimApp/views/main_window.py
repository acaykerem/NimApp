import customtkinter as ctk
from tkinter import ttk, messagebox, Menu, filedialog
import os
import sys
import shutil  # Dosya kopyalama için
from datetime import datetime

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.category import Category
from models.product import Product
from models.supplier import Supplier
from models.sales_channel import SalesChannel

from views.category_dialog import CategoryDialog
from views.product_dialog import ProductDialog
from views.supplier_dialog import SupplierDialog
from views.stock_dialog import StockDialog
from views.component_dialog import ComponentDialog
from views.production_dialog import ProductionDialog  # Üretim dialog penceresini ekledik


class MainWindow:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

        # Menü ekleme
        self.create_menu()

        # Ana çerçeve
        self.main_frame = ctk.CTkFrame(parent)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Ana düzen: Sol menü + Sağ içerik
        self.left_frame = ctk.CTkFrame(self.main_frame, width=200)
        self.left_frame.pack(side="left", fill="y", padx=5, pady=5)
        self.left_frame.pack_propagate(False)  # Genişliği sabit tut

        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Sol menü butonlarını oluştur
        self.create_menu_buttons()

        # Varsayılan içerik olarak ürünler sayfasını göster
        self.show_products_page()

    def create_menu(self):
        """Ana menüyü oluşturur."""
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        # Dosya menüsü
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)

        # Veritabanı işlemleri
        file_menu.add_command(label="Veritabanını Yedekle", command=self.backup_database)
        file_menu.add_command(label="Veritabanını Geri Yükle", command=self.restore_database)
        file_menu.add_separator()

        # İçe/Dışa Aktarma Menüsü
        export_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Dışa Aktar (Excel)", menu=export_menu)
        export_menu.add_command(label="Ürünleri Dışa Aktar", command=lambda: self.export_to_excel("products"))
        export_menu.add_command(label="Kategorileri Dışa Aktar", command=lambda: self.export_to_excel("categories"))
        export_menu.add_command(label="Tedarikçileri Dışa Aktar", command=lambda: self.export_to_excel("suppliers"))
        export_menu.add_command(label="Stok Hareketlerini Dışa Aktar",
                                command=lambda: self.export_to_excel("stock_movements"))

        import_menu = Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="İçe Aktar (Excel)", menu=import_menu)
        import_menu.add_command(label="Ürünleri İçe Aktar", command=lambda: self.import_from_excel("products"))
        import_menu.add_command(label="Kategorileri İçe Aktar", command=lambda: self.import_from_excel("categories"))
        import_menu.add_command(label="Tedarikçileri İçe Aktar", command=lambda: self.import_from_excel("suppliers"))

        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.exit_app)

    def create_menu_buttons(self):
        """Sol menü butonlarını oluşturur."""
        # Menü başlığı
        ctk.CTkLabel(self.left_frame, text="ANA MENÜ", font=("Arial", 16, "bold")).pack(pady=10)

        # Menü butonları
        button_width = 180
        button_height = 40
        button_pady = 5

        self.products_btn = ctk.CTkButton(self.left_frame, text="ÜRÜNLER", width=button_width, height=button_height,
                                          command=self.show_products_page)
        self.products_btn.pack(pady=button_pady)

        self.suppliers_btn = ctk.CTkButton(self.left_frame, text="TEDARİKÇİLER", width=button_width,
                                           height=button_height,
                                           command=self.show_suppliers_page)
        self.suppliers_btn.pack(pady=button_pady)

        self.stocks_btn = ctk.CTkButton(self.left_frame, text="STOKLAR", width=button_width, height=button_height,
                                        command=self.show_stocks_page)
        self.stocks_btn.pack(pady=button_pady)

        self.production_btn = ctk.CTkButton(self.left_frame, text="ÜRETİM", width=button_width, height=button_height,
                                            command=self.show_production_page)
        self.production_btn.pack(pady=button_pady)

        self.sales_channels_btn = ctk.CTkButton(self.left_frame, text="SATIŞ KANALLARI", width=button_width,
                                                height=button_height,
                                                command=self.show_sales_channels_page)
        self.sales_channels_btn.pack(pady=button_pady)

        self.reports_btn = ctk.CTkButton(self.left_frame, text="RAPORLAR", width=button_width, height=button_height,
                                         command=self.show_reports_page)
        self.reports_btn.pack(pady=button_pady)



    def clear_right_frame(self):
        """Sağ taraftaki içeriği temizler."""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

    def show_products_page(self):
        """Ürünler sayfasını gösterir."""
        self.clear_right_frame()

        # Üst butonlar çerçevesi
        top_frame = ctk.CTkFrame(self.right_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Üst butonlar
        ctk.CTkButton(top_frame, text="YENİ ÜRÜN EKLE", command=self.open_product_dialog).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="KATEGORİ YÖNETİMİ", command=self.open_category_dialog).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="ÜRÜN BİLEŞENLERİ", command=self.open_component_dialog).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="YENİLE", command=self.load_products).pack(side="left", padx=5)

        # İçerik çerçevesi
        content_frame = ctk.CTkFrame(self.right_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(content_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("id", "category", "name", "stock", "threshold", "barcode", "is_raw")
        self.product_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("category", text="Kategori")
        self.product_tree.heading("name", text="Ürün Adı")
        self.product_tree.heading("stock", text="Stok Miktarı")
        self.product_tree.heading("threshold", text="Stok Eşiği")
        self.product_tree.heading("barcode", text="Barkod")
        self.product_tree.heading("is_raw", text="Hammadde")

        # Sütun genişlikleri
        self.product_tree.column("id", width=50)
        self.product_tree.column("category", width=100)
        self.product_tree.column("name", width=200)
        self.product_tree.column("stock", width=100)
        self.product_tree.column("threshold", width=100)
        self.product_tree.column("barcode", width=100)
        self.product_tree.column("is_raw", width=100)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.product_tree.pack(fill="both", expand=True)

        # Çift tıklama olayını bağla
        self.product_tree.bind("<Double-1>", self.on_product_double_click)

        # Verileri yükle
        self.load_products()

    def show_suppliers_page(self):
        """Tedarikçiler sayfasını gösterir."""
        self.clear_right_frame()

        # Üst butonlar çerçevesi
        top_frame = ctk.CTkFrame(self.right_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Üst butonlar
        ctk.CTkButton(top_frame, text="YENİ TEDARİKÇİ", command=self.open_supplier_dialog).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="YENİLE", command=self.load_suppliers).pack(side="left", padx=5)

        # İçerik çerçevesi
        content_frame = ctk.CTkFrame(self.right_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(content_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("id", "name", "phone", "email", "address")
        self.supplier_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.supplier_tree.heading("id", text="ID")
        self.supplier_tree.heading("name", text="Tedarikçi Adı")
        self.supplier_tree.heading("phone", text="Telefon")
        self.supplier_tree.heading("email", text="E-posta")
        self.supplier_tree.heading("address", text="Adres")

        # Sütun genişlikleri
        self.supplier_tree.column("id", width=50)
        self.supplier_tree.column("name", width=200)
        self.supplier_tree.column("phone", width=150)
        self.supplier_tree.column("email", width=200)
        self.supplier_tree.column("address", width=300)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.supplier_tree.yview)
        self.supplier_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.supplier_tree.pack(fill="both", expand=True)

        # Çift tıklama olayını bağla
        self.supplier_tree.bind("<Double-1>", self.on_supplier_double_click)

        # Verileri yükle
        self.load_suppliers()

    def show_stocks_page(self):
        """Stok hareketleri sayfasını gösterir."""
        self.clear_right_frame()

        # Üst butonlar çerçevesi
        top_frame = ctk.CTkFrame(self.right_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Üst butonlar
        ctk.CTkButton(top_frame, text="STOK GİRİŞİ",
                      command=lambda: self.open_stock_dialog("IN")).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="STOK ÇIKIŞI",
                      command=lambda: self.open_stock_dialog("OUT")).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="YENİLE",
                      command=self.load_stock_movements).pack(side="left", padx=5)

        # İçerik çerçevesi
        content_frame = ctk.CTkFrame(self.right_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(content_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("id", "date", "product", "quantity", "type", "supplier", "expiry")
        self.stock_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.stock_tree.heading("id", text="ID")
        self.stock_tree.heading("date", text="Tarih")
        self.stock_tree.heading("product", text="Ürün")
        self.stock_tree.heading("quantity", text="Miktar")
        self.stock_tree.heading("type", text="İşlem Tipi")
        self.stock_tree.heading("supplier", text="Tedarikçi/Kanal")
        self.stock_tree.heading("expiry", text="S.K.T.")

        # Sütun genişlikleri
        self.stock_tree.column("id", width=50)
        self.stock_tree.column("date", width=150)
        self.stock_tree.column("product", width=200)
        self.stock_tree.column("quantity", width=100)
        self.stock_tree.column("type", width=100)
        self.stock_tree.column("supplier", width=150)
        self.stock_tree.column("expiry", width=150)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.stock_tree.pack(fill="both", expand=True)

        # Verileri yükle
        self.load_stock_movements()

    def show_production_page(self):
        """Üretim sayfasını gösterir."""
        self.clear_right_frame()

        # Üst butonlar çerçevesi
        top_frame = ctk.CTkFrame(self.right_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Üst butonlar
        ctk.CTkButton(top_frame, text="YENİ ÜRETİM EMRİ",
                      command=self.open_production_dialog).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="YENİLE",
                      command=self.load_production_orders).pack(side="left", padx=5)

        # İçerik çerçevesi
        content_frame = ctk.CTkFrame(self.right_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(content_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("id", "date", "product", "quantity", "status")
        self.production_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.production_tree.heading("id", text="ID")
        self.production_tree.heading("date", text="Tarih")
        self.production_tree.heading("product", text="Üretilecek Ürün")
        self.production_tree.heading("quantity", text="Miktar")
        self.production_tree.heading("status", text="Durum")

        # Sütun genişlikleri
        self.production_tree.column("id", width=50)
        self.production_tree.column("date", width=150)
        self.production_tree.column("product", width=200)
        self.production_tree.column("quantity", width=100)
        self.production_tree.column("status", width=100)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.production_tree.yview)
        self.production_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.production_tree.pack(fill="both", expand=True)

        # Çift tıklama olayını bağla
        self.production_tree.bind("<Double-1>", self.on_production_double_click)

        # Verileri yükle
        self.load_production_orders()

    def show_sales_channels_page(self):
        """Satış Kanalları sayfasını gösterir."""
        self.clear_right_frame()

        # Üst butonlar çerçevesi
        top_frame = ctk.CTkFrame(self.right_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Üst butonlar
        ctk.CTkButton(top_frame, text="YENİ SATIŞ KANALI",
                      command=self.open_sales_channel_dialog).pack(side="left", padx=5)
        ctk.CTkButton(top_frame, text="YENİLE",
                      command=self.load_sales_channels).pack(side="left", padx=5)

        # İçerik çerçevesi
        content_frame = ctk.CTkFrame(self.right_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(content_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("id", "name", "description")
        self.sales_channel_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.sales_channel_tree.heading("id", text="ID")
        self.sales_channel_tree.heading("name", text="Kanal Adı")
        self.sales_channel_tree.heading("description", text="Açıklama")

        # Sütun genişlikleri
        self.sales_channel_tree.column("id", width=50)
        self.sales_channel_tree.column("name", width=200)
        self.sales_channel_tree.column("description", width=300)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.sales_channel_tree.yview)
        self.sales_channel_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.sales_channel_tree.pack(fill="both", expand=True)

        # Verileri yükle
        self.load_sales_channels()

    def show_reports_page(self):
        """Raporlar sayfasını gösterir."""
        self.clear_right_frame()

        # Rapor seçenekleri çerçevesi
        options_frame = ctk.CTkFrame(self.right_frame)
        options_frame.pack(fill="x", padx=5, pady=5)

        # Rapor seçimi
        ctk.CTkLabel(options_frame, text="Rapor Türü:").pack(side="left", padx=5)

        self.report_type = ctk.StringVar(value="Stok Durumu")
        report_options = [
            "Stok Durumu",
            "Azalan Ürünler",
            "Son Kullanma Tarihi Yaklaşan"
        ]

        report_combobox = ctk.CTkComboBox(
            options_frame,
            values=report_options,
            variable=self.report_type,
            command=self.on_report_type_change
        )
        report_combobox.pack(side="left", padx=5)

        # Rapor oluştur butonu
        ctk.CTkButton(options_frame, text="Raporu Oluştur",
                      command=self.generate_report).pack(side="left", padx=5)

        # Dışa aktar butonu
        ctk.CTkButton(options_frame, text="Excel'e Aktar",
                      command=self.export_report).pack(side="left", padx=5)

        # Sonuç çerçevesi
        report_frame = ctk.CTkFrame(self.right_frame)
        report_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview için çerçeve
        tree_frame = ctk.CTkFrame(report_frame)
        tree_frame.pack(fill="both", expand=True)

        # Treeview oluştur - başlangıçta sütunlar yok, dinamik olarak eklenecek
        self.report_tree = ttk.Treeview(tree_frame)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.report_tree.pack(fill="both", expand=True)

    def show_file_options(self):
        """Dosya işlemleri için bir popup pencere gösterir."""
        popup = ctk.CTkToplevel(self.parent)
        popup.title("Dosya İşlemleri")
        popup.geometry("300x200")
        popup.transient(self.parent)  # Ana pencereye bağlı
        popup.grab_set()  # Odağı yakala

        # İçerik çerçevesi
        content_frame = ctk.CTkFrame(popup)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Butonlar
        ctk.CTkButton(content_frame, text="Veritabanını Yedekle",
                      command=lambda: [popup.destroy(), self.backup_database()]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Veritabanını Geri Yükle",
                      command=lambda: [popup.destroy(), self.restore_database()]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Veri Dışa Aktar",
                      command=lambda: [popup.destroy(), self.show_export_options()]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Veri İçe Aktar",
                      command=lambda: [popup.destroy(), self.show_import_options()]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Kapat",
                      command=popup.destroy).pack(pady=5, fill="x")

    def show_export_options(self):
        """Dışa aktarma seçeneklerini gösterir."""
        popup = ctk.CTkToplevel(self.parent)
        popup.title("Veri Dışa Aktar")
        popup.geometry("300x200")
        popup.transient(self.parent)
        popup.grab_set()

        content_frame = ctk.CTkFrame(popup)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkButton(content_frame, text="Ürünleri Dışa Aktar",
                      command=lambda: [popup.destroy(), self.export_to_excel("products")]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Kategorileri Dışa Aktar",
                      command=lambda: [popup.destroy(), self.export_to_excel("categories")]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Tedarikçileri Dışa Aktar",
                      command=lambda: [popup.destroy(), self.export_to_excel("suppliers")]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Stok Hareketlerini Dışa Aktar",
                      command=lambda: [popup.destroy(), self.export_to_excel("stock_movements")]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Kapat",
                      command=popup.destroy).pack(pady=5, fill="x")

    def show_import_options(self):
        """İçe aktarma seçeneklerini gösterir."""
        popup = ctk.CTkToplevel(self.parent)
        popup.title("Veri İçe Aktar")
        popup.geometry("300x150")
        popup.transient(self.parent)
        popup.grab_set()

        content_frame = ctk.CTkFrame(popup)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkButton(content_frame, text="Ürünleri İçe Aktar",
                      command=lambda: [popup.destroy(), self.import_from_excel("products")]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Kategorileri İçe Aktar",
                      command=lambda: [popup.destroy(), self.import_from_excel("categories")]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Tedarikçileri İçe Aktar",
                      command=lambda: [popup.destroy(), self.import_from_excel("suppliers")]).pack(pady=5, fill="x")
        ctk.CTkButton(content_frame, text="Kapat",
                      command=popup.destroy).pack(pady=5, fill="x")

    # Diğer metodlar (load_data, load_products, load_suppliers, vb.) burada devam edecek...
    # ...

    def open_production_dialog(self):
        """Üretim emri oluşturma penceresini açar."""
        dialog = ProductionDialog(self.parent, self.db)
        self.parent.wait_window(dialog.top)
        self.load_production_orders()
        self.load_products()  # Üretim ürün stoklarını etkileyecek

    def load_production_orders(self):
        """Üretim emirlerini yükler ve tabloya ekler."""
        # Tabloyu temizle
        for item in self.production_tree.get_children():
            self.production_tree.delete(item)

        # Üretim emirlerini çek
        self.db.cursor.execute("""
        SELECT po.id, po.date, p.name, po.quantity, po.status
        FROM production_orders po
        JOIN products p ON po.product_id = p.id
        ORDER BY po.date DESC
        """)

        orders = self.db.cursor.fetchall()

        # Tabloya ekle
        for order in orders:
            status_text = "Bekliyor" if order['status'] == "PENDING" else "Tamamlandı"
            self.production_tree.insert("", "end", values=(
                order['id'],
                order['date'],
                order['name'],
                order['quantity'],
                status_text
            ))

    def on_production_double_click(self, event):
        """Üretim emrine çift tıklandığında düzenleme penceresini açar."""
        selected_item = self.production_tree.selection()
        if selected_item:
            production_id = self.production_tree.item(selected_item[0], 'values')[0]

            # Bekleyen üretim emrini açma
            self.db.cursor.execute("SELECT status FROM production_orders WHERE id = ?", (production_id,))
            result = self.db.cursor.fetchone()

            if result and result['status'] == "PENDING":
                dialog = ProductionDialog(self.parent, self.db, production_id)
                self.parent.wait_window(dialog.top)
                self.load_production_orders()
                self.load_products()
            else:
                messagebox.showinfo("Bilgi", "Tamamlanan üretim emirleri düzenlenemez.")

    def open_sales_channel_dialog(self):
        """Satış kanalı ekleme/düzenleme penceresini açar."""
        # Bu işlevsellik henüz mevcut değil, ileriki geliştirme için yer tutucu
        messagebox.showinfo("Bilgi", "Bu özellik henüz uygulanmadı.")

    def load_sales_channels(self):
        """Satış kanallarını yükler ve tabloya ekler."""
        # Tabloyu temizle
        for item in self.sales_channel_tree.get_children():
            self.sales_channel_tree.delete(item)

        # Satış kanallarını çek
        self.db.cursor.execute("SELECT id, name, description FROM sales_channels")
        channels = self.db.cursor.fetchall()

        # Tabloya ekle
        for channel in channels:
            self.sales_channel_tree.insert("", "end", values=(
                channel['id'],
                channel['name'],
                channel['description']
            ))

    def load_data(self):
        """Tüm verileri yükler."""
        self.load_products()
        self.load_suppliers()
        self.load_stock_movements()
        self.load_production_orders()
        self.load_sales_channels()

    def load_products(self):
        """Ürünleri yükler ve tabloya ekler."""
        # Tabloyu temizle
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        # Ürünleri çek
        products = Product.get_all(self.db)

        # Tabloya ekle
        for product in products:
            is_raw = "Evet" if product.is_raw_material else "Hayır"
            self.product_tree.insert("", "end", values=(
                product.id,
                product.category_name,
                product.name,
                product.stock_quantity,
                product.stock_threshold,
                product.barcode,
                is_raw
            ))

    def load_suppliers(self):
        """Tedarikçileri yükler ve tabloya ekler."""
        # Tabloyu temizle
        for item in self.supplier_tree.get_children():
            self.supplier_tree.delete(item)

        # Tedarikçileri çek
        suppliers = Supplier.get_all(self.db)

        # Tabloya ekle
        for supplier in suppliers:
            self.supplier_tree.insert("", "end", values=(
                supplier.id,
                supplier.name,
                supplier.phone,
                supplier.email,
                supplier.address
            ))

    def load_stock_movements(self):
        """Stok hareketlerini yükler ve tabloya ekler."""
        # Tabloyu temizle
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        # Stok hareketlerini çek
        self.db.cursor.execute("""
        SELECT sm.id, sm.date, p.name, sm.quantity, sm.movement_type, 
               CASE 
                   WHEN sm.movement_type = 'IN' THEN s.name 
                   WHEN sm.movement_type = 'OUT' THEN sc.name 
                   ELSE NULL 
               END as source,
               sm.expiry_date
        FROM stock_movements sm
        JOIN products p ON sm.product_id = p.id
        LEFT JOIN suppliers s ON sm.supplier_id = s.id
        LEFT JOIN sales_channels sc ON sm.sales_channel_id = sc.id
        ORDER BY sm.date DESC
        LIMIT 100
        """)

        movements = self.db.cursor.fetchall()

        # Tabloya ekle
        for movement in movements:
            movement_type = "Giriş" if movement['movement_type'] == "IN" else "Çıkış"
            self.stock_tree.insert("", "end", values=(
                movement['id'],
                movement['date'],
                movement['name'],
                movement['quantity'],
                movement_type,
                movement['source'] if movement['source'] else '',
                movement['expiry_date'] if movement['expiry_date'] else ''
            ))

    def open_product_dialog(self, product_id=None):
        """Ürün ekleme/düzenleme penceresini açar."""
        product = None
        if product_id:
            product = Product.get_by_id(self.db, product_id)

        dialog = ProductDialog(self.parent, self.db, product)
        self.parent.wait_window(dialog.top)
        self.load_products()

    def open_category_dialog(self):
        """Kategori yönetimi penceresini açar."""
        dialog = CategoryDialog(self.parent, self.db)
        self.parent.wait_window(dialog.top)
        self.load_products()  # Kategori değişimi ürünleri etkileyebilir

    def open_supplier_dialog(self, supplier_id=None):
        """Tedarikçi ekleme/düzenleme penceresini açar."""
        supplier = None
        if supplier_id:
            supplier = Supplier.get_by_id(self.db, supplier_id)

        dialog = SupplierDialog(self.parent, self.db, supplier)
        self.parent.wait_window(dialog.top)
        self.load_suppliers()

    def open_stock_dialog(self, movement_type):
        """Stok giriş/çıkış penceresini açar."""
        dialog = StockDialog(self.parent, self.db, movement_type)
        self.parent.wait_window(dialog.top)
        self.load_stock_movements()
        self.load_products()  # Stok değişimleri ürün listesini etkiler

    def open_component_dialog(self):
        """Ürün bileşenleri penceresini açar."""
        selected_item = self.product_tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen bir ürün seçin.")
            return

        # Seçilen ürünün ID'sini al
        product_id = self.product_tree.item(selected_item[0], 'values')[0]
        product = Product.get_by_id(self.db, product_id)

        dialog = ComponentDialog(self.parent, self.db, product)
        self.parent.wait_window(dialog.top)

    def on_product_double_click(self, event):
        """Ürüne çift tıklandığında düzenleme penceresini açar."""
        selected_item = self.product_tree.selection()
        if selected_item:
            product_id = self.product_tree.item(selected_item[0], 'values')[0]
            self.open_product_dialog(product_id)

    def on_supplier_double_click(self, event):
        """Tedarikçiye çift tıklandığında düzenleme penceresini açar."""
        selected_item = self.supplier_tree.selection()
        if selected_item:
            supplier_id = self.supplier_tree.item(selected_item[0], 'values')[0]
            self.open_supplier_dialog(supplier_id)

    def on_report_type_change(self, selection):
        """Rapor türü değiştiğinde yapılacak işlemler."""
        # Burada self.report_type.get() değerini kullanarak gerekli değişiklikleri yapabiliriz
        pass

    def generate_report(self):
        """Seçilen rapora göre rapor oluşturur."""
        # Önce treeview'ı temizle
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)

        # Mevcut sütunları kaldır
        for col in self.report_tree['columns']:
            self.report_tree.heading(col, text="")

        report_type = self.report_type.get()

        if report_type == "Stok Durumu":
            # Stok durumu raporu
            columns = ("id", "category", "name", "stock", "threshold")
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'

            self.report_tree.heading("id", text="ID")
            self.report_tree.heading("category", text="Kategori")
            self.report_tree.heading("name", text="Ürün Adı")
            self.report_tree.heading("stock", text="Stok Miktarı")
            self.report_tree.heading("threshold", text="Stok Eşiği")

            self.report_tree.column("id", width=50)
            self.report_tree.column("category", width=100)
            self.report_tree.column("name", width=200)
            self.report_tree.column("stock", width=100)
            self.report_tree.column("threshold", width=100)

            # Verileri çek
            products = Product.get_all(self.db)

            # Tabloya ekle
            for product in products:
                self.report_tree.insert("", "end", values=(
                    product.id,
                    product.category_name,
                    product.name,
                    product.stock_quantity,
                    product.stock_threshold
                ))

        elif report_type == "Azalan Ürünler":
            # Azalan ürünler raporu
            columns = ("id", "name", "stock", "threshold", "needed")
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'

            self.report_tree.heading("id", text="ID")
            self.report_tree.heading("name", text="Ürün Adı")
            self.report_tree.heading("stock", text="Stok Miktarı")
            self.report_tree.heading("threshold", text="Stok Eşiği")
            self.report_tree.heading("needed", text="Gereken Miktar")

            self.report_tree.column("id", width=50)
            self.report_tree.column("name", width=200)
            self.report_tree.column("stock", width=100)
            self.report_tree.column("threshold", width=100)
            self.report_tree.column("needed", width=100)

            # Verileri çek
            low_stock_products = Product.get_products_below_threshold(self.db)

            # Tabloya ekle
            for product in low_stock_products:
                needed = product['stock_threshold'] - product['stock_quantity']
                self.report_tree.insert("", "end", values=(
                    product['id'],
                    product['name'],
                    product['stock_quantity'],
                    product['stock_threshold'],
                    needed
                ))

        elif report_type == "Son Kullanma Tarihi Yaklaşan":
            # SKT yaklaşan ürünler raporu
            columns = ("id", "name", "expiry", "days_left")
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'

            self.report_tree.heading("id", text="ID")
            self.report_tree.heading("name", text="Ürün Adı")
            self.report_tree.heading("expiry", text="Son Kullanma Tarihi")
            self.report_tree.heading("days_left", text="Kalan Gün")

            self.report_tree.column("id", width=50)
            self.report_tree.column("name", width=200)
            self.report_tree.column("expiry", width=150)
            self.report_tree.column("days_left", width=100)

            # Verileri çek
            expiring_products = Product.get_expiring_products(self.db, 30)

            # Tabloya ekle
            for product in expiring_products:
                self.report_tree.insert("", "end", values=(
                    product['id'],
                    product['name'],
                    product['expiry_date'],
                    int(product['days_left'])
                ))

    def export_report(self):
        """Mevcut raporu Excel'e aktarır."""
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Hata",
                                 "Bu özellik için 'pandas' kütüphanesi gereklidir. Lütfen 'pip install pandas openpyxl' komutunu çalıştırın.")
            return

        # Rapor tablosunda veri var mı kontrol et
        if not self.report_tree.get_children():
            messagebox.showwarning("Uyarı", "Aktarılacak rapor verisi bulunamadı.")
            return

        # Dosya adını oluştur
        report_type = self.report_type.get()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"rapor_{report_type.lower().replace(' ', '_')}_{timestamp}.xlsx"

        # Dosya seçim penceresi
        filename = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title=f"{report_type} Raporunu Dışa Aktar",
            initialfile=default_filename,
            filetypes=[("Excel Dosyası", "*.xlsx"), ("Tüm Dosyalar", "*.*")]
        )

        if not filename:
            return  # Kullanıcı iptal etti

        # Dosya uzantısı kontrolü
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'

        try:
            # Treeview verilerini al
            data = []
            columns = self.report_tree['columns']

            # Sütun başlıklarını al
            headers = [self.report_tree.heading(col)['text'] for col in columns]
            data.append(headers)

            # Treeview verilerini al
            for item in self.report_tree.get_children():
                values = self.report_tree.item(item, 'values')
                data.append(values)

            # Excel'e yaz
            df = pd.DataFrame(data[1:], columns=headers)
            df.to_excel(filename, index=False)

            messagebox.showinfo("Bilgi", f"{report_type} raporu başarıyla dışa aktarıldı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dışa aktarma sırasında bir hata oluştu: {str(e)}")

    def export_to_excel(self, table_name):
        """Belirtilen tabloyu Excel'e aktarır."""
        # Pandas'ın yüklü olduğunu kontrol et
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Hata",
                                 "Bu özellik için 'pandas' kütüphanesi gereklidir. Lütfen 'pip install pandas openpyxl' komutunu çalıştırın.")
            return

        # Dosya adını oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{table_name}_{timestamp}.xlsx"

        # Dosya seçim penceresi
        filename = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title=f"{table_name.capitalize()} Tablosunu Dışa Aktar",
            initialfile=default_filename,
            filetypes=[("Excel Dosyası", "*.xlsx"), ("Tüm Dosyalar", "*.*")]
        )

        if not filename:
            return  # Kullanıcı iptal etti

        # Dosya uzantısı kontrolü
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'

        try:
            # Tablo verilerini al
            if table_name == "products":
                query = """
                SELECT p.id, c.name as category, p.name, p.description, 
                       p.stock_quantity, p.stock_threshold, p.barcode, 
                       p.is_raw_material
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                """
            elif table_name == "categories":
                query = "SELECT id, name, description FROM categories"
            elif table_name == "suppliers":
                query = "SELECT id, name, phone, email, address FROM suppliers"
            elif table_name == "stock_movements":
                query = """
                SELECT sm.id, sm.date, p.name as product, sm.quantity, sm.movement_type, 
                       CASE 
                           WHEN sm.movement_type = 'IN' THEN s.name 
                           WHEN sm.movement_type = 'OUT' THEN sc.name 
                           ELSE NULL 
                       END as source,
                       sm.production_date, sm.expiry_date, sm.batch_number, sm.description
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                LEFT JOIN suppliers s ON sm.supplier_id = s.id
                LEFT JOIN sales_channels sc ON sm.sales_channel_id = sc.id
                """
            else:
                raise ValueError(f"Bilinmeyen tablo: {table_name}")

            # Sorguyu çalıştır
            self.db.cursor.execute(query)

            # Pandas DataFrame'e çevir
            df = pd.DataFrame(self.db.cursor.fetchall())

            # Excel'e kaydet
            df.to_excel(filename, index=False)

            messagebox.showinfo("Bilgi", f"{table_name.capitalize()} tablosu başarıyla dışa aktarıldı.")
        except Exception as e:
            messagebox.showerror("Hata", f"Dışa aktarma sırasında bir hata oluştu: {str(e)}")

    def import_from_excel(self, table_name):
        """Excel'den veri içe aktarır."""
        # Pandas'ın yüklü olduğunu kontrol et
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("Hata",
                                 "Bu özellik için 'pandas' kütüphanesi gereklidir. Lütfen 'pip install pandas openpyxl' komutunu çalıştırın.")
            return

        # Dosya seçim penceresi
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title=f"{table_name.capitalize()} Tablosuna İçe Aktar",
            filetypes=[("Excel Dosyası", "*.xlsx"), ("Tüm Dosyalar", "*.*")]
        )

        if not filename:
            return  # Kullanıcı iptal etti

        try:
            # Excel dosyasını oku
            df = pd.read_excel(filename)

            # DataFrame boş mu kontrol et
            if df.empty:
                messagebox.showwarning("Uyarı", "İçe aktarılacak veri bulunamadı.")
                return

            # DataFrame sütunlarını kontrol et
            if table_name == "products":
                required_columns = ["name", "category", "stock_quantity", "stock_threshold"]
            elif table_name == "categories":
                required_columns = ["name"]
            elif table_name == "suppliers":
                required_columns = ["name"]
            else:
                raise ValueError(f"Bilinmeyen tablo: {table_name}")

            # Gerekli sütunlar var mı kontrol et
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                messagebox.showwarning("Uyarı",
                                       f"Excel dosyasında gerekli sütunlar eksik: {', '.join(missing_columns)}")
                return

            # Kullanıcı onayı
            if not messagebox.askyesno("Onay",
                                       f"{len(df)} adet kayıt içe aktarılacak. Devam etmek istiyor musunuz?"):
                return

            # Verileri içe aktar
            imported_count = 0

            if table_name == "products":
                for _, row in df.iterrows():
                    # Kategori ID'sini bul
                    category_name = row.get("category", "")
                    category_id = None

                    if category_name:
                        self.db.cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
                        category_result = self.db.cursor.fetchone()
                        if category_result:
                            category_id = category_result[0]
                        else:
                            # Kategori yoksa oluştur
                            self.db.cursor.execute(
                                "INSERT INTO categories (name) VALUES (?)", (category_name,))
                            category_id = self.db.cursor.lastrowid

                    # Ürün ekle
                    self.db.cursor.execute(
                        """INSERT INTO products 
                           (category_id, name, description, stock_quantity, stock_threshold, barcode, is_raw_material) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            category_id,
                            row.get("name", ""),
                            row.get("description", ""),
                            row.get("stock_quantity", 0),
                            row.get("stock_threshold", 5),
                            row.get("barcode", ""),
                            1 if row.get("is_raw_material", "").lower() in ["evet", "true", "1", "yes"] else 0
                        )
                    )
                    imported_count += 1

            elif table_name == "categories":
                for _, row in df.iterrows():
                    self.db.cursor.execute(
                        "INSERT INTO categories (name, description) VALUES (?, ?)",
                        (row.get("name", ""), row.get("description", ""))
                    )
                    imported_count += 1

            elif table_name == "suppliers":
                for _, row in df.iterrows():
                    self.db.cursor.execute(
                        "INSERT INTO suppliers (name, phone, email, address) VALUES (?, ?, ?, ?)",
                        (
                            row.get("name", ""),
                            row.get("phone", ""),
                            row.get("email", ""),
                            row.get("address", "")
                        )
                    )
                    imported_count += 1

            # Değişiklikleri kaydet
            self.db.connection.commit()

            # Verileri yenile
            self.load_data()

            messagebox.showinfo("Bilgi", f"{imported_count} kayıt başarıyla içe aktarıldı.")

        except Exception as e:
            messagebox.showerror("Hata", f"İçe aktarma sırasında bir hata oluştu: {str(e)}")

    def backup_database(self):
        """Veritabanını yedekler."""
        # Yedek dosya adını oluştur (tarih-saat ekleyerek)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"stok_takip_yedek_{timestamp}.db"

        # Dosya seçim penceresi
        filename = filedialog.asksaveasfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title="Veritabanını Yedekle",
            initialfile=default_filename,
            filetypes=[("SQLite Veritabanı", "*.db"), ("Tüm Dosyalar", "*.*")]
        )

        if not filename:
            return  # Kullanıcı iptal etti

        try:
            # Veritabanı bağlantısını kapat (yedekleme için gerekli)
            self.db.close()

            # Dosyayı kopyala
            shutil.copy2(self.db.db_path, filename)

            # Veritabanını yeniden aç
            self.db.connect()

            messagebox.showinfo("Bilgi", "Veritabanı başarıyla yedeklendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Yedekleme sırasında bir hata oluştu: {str(e)}")
            # Hata olsa bile veritabanını yeniden açmaya çalış
            try:
                self.db.connect()
            except:
                pass

    def restore_database(self):
        """Yedekten veritabanını geri yükler."""
        # Kullanıcı onayı
        if not messagebox.askyesno("Onay",
                                   "Bu işlem mevcut veritabanını yedekten geri yükleyecek. Devam etmek istiyor musunuz?"):
            return

        # Dosya seçim penceresi
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title="Veritabanını Geri Yükle",
            filetypes=[("SQLite Veritabanı", "*.db"), ("Tüm Dosyalar", "*.*")]
        )

        if not filename:
            return  # Kullanıcı iptal etti

        try:
            # Veritabanı bağlantısını kapat
            self.db.close()

            # Yedek dosyasını mevcut veritabanının üzerine kopyala
            shutil.copy2(filename, self.db.db_path)

            # Veritabanını yeniden aç
            self.db.connect()

            # Verileri yenile
            self.load_data()

            messagebox.showinfo("Bilgi", "Veritabanı başarıyla geri yüklendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Geri yükleme sırasında bir hata oluştu: {str(e)}")
            # Hata olsa bile veritabanını yeniden açmaya çalış
            try:
                self.db.connect()
                self.load_data()
            except:
                pass

    def exit_app(self):
        """Uygulamadan çıkış yapar."""
        if messagebox.askokcancel("Çıkış", "Uygulamadan çıkmak istediğinize emin misiniz?"):
            self.db.close()
            self.parent.destroy()