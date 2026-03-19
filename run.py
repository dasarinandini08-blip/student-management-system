import tkinter as tk
from database import init_db
from auth_window import AuthWindow
from main_window import MainWindow


def main():
    init_db()
    root = tk.Tk()
    root.resizable(False, False)

    app_state = {"window": None}

    def on_login_success(user):
        root.resizable(True, True)
        for w in root.winfo_children():
            w.destroy()
        root.title(f"SMS — {user['name']}")
        app_state["window"] = MainWindow(root, user, on_logout)

    def on_logout():
        root.resizable(False, False)
        for w in root.winfo_children():
            w.destroy()
        AuthWindow(root, on_login_success)

    AuthWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()