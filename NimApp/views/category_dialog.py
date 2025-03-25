import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.category import Category


class CategoryDialog:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Kategori Yönetimi")
        self.top.geometry("600x500")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Sol tarafta kategori listesi
        left_frame = ctk.CTkFrame(self.top)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(left_frame, text="Kategoriler").pack(pady=5)

        # Treeview çerçevesi
        tree_frame = ctk.CTkFrame(left_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Treeview oluştur
        columns = ("id", "name", "description")
        self.category_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Sütun başlıkları
        self.category_tree.heading("id", text="ID")
        self.category_tree.heading("name", text="Kategori Adı")
        self.category_tree.heading("description", text="Açıklama")

        # Sütun genişlikleri
        self.category_tree.column("id", width=50)
        self.category_tree.column("name", width=150)
        self.category_tree.column("description", width=250)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.category_tree.pack(fill="both", expand=True)

        # Butonlar
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", pady=5)

        ctk.CTkButton(button_frame, text="Yeni", command=self.clear_form).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Düzenle", command=self.edit_selected).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Sil", command=self.delete_selected).pack(side="left", padx=5)

        # Sağ tarafta form
        right_frame = ctk.CTkFrame(self.top)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(right_frame, text="Kategori Bilgileri").pack(pady=5)

        form_frame = ctk.CTkFrame(right_frame)
        form_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Form alanları
        ctk.CTkLabel(form_frame, text="Kategori Adı:").pack(anchor="w", padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(form_frame, width=250)
        self.name_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Açıklama:").pack(anchor="w", padx=5, pady=5)
        self.description_entry = ctk.CTkTextbox(form_frame, width=250, height=100)
        self.description_entry.pack(anchor="w", padx=5, pady=5)

        self.id_var = None  # Seçilen kategori ID'si

        # Kaydet butonu
        ctk.CTkButton(form_frame, text="Kaydet", command=self.save_category).pack(anchor="w", padx=5, pady=10)

        # Kategorileri yükle
        self.load_categories()

        # Seçim değiştiğinde event
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)

    def load_categories(self):
        """Kategorileri yükler ve tabloya ekler."""
        # Tabloyu temizle
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        # Kategorileri çek
        categories = Category.get_all(self.db)

        # Tabloya ekle
        for category in categories:
            self.category_tree.insert("", "end", values=(
                category.id,
                category.name,
                category.description
            ))

    def clear_form(self):
        """Form alanlarını temizler."""
        self.id_var = None
        self.name_entry.delete(0, "end")
        self.description_entry.delete("1.0", "end")

    def edit_selected(self):
        """Seçili kategoriyi düzenlemek için formu doldurur."""
        selected_item = self.category_tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen bir kategori seçin.")
            return

        # Seçilen kategorinin ID'sini al
        category_id = self.category_tree.item(selected_item[0], 'values')[0]
        category = Category.get_by_id(self.db, category_id)

        if category:
            self.id_var = category.id
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, category.name)

            self.description_entry.delete("1.0", "end")
            self.description_entry.insert("1.0", category.description if category.description else "")

    def on_category_select(self, event):
        """Kategori seçildiğinde formu doldurur."""
        self.edit_selected()

    def save_category(self):
        """Kategoriyi kaydeder."""
        name = self.name_entry.get().strip()
        description = self.description_entry.get("1.0", "end-1c").strip()

        if not name:
            messagebox.showwarning("Uyarı", "Kategori adı boş olamaz.")
            return

        category = Category(self.id_var, name, description)
        category.save(self.db)

        self.load_categories()
        self.clear_form()
        messagebox.showinfo("Bilgi", "Kategori kaydedildi.")

    def delete_selected(self):
        """Seçili kategoriyi siler."""
        selected_item = self.category_tree.selection()
        if not selected_item:
            messagebox.showwarning("Uyarı", "Lütfen bir kategori seçin.")
            return

        # Seçilen kategorinin ID'sini al
        category_id = self.category_tree.item(selected_item[0], 'values')[0]

        if messagebox.askyesno("Onay", "Bu kategoriyi silmek istediğinize emin misiniz?"):
            category = Category.get_by_id(self.db, category_id)
            if category:
                # Önce kategoriye bağlı ürünleri kontrol et
                self.db.cursor.execute("SELECT COUNT(*) FROM products WHERE category_id = ?", (category_id,))
                count = self.db.cursor.fetchone()[0]

                if count > 0:
                    if not messagebox.askyesno("Uyarı",
                                               f"Bu kategoriye bağlı {count} ürün bulunmaktadır. Silmek istediğinize emin misiniz?"):
                        return

                category.delete(self.db)
                self.load_categories()
                self.clear_form()
                messagebox.showinfo("Bilgi", "Kategori silindi.")