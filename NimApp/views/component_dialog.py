import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.product import Product


class ComponentDialog:
    def __init__(self, parent, db, product):
        self.parent = parent
        self.db = db
        self.product = product

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        self.top.title(f"'{product.name}' için Ürün Bileşenleri")
        self.top.geometry("700x500")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Sol tarafta bileşen listesi
        left_frame = ctk.CTkFrame(self.top)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Mevcut Bileşenler").pack(pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(left_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("id", "component_id", "name", "quantity")
        self.component_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.component_tree.heading("id", text="ID")
        self.component_tree.heading("component_id", text="Bileşen ID")
        self.component_tree.heading("name", text="Bileşen Adı")
        self.component_tree.heading("quantity", text="Miktar")

        # Sütun genişlikleri
        self.component_tree.column("id", width=50)
        self.component_tree.column("component_id", width=80)
        self.component_tree.column("name", width=200)
        self.component_tree.column("quantity", width=100)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.component_tree.yview)
        self.component_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.component_tree.pack(fill="both", expand=True)

        # Butonlar
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", pady=5)

        ctk.CTkButton(button_frame, text="Sil", command=self.delete_component).pack(side="left", padx=5)

        # Sağ tarafta form
        right_frame = ctk.CTkFrame(self.top)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="Bileşen Ekle").pack(pady=5)

        form_frame = ctk.CTkFrame(right_frame)
        form_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Bileşen seçimi
        ctk.CTkLabel(form_frame, text="Bileşen:").pack(anchor="w", padx=5, pady=5)

        # Hammadde olan ürünleri çek
        self.raw_materials = [p for p in Product.get_all(self.db) if p.is_raw_material and p.id != self.product.id]
        raw_material_names = [p.name for p in self.raw_materials]

        self.component_var = ctk.StringVar()
        self.component_combobox = ctk.CTkComboBox(form_frame, values=raw_material_names, variable=self.component_var,
                                                  width=250)
        self.component_combobox.pack(anchor="w", padx=5, pady=5)

        # Miktar
        ctk.CTkLabel(form_frame, text="Miktar:").pack(anchor="w", padx=5, pady=5)
        self.quantity_entry = ctk.CTkEntry(form_frame, width=250)
        self.quantity_entry.pack(anchor="w", padx=5, pady=5)

        # Ekle butonu
        ctk.CTkButton(form_frame, text="Ekle", command=self.add_component).pack(anchor="w", padx=5, pady=10)

        # Bileşenleri yükle
        self.load_components()

    def load_components(self):
        """Ürün bileşenlerini yükler ve tabloya ekler."""
        # Tabloyu temizle
        for item in self.component_tree.get_children():
            self.component_tree.delete(item)

        # Bileşenleri çek
        components = self.product.get_components(self.db)

        # Tabloya ekle
        for component in components:
            self.component_tree.insert("", "end", values=(
                component['id'],
                component['component_id'],
                component['name'],
                component['quantity']
            ))

    def add_component(self):
        """Ürüne bileşen ekler."""
        # Bileşen seçimi kontrolü
        component_index = self.component_combobox._values.index(
            self.component_var.get()) if self.component_var.get() else -1
        if component_index == -1:
            messagebox.showwarning("Uyarı", "Lütfen bir bileşen seçin.")
            return

        component = self.raw_materials[component_index]

        # Miktar kontrolü
        try:
            quantity = float(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Miktar pozitif olmalıdır.")
        except ValueError as e:
            messagebox.showwarning("Uyarı", f"Geçersiz miktar: {str(e)}")
            return

        # Aynı bileşen zaten eklenmiş mi kontrol et
        for item in self.component_tree.get_children():
            values = self.component_tree.item(item, 'values')
            if int(values[1]) == component.id:
                messagebox.showwarning("Uyarı", "Bu bileşen zaten eklenmiş.")
                return

        # Bileşeni ekle
        self.product.add_component(self.db, component.id, quantity)

        # Listeyi yenile
        self.load_components()

        # Formu temizle
        self.component_combobox.set("")
        self.quantity_entry.delete(0, "end")

    def delete_component(self):
        """Seçili bileşeni siler."""
        selected_item = self.component_tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen bir bileşen seçin.")
            return

        # Seçilen bileşenin ID'sini al
        component_id = self.component_tree.item(selected_item[0], 'values')[1]

        if messagebox.askyesno("Onay", "Bu bileşeni silmek istediğinize emin misiniz?"):
            self.product.remove_component(self.db, component_id)
            self.load_components()