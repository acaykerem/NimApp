import customtkinter as ctk
from tkinter import messagebox
import os
import sys

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.supplier import Supplier


class SupplierDialog:
    def __init__(self, parent, db, supplier=None):
        self.parent = parent
        self.db = db
        self.supplier = supplier

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        self.top.title("Tedarikçi Ekle/Düzenle")
        self.top.geometry("500x400")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Form çerçevesi
        form_frame = ctk.CTkFrame(self.top)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form başlığı
        title = "Tedarikçi Düzenle" if supplier else "Yeni Tedarikçi Ekle"
        ctk.CTkLabel(form_frame, text=title, font=("Arial", 16)).pack(pady=10)

        # Form alanları
        ctk.CTkLabel(form_frame, text="Tedarikçi Adı:").pack(anchor="w", padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(form_frame, width=300)
        self.name_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Telefon:").pack(anchor="w", padx=5, pady=5)
        self.phone_entry = ctk.CTkEntry(form_frame, width=300)
        self.phone_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="E-posta:").pack(anchor="w", padx=5, pady=5)
        self.email_entry = ctk.CTkEntry(form_frame, width=300)
        self.email_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Adres:").pack(anchor="w", padx=5, pady=5)
        self.address_entry = ctk.CTkTextbox(form_frame, width=300, height=100)
        self.address_entry.pack(anchor="w", padx=5, pady=5)

        # Buton çerçevesi
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="İptal", command=self.top.destroy).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Kaydet", command=self.save_supplier).pack(side="left", padx=10)

        # Eğer tedarikçi düzenleme ise formu doldur
        if self.supplier:
            self.fill_form()

    def fill_form(self):
        """Tedarikçi bilgileriyle formu doldurur."""
        self.name_entry.insert(0, self.supplier.name)
        self.phone_entry.insert(0, self.supplier.phone if self.supplier.phone else "")
        self.email_entry.insert(0, self.supplier.email if self.supplier.email else "")
        self.address_entry.insert("1.0", self.supplier.address if self.supplier.address else "")

    def save_supplier(self):
        """Tedarikçiyi kaydeder."""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get("1.0", "end-1c").strip()

        # Zorunlu alan kontrolü
        if not name:
            messagebox.showwarning("Uyarı", "Tedarikçi adı boş olamaz.")
            return

        # Tedarikçi objesini oluştur veya güncelle
        if self.supplier:
            self.supplier.name = name
            self.supplier.phone = phone
            self.supplier.email = email
            self.supplier.address = address
        else:
            self.supplier = Supplier(None, name, phone, email, address)

        # Kaydet
        self.supplier.save(self.db)
        messagebox.showinfo("Bilgi", "Tedarikçi başarıyla kaydedildi.")
        self.top.destroy()