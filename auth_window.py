import tkinter as tk
from tkinter import messagebox
from models import login_user, register_user

ACCENT = "#6c63ff"
BG     = "#1e1e2e"
SURF   = "#2a2a3e"
TEXT   = "#cdd6f4"
MUTED  = "#a9b1d6"
GREEN  = "#4caf50"
RED    = "#f44336"


class AuthWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("Student Management System — Login")
        self.root.geometry("480x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.mode = "login"
        self._center_window()
        self.build()

    def _center_window(self):
        self.root.update_idletasks()
        w = 480
        h = 680 if self.mode == "register" else 540
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def build(self):
        for w in self.root.winfo_children():
            w.destroy()

        # Resize window based on mode
        win_w = 480
        win_h = 680 if self.mode == "register" else 540
        self.root.geometry(f"{win_w}x{win_h}")

        # Top banner
        banner = tk.Frame(self.root, bg=ACCENT, height=75)
        banner.pack(fill="x")
        banner.pack_propagate(False)
        tk.Label(banner, text="🎓  Student Management System",
                 font=("Helvetica", 14, "bold"),
                 bg=ACCENT, fg="white").pack(expand=True)

        # Card
        card = tk.Frame(self.root, bg=SURF, padx=36, pady=16)
        card.pack(fill="both", expand=True, padx=36, pady=16)

        title = "Create Account" if self.mode == "register" else "Sign In"
        tk.Label(card, text=title, font=("Helvetica", 16, "bold"),
                 bg=SURF, fg=TEXT).pack(anchor="w", pady=(0, 2))
        subtitle = "Fill in your details to register" if self.mode == "register" \
                   else "Enter your credentials to continue"
        tk.Label(card, text=subtitle, font=("Helvetica", 9),
                 bg=SURF, fg=MUTED).pack(anchor="w", pady=(0, 8))

        self.fields = {}

        if self.mode == "register":
            self._field(card, "Full Name", "name")
            self._field(card, "Role", "role", is_combo=True,
                        values=["student", "faculty", "admin"])

        self._field(card, "Email Address", "email")
        self._field(card, "Password", "password", show="•")

        if self.mode == "register":
            self._field(card, "Confirm Password", "confirm", show="•")

        self.status_lbl = tk.Label(card, text="", bg=SURF,
                                    fg=RED, font=("Helvetica", 9),
                                    wraplength=320)
        self.status_lbl.pack(pady=(4, 0))

        # Main button
        main_text = "Create Account" if self.mode == "register" else "Sign In"
        tk.Button(card, text=main_text,
                  command=self.submit,
                  bg=ACCENT, fg="white",
                  font=("Helvetica", 11, "bold"),
                  relief="flat", cursor="hand2",
                  padx=20, pady=8,
                  activebackground="#5550dd",
                  activeforeground="white").pack(fill="x", pady=(10, 6))

        # Toggle link
        if self.mode == "login":
            msg = "Don't have an account?"
            lnk = "Create Account"
        else:
            msg = "Already have an account?"
            lnk = "Sign In"

        toggle_frame = tk.Frame(card, bg=SURF)
        toggle_frame.pack()
        tk.Label(toggle_frame, text=msg, bg=SURF,
                 fg=MUTED, font=("Helvetica", 9)).pack(side="left")
        tk.Label(toggle_frame, text=" " + lnk, bg=SURF,
                 fg=ACCENT, font=("Helvetica", 9, "underline"),
                 cursor="hand2").pack(side="left")
        toggle_frame.winfo_children()[-1].bind("<Button-1>", self.toggle_mode)

        if self.mode == "login":
            tk.Label(card, text="Demo: admin@sms.com / admin123",
                     bg=SURF, fg=MUTED,
                     font=("Helvetica", 8)).pack(pady=(12, 0))

    def _field(self, parent, label, key, show=None, is_combo=False, values=None):
        tk.Label(parent, text=label, bg=SURF, fg=MUTED,
                 font=("Helvetica", 9)).pack(anchor="w", pady=(4, 1))
        if is_combo:
            from tkinter import ttk
            var = tk.StringVar(value=values[0])
            cb = ttk.Combobox(parent, textvariable=var, values=values,
                              state="readonly", font=("Helvetica", 10))
            cb.pack(fill="x", ipady=3)
            self.fields[key] = var
        else:
            e = tk.Entry(parent, font=("Helvetica", 11),
                         bg="#1e1e2e", fg=TEXT,
                         insertbackground=TEXT,
                         relief="flat",
                         highlightthickness=1,
                         highlightbackground=ACCENT,
                         highlightcolor=ACCENT,
                         show=show or "")
            e.pack(fill="x", ipady=5)
            self.fields[key] = e
            if key == "password" and self.mode == "login":
                e.bind("<Return>", lambda _: self.submit())

    def toggle_mode(self, _=None):
        self.mode = "register" if self.mode == "login" else "login"
        self.build()

    def get(self, key):
        w = self.fields.get(key)
        if w is None:
            return ""
        if isinstance(w, tk.StringVar):
            return w.get()
        return w.get().strip()

    def show_status(self, msg, color=RED):
        self.status_lbl.config(text=msg, fg=color)

    def submit(self):
        if self.mode == "login":
            email = self.get("email")
            pw    = self.get("password")
            if not email or not pw:
                self.show_status("Please fill in all fields.")
                return
            ok, result = login_user(email, pw)
            if ok:
                self.on_success(result)
            else:
                self.show_status(result)
        else:
            name    = self.get("name")
            email   = self.get("email")
            role    = self.get("role")
            pw      = self.get("password")
            confirm = self.get("confirm")
            if not all([name, email, pw, confirm]):
                self.show_status("Please fill in all fields.")
                return
            if pw != confirm:
                self.show_status("Passwords do not match.")
                return
            if len(pw) < 6:
                self.show_status("Password must be at least 6 characters.")
                return
            ok, msg = register_user(name, email, pw, role)
            if ok:
                self.show_status(msg, GREEN)
                self.root.after(1200, self.toggle_mode)
            else:
                self.show_status(msg)