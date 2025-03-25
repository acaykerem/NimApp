import customtkinter as ctk
from tkinter import messagebox
import os
import sys

# Modelleri import et
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.customer import Customer


class CustomerDialog:
    def __init__(self, parent, db, customer=None):
        self.parent = parent
        self.db = db
        self.customer = customer

        # Dialog penceresini oluştur
        self.top = ctk.CTkToplevel(parent)
        title = "Müşteri Düzenle" if customer else "Yeni Müşteri Ekle"
        self.top.title(title)
        self.top.geometry("500x400")
        self.top.transient(parent)  # Ana pencereye bağlı
        self.top.grab_set()  # Odağı yakala

        # Form çerçevesi
        form_frame = ctk.CTkFrame(self.top)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form başlığı
        ctk.CTkLabel(form_frame, text=title, font=("Arial", 16)).pack(pady=10)

        # Form alanları
        ctk.CTkLabel(form_frame, text="Müşteri Adı:").pack(anchor="w", padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(form_frame, width=300)
        self.name_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Telefon:").pack(anchor="w", padx=5, pady=5)
        self.phone_entry = ctk.CTkEntry(form_frame, width=300)
        self.phone_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="E-posta:").pack(anchor="w", padx=5, pady=5)
        self.email_entry = ctk.CTkEntry(form_frame, width=300)
        self.email_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Adres:").pack(anchor="w", padx=5, pady=5)
        self.address_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.address_entry.pack(anchor="w", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Notlar:").pack(anchor="w", padx=5, pady=5)
        self.notes_entry = ctk.CTkTextbox(form_frame, width=300, height=80)
        self.notes_entry.pack(anchor="w", padx=5, pady=5)

        # Buton çerçevesi
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="İptal", command=self.top.destroy).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Kaydet", command=self.save_customer).pack(side="left", padx=10)

        # Eğer müşteri düzenleme ise formu doldur
        if self.customer:
            self.fill_form()

    def fill_form(self):
        """Müşteri bilgileriyle formu doldurur."""
        self.name_entry.insert(0, self.customer.name)
        self.phone_entry.insert(0, self.customer.phone if self.customer.phone else "")
        self.email_entry.insert(0, self.customer.email if self.customer.email else "")
        self.address_entry.insert("1.0", self.customer.address if self.customer.address else "")
        self.notes_entry.insert("1.0", self.customer.notes if self.customer.notes else "")

    def save_customer(self):
        """Müşteriyi kaydeder."""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get("1.0", "end-1c").strip()
        notes = self.notes_entry.get("1.0", "end-1c").strip()

        # Zorunlu alan kontrolü
        if not name:
            messagebox.showwarning("Uyarı", "Müşteri adı boş olamaz.")
            return

        # Müşteri objesini oluştur veya güncelle
        if self.customer:
            self.customer.name = name
            self.customer.phone = phone
            self.customer.email = email
            self.customer.address = address
            self.customer.notes = notes
        else:
            self.customer = Customer(None, name, phone, email, address, notes)

        # Kaydet
        self.customer.save(self.db)
        messagebox.showinfo("Bilgi", "Müşteri başarıyla kaydedildi.")
        self.top.destroy()