import customtkinter as ctk
from tkinter import messagebox
import requests
import random
import string

class AdminPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Unick Scanner - Admin Panel")
        self.geometry("450x350")
        
        # এখানে আপনার Railway লিংকের /api অংশটুকু বসান
        self.api_url = "https://unick-scan-production.up.railway.app/api"

        ctk.CTkLabel(self, text="Admin Control Panel", font=("Arial", 20, "bold")).pack(pady=20)

        self.entry_machine_id = ctk.CTkEntry(self, placeholder_text="Enter Client's Machine ID", width=350)
        self.entry_machine_id.pack(pady=10)

        self.btn_generate = ctk.CTkButton(self, text="Generate License Key", command=self.generate_key)
        self.btn_generate.pack(pady=20)

        self.lbl_result = ctk.CTkEntry(self, width=350, justify="center")
        self.lbl_result.pack(pady=10)
        self.lbl_result.configure(state="disabled")

    def generate_key(self):
        machine_id = self.entry_machine_id.get().strip()
        if not machine_id:
            messagebox.showwarning("Warning", "Machine ID is required!")
            return

        # 랜덤 কি তৈরি করা (যেমন: UNICK-A1B2-C3D4-E5F6)
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        new_key = f"UNICK-{random_str[:4]}-{random_str[4:8]}-{random_str[8:]}"

        try:
            response = requests.post(f"{self.api_url}/admin/generate", json={"machine_id": machine_id, "new_key": new_key})
            if response.status_code == 200 and response.json().get("success"):
                self.lbl_result.configure(state="normal")
                self.lbl_result.delete(0, 'end')
                self.lbl_result.insert(0, new_key)
                self.lbl_result.configure(state="disabled")
                messagebox.showinfo("Success", "License Key Generated & Saved to Database!")
            else:
                messagebox.showerror("Error", "Failed to save key. Make sure the Machine ID exists in DB.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()