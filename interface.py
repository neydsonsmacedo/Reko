from tkinter import *
from tkinter import ttk
from encryption_service import EncryptionService


class RekoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reko - Gerenciador de Senhas")
        self.root.geometry("600x400")

        self.encryption_service = EncryptionService()

        # Main frame
        self.frm = ttk.Frame(root, padding=10)
        self.frm.grid(row=0, column=0, sticky=(N, W, E, S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.frm.columnconfigure(0, weight=1)
        self.frm.rowconfigure(0, weight=1)

        # Frame to hold service rows (with scrollbar)
        self.services_frame = ttk.Frame(self.frm)
        self.services_frame.grid(row=0, column=0, sticky=(N, W, E, S))

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.services_frame, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Canvas for scrollable area
        self.canvas = Canvas(self.services_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar.config(command=self.canvas.yview)

        # Frame inside canvas to hold service rows
        self.service_frame_inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.service_frame_inner, anchor="nw")

        # Update scroll region when frame size changes
        self.service_frame_inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Button frame at bottom
        btn_frame = ttk.Frame(self.frm)
        btn_frame.grid(row=1, column=0, pady=10, sticky=W)

        # Refresh button
        ttk.Button(btn_frame, text="Atualizar", command=self.refresh_services).grid(row=0, column=0, padx=5)

        # Service data storage
        self.service_data = {}
        self.rows = {}           # {service_name: frame}
        self.details_panels = {} # {service_name: frame}
        self.detail_visible = {} # {service_name: bool}
        self.show_password_btns = {}  # {service_name: Button}
        self.password_labels = {}      # {service_name: Label}

        # Load services initially
        self.load_services()

    def load_services(self):
        """Load services from data.json and populate the scrollable frame."""
        # Clear existing service rows
        for widget in list(self.service_frame_inner.winfo_children()):
            widget.destroy()

        self.service_data = {}
        self.rows = {}
        self.details_panels = {}
        self.detail_visible = {}
        self.show_password_btns = {}
        self.password_labels = {}

        import json
        import os

        data_file = self.encryption_service.data_file

        if os.path.exists(data_file):
            with open(data_file, 'r') as file:
                data = json.load(file)

            for service_name in data.keys():
                entry = data[service_name]
                username = entry.get('username', '')
                encrypted_password = entry.get('password', '')

                # Store data
                self.service_data[service_name] = {
                    'username': username,
                    'encrypted_password': encrypted_password
                }
                self.detail_visible[service_name] = False

                # --- Row: service name + Show button ---
                row_frame = ttk.Frame(self.service_frame_inner, relief=RAISED, borderwidth=1)
                row_frame.pack(fill=X, pady=2)
                self.rows[service_name] = row_frame

                # Service name label
                ttk.Label(row_frame, text=service_name, width=20).pack(side=LEFT, padx=5)

                # Show/Hide button - initially "Show"
                btn = ttk.Button(row_frame, text="Show", width=8,
                                 command=lambda sn=service_name: self.toggle_detail(sn))
                btn.pack(side=RIGHT, padx=5)

                # --- Detail panel: hidden by default ---
                detail_panel = ttk.Frame(self.service_frame_inner, relief=RAISED, borderwidth=1)

                # Service title as heading
                title_label = ttk.Label(detail_panel, text=f"Serviço: {service_name}",
                                        font=("Helvetica", 14, "bold"))
                title_label.pack(anchor=W, pady=5)

                # Username
                username_label = ttk.Label(detail_panel, text=f"Usuário: {username}",
                                           anchor=W)
                username_label.pack(anchor=W, fill=X)

                # Password (hidden by default)
                password_frame = ttk.Frame(detail_panel)
                password_frame.pack(anchor=W, fill=X, padx=5, pady=5)
                ttk.Label(password_frame, text="Senha: ", anchor=W).pack(side=LEFT, padx=5)
                pwd_label = ttk.Label(password_frame, text="••••••", anchor=W)
                pwd_label.pack(side=LEFT, fill=X, expand=True)
                show_btn = ttk.Button(password_frame, text="Show",
                                      command=lambda sn=service_name: self.show_password(sn))
                show_btn.pack(side=RIGHT, padx=5)

                # Hide the detail panel initially
                detail_panel.pack_forget()

                # Pack the detail panel at the end
                self.details_panels[service_name] = detail_panel
                self.show_password_btns[service_name] = show_btn
                self.password_labels[service_name] = pwd_label

        # Update scroll region
        self.service_frame_inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def toggle_detail(self, service_name):
        """Show/hide the detail panel for a service."""
        if service_name not in self.service_data:
            return

        visible = self.detail_visible[service_name]
        detail_panel = self.details_panels[service_name]
        row_frame = self.rows[service_name]

        if visible:
            # Hide the detail panel
            detail_panel.pack_forget()
            row_frame.pack(fill=X, pady=2)
            self.detail_visible[service_name] = False
        else:
            # Hide the row, show the detail panel
            row_frame.pack_forget()
            detail_panel.pack(fill=X, pady=2, padx=10)
            self.detail_visible[service_name] = True

    def show_password(self, service_name):
        """Reveal the password for the service."""
        if service_name not in self.service_data:
            return

        btn = self.show_password_btns[service_name]
        pwd_label = self.password_labels[service_name]

        if btn.cget("text") == "Show":
            # Reveal the password
            entry = self.service_data[service_name]
            try:
                decrypted_password = self.encryption_service.decrypt_text(
                    entry['encrypted_password'])
                pwd_label.config(text=decrypted_password)
                btn.config(text="Hide")
            except Exception as e:
                pwd_label.config(text=f"Erro: {str(e)[:50]}")
                btn.config(text="Show")
        else:
            # Hide the password again
            pwd_label.config(text="••••••")
            btn.config(text="Show")

    def refresh_services(self):
        """Refresh the service list."""
        self.load_services()
