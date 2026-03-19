import tkinter as tk
from tkinter import ttk, messagebox
import csv, os, datetime
import models

THEMES = {
    "dark": {
        "bg":     "#1e1e2e",
        "surf":   "#2a2a3e",
        "surf2":  "#252535",
        "border": "#44446a",
        "text":   "#cdd6f4",
        "muted":  "#a9b1d6",
        "accent": "#6c63ff",
        "green":  "#4caf50",
        "red":    "#f44336",
        "orange": "#ff9800",
        "blue":   "#2196f3",
    },
    "light": {
        "bg":     "#f0f0f8",
        "surf":   "#ffffff",
        "surf2":  "#f5f5fc",
        "border": "#d0d0e8",
        "text":   "#1e1e2e",
        "muted":  "#666680",
        "accent": "#6c63ff",
        "green":  "#388e3c",
        "red":    "#d32f2f",
        "orange": "#e65100",
        "blue":   "#1565c0",
    },
}

GRADE_COLORS = {
    "A+": "#9c27b0", "A": "#4caf50", "B": "#2196f3",
    "C":  "#ff9800", "D": "#f44336", "F": "#b71c1c",
}

DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# ── Sidebar tabs per role ────────────────────────────────────────────────────
ROLE_TABS = {
    "admin": [
        ("dashboard",     "📊  Dashboard"),
        ("students",      "👨‍🎓  Students"),
        ("attendance",    "📋  Attendance"),
        ("marks",         "📝  Marks & Grades"),
        ("timetable",     "📅  Timetable"),
        ("fees",          "💳  Fees"),
        ("assignments",   "📌  Assignments"),
        ("exams",         "📃  Exam Schedule"),
        ("library",       "📚  Library"),
        ("notifications", "🔔  Notifications"),
        ("messages",      "💬  Messages"),
        ("users",         "👥  User Accounts"),
    ],
    "faculty": [
        ("dashboard",     "📊  Dashboard"),
        ("students",      "👨‍🎓  Students"),
        ("attendance",    "📋  Attendance"),
        ("marks",         "📝  Marks & Grades"),
        ("timetable",     "📅  Timetable"),
        ("assignments",   "📌  Assignments"),
        ("exams",         "📃  Exam Schedule"),
        ("library",       "📚  Library"),
        ("notifications", "🔔  Notifications"),
        ("messages",      "💬  Messages"),
    ],
    "student": [
        ("dashboard",     "📊  My Dashboard"),
        ("my_attendance", "📋  My Attendance"),
        ("my_marks",      "📝  My Marks"),
        ("timetable",     "📅  Timetable"),
        ("my_fees",       "💳  My Fees"),
        ("assignments",   "📌  Assignments"),
        ("exams",         "📃  Exam Schedule"),
        ("library",       "📚  Library"),
        ("notifications", "🔔  Notifications"),
        ("messages",      "💬  Messages"),
    ],
}


class MainWindow:
    def __init__(self, root, user, on_logout):
        self.root      = root
        self.user      = user
        self.on_logout = on_logout
        self.theme_name = "dark"
        self.T          = THEMES["dark"]

        # Resolve the student's own DB record ID (used to filter their data)
        self.student_record_id = None
        if user["role"] == "student":
            self.student_record_id = self._find_student_id(user["email"])

        self.root.title(f"SMS — {user['name']}  ({user['role'].title()})")
        self.root.geometry("1200x750")
        self.root.resizable(True, True)
        self.root.configure(bg=self.T["bg"])
        self._center()
        self.build_layout()
        self.show_tab("dashboard")

    def _center(self):
        self.root.update_idletasks()
        w, h = 1200, 750
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _find_student_id(self, email):
        """Return the students.id whose email matches the logged-in user."""
        all_students = models.get_all_students()
        for s in all_students:
            if s[3] and s[3].lower() == email.lower():
                return s[0]
        return None

    # ── Layout ────────────────────────────────────────────────────────────────

    def build_layout(self):
        T = self.T

        self.topbar = tk.Frame(self.root, bg=T["accent"], height=50)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        tk.Label(self.topbar, text="🎓  Student Management System",
                 font=("Helvetica", 14, "bold"),
                 bg=T["accent"], fg="white").pack(side="left", padx=16)

        right = tk.Frame(self.topbar, bg=T["accent"])
        right.pack(side="right", padx=10)

        self.notif_btn = tk.Label(right, text="🔔 0",
                                   bg=T["accent"], fg="white",
                                   font=("Helvetica", 11), cursor="hand2")
        self.notif_btn.pack(side="left", padx=8)
        self.notif_btn.bind("<Button-1>", lambda _: self.show_tab("notifications"))

        role_badge_colors = {"admin": "#f44336", "faculty": "#ff9800", "student": "#4caf50"}
        badge_bg = role_badge_colors.get(self.user["role"], "#555")
        tk.Label(right,
                 text=f"  {self.user['role'].title()}  ",
                 bg=badge_bg, fg="white",
                 font=("Helvetica", 8, "bold"),
                 padx=4).pack(side="left", padx=4)

        tk.Label(right, text=f"👤 {self.user['name']}",
                 bg=T["accent"], fg="white",
                 font=("Helvetica", 10)).pack(side="left", padx=6)

        tk.Button(right, text="🌙 Theme", command=self.toggle_theme,
                  bg="white", fg=T["accent"],
                  font=("Helvetica", 8, "bold"),
                  relief="flat", padx=8, pady=2,
                  cursor="hand2").pack(side="left", padx=4)

        tk.Button(right, text="Logout", command=self.logout,
                  bg=T["red"], fg="white",
                  font=("Helvetica", 8, "bold"),
                  relief="flat", padx=10, pady=2,
                  cursor="hand2").pack(side="left", padx=4)

        body = tk.Frame(self.root, bg=T["bg"])
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg=T["surf"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg=T["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        self.nav_buttons = {}
        self.build_sidebar()

    def build_sidebar(self):
        T    = self.T
        role = self.user["role"]
        for w in self.sidebar.winfo_children():
            w.destroy()

        # Role banner at top of sidebar
        role_colors = {"admin": "#f44336", "faculty": "#ff9800", "student": "#4caf50"}
        role_bg = role_colors.get(role, T["accent"])
        banner = tk.Frame(self.sidebar, bg=role_bg, pady=10)
        banner.pack(fill="x")
        tk.Label(banner,
                 text=f"Logged in as\n{role.title()}",
                 bg=role_bg, fg="white",
                 font=("Helvetica", 9, "bold"),
                 justify="center").pack()

        tk.Label(self.sidebar, text="NAVIGATION",
                 bg=T["surf"], fg=T["muted"],
                 font=("Helvetica", 8, "bold")).pack(pady=(12, 4), padx=12, anchor="w")

        tabs = ROLE_TABS.get(role, ROLE_TABS["student"])
        self.nav_buttons = {}
        for key, label in tabs:
            btn = tk.Button(self.sidebar, text=label,
                            anchor="w", relief="flat",
                            bg=T["surf"], fg=T["text"],
                            font=("Helvetica", 10),
                            padx=14, pady=7,
                            cursor="hand2",
                            command=lambda k=key: self.show_tab(k))
            btn.pack(fill="x", padx=6, pady=1)
            self.nav_buttons[key] = btn

        tk.Label(self.sidebar, text=self.user["email"],
                 bg=T["surf"], fg=T["muted"],
                 font=("Helvetica", 7),
                 wraplength=180).pack(side="bottom", pady=8)

    def show_tab(self, name):
        T = self.T
        for key, btn in self.nav_buttons.items():
            btn.config(bg=T["accent"] if key == name else T["surf"],
                       fg="white"    if key == name else T["text"])

        for w in self.content.winfo_children():
            w.destroy()

        tab_builders = {
            # shared / admin+faculty
            "dashboard":     self.tab_dashboard,
            "students":      self.tab_students,
            "attendance":    self.tab_attendance,
            "marks":         self.tab_marks,
            "timetable":     self.tab_timetable,
            "fees":          self.tab_fees,
            "assignments":   self.tab_assignments,
            "exams":         self.tab_exams,
            "library":       self.tab_library,
            "notifications": self.tab_notifications,
            "messages":      self.tab_messages,
            "users":         self.tab_users,
            # student-only views
            "my_attendance": self.tab_my_attendance,
            "my_marks":      self.tab_my_marks,
            "my_fees":       self.tab_my_fees,
        }
        builder = tab_builders.get(name)
        if builder:
            builder()
        self.update_notif_badge()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def is_admin(self):
        return self.user["role"] == "admin"

    def is_faculty(self):
        return self.user["role"] == "faculty"

    def is_student(self):
        return self.user["role"] == "student"

    def update_notif_badge(self):
        notifs = models.get_notifications(self.user["role"])
        count  = sum(1 for n in notifs if n[7] == 0)
        self.notif_btn.config(text=f"🔔 {count}")

    def page_title(self, text, subtitle=""):
        T   = self.T
        hdr = tk.Frame(self.content, bg=T["bg"])
        hdr.pack(fill="x", padx=20, pady=(16, 6))
        tk.Label(hdr, text=text, font=("Helvetica", 16, "bold"),
                 bg=T["bg"], fg=T["text"]).pack(side="left")
        if subtitle:
            tk.Label(hdr, text=f"   {subtitle}", font=("Helvetica", 10),
                     bg=T["bg"], fg=T["muted"]).pack(side="left", pady=(4, 0))
        return hdr

    def access_denied(self, reason="You do not have permission to view this page."):
        T = self.T
        self.page_title("Access Denied")
        tk.Label(self.content, text="🔒", font=("Helvetica", 48),
                 bg=T["bg"], fg=T["red"]).pack(pady=(40, 8))
        tk.Label(self.content, text=reason,
                 font=("Helvetica", 12),
                 bg=T["bg"], fg=T["muted"]).pack()

    def stat_card(self, parent, label, value, color):
        T    = self.T
        card = tk.Frame(parent, bg=T["surf"], padx=16, pady=12)
        card.pack(side="left", expand=True, fill="both", padx=5)
        tk.Frame(card, bg=color, width=4, height=40).pack(side="left", padx=(0, 10))
        info = tk.Frame(card, bg=T["surf"])
        info.pack(side="left")
        tk.Label(info, text=str(value), font=("Helvetica", 22, "bold"),
                 bg=T["surf"], fg=T["text"]).pack(anchor="w")
        tk.Label(info, text=label, font=("Helvetica", 9),
                 bg=T["surf"], fg=T["muted"]).pack(anchor="w")

    def make_table(self, parent, columns, rows, widths=None, height=12):
        T     = self.T
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SMS.Treeview",
                         background=T["surf"], foreground=T["text"],
                         rowheight=26, fieldbackground=T["surf"],
                         font=("Helvetica", 9))
        style.configure("SMS.Treeview.Heading",
                         background=T["accent"], foreground="white",
                         font=("Helvetica", 9, "bold"))
        style.map("SMS.Treeview", background=[("selected", T["accent"])])

        frame = tk.Frame(parent, bg=T["bg"])
        frame.pack(fill="both", expand=True, padx=18, pady=6)

        tree = ttk.Treeview(frame, columns=columns, show="headings",
                             style="SMS.Treeview", height=height)
        for i, col in enumerate(columns):
            w = widths[i] if widths else 120
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        for i, row in enumerate(rows):
            tree.insert("", "end", values=row,
                        tags=("odd" if i % 2 == 0 else "even",))
        tree.tag_configure("odd",  background=T["surf"])
        tree.tag_configure("even", background=T["surf2"])
        return tree

    def input_row(self, parent, label, key, fields_dict,
                  width=20, is_combo=False, values=None, show=None):
        T   = self.T
        row = tk.Frame(parent, bg=T["surf"])
        row.pack(fill="x", pady=3)
        tk.Label(row, text=label + ":", width=16, anchor="e",
                 bg=T["surf"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(side="left", padx=(0, 6))
        if is_combo:
            var = tk.StringVar(value=(values[0] if values else ""))
            cb  = ttk.Combobox(row, textvariable=var, values=values or [],
                               width=width - 2, state="readonly")
            cb.pack(side="left")
            fields_dict[key] = var
        else:
            e = tk.Entry(row, bg=T["bg"], fg=T["text"],
                         insertbackground=T["text"],
                         relief="flat", width=width,
                         highlightthickness=1,
                         highlightbackground=T["accent"],
                         highlightcolor=T["accent"],
                         font=("Helvetica", 10),
                         show=show or "")
            e.pack(side="left")
            fields_dict[key] = e

    def action_btn(self, parent, text, color, cmd):
        tk.Button(parent, text=text, bg=color, fg="white",
                  font=("Helvetica", 9, "bold"), relief="flat",
                  padx=12, pady=5, cursor="hand2",
                  command=cmd).pack(side="left", padx=4)

    def mini_bar_chart(self, parent, data, title=""):
        T   = self.T
        box = tk.LabelFrame(parent, text=f" {title} ",
                            bg=T["bg"], fg=T["muted"],
                            font=("Helvetica", 8, "bold"),
                            relief="groove", bd=1, padx=8, pady=6)
        box.pack(side="left", expand=True, fill="both", padx=5)
        colors = [T["accent"], T["green"], T["orange"], T["blue"], T["red"]]
        max_v  = max((v for _, v in data), default=1)
        for i, (label, val) in enumerate(data):
            bw  = max(4, int(val / max(max_v, 1) * 130)) if val else 0
            row = tk.Frame(box, bg=T["bg"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=str(label), width=6, anchor="e",
                     bg=T["bg"], fg=T["muted"],
                     font=("Helvetica", 8)).pack(side="left")
            bg_bar = tk.Frame(row, bg=T["surf2"], height=14, width=140)
            bg_bar.pack(side="left", padx=4)
            bg_bar.pack_propagate(False)
            clr = GRADE_COLORS.get(str(label), colors[i % len(colors)])
            if bw:
                tk.Frame(bg_bar, bg=clr, width=bw).pack(side="left", fill="y")
            tk.Label(row, text=str(val), bg=T["bg"], fg=T["text"],
                     font=("Helvetica", 8)).pack(side="left")

    def status_bar(self, parent):
        T   = self.T
        lbl = tk.Label(parent, text="", bg=T["bg"],
                        fg=T["green"], font=("Helvetica", 9))
        lbl.pack(pady=2)
        return lbl

    def set_status(self, lbl, msg, color=None):
        lbl.config(text=msg, fg=color or self.T["green"])
        self.root.after(2500, lambda: lbl.config(text=""))

    def export_to_csv(self, columns, rows, filename):
        path = os.path.join(os.path.expanduser("~"), filename)
        with open(path, "w", newline="") as f:
            csv.writer(f).writerows([columns, *rows])
        messagebox.showinfo("Exported", f"Saved to:\n{path}")

    # ═══════════════════════════════════════════════════════════════════════════
    #  TABS — ADMIN + FACULTY
    # ═══════════════════════════════════════════════════════════════════════════

    # ── Dashboard (admin / faculty) ────────────────────────────────────────────

    def tab_dashboard(self):
        T = self.T
        if self.is_student():
            self._student_dashboard()
            return

        self.page_title("Dashboard", f"Welcome back, {self.user['name']}!")
        stats = models.get_dashboard_stats()

        cards = tk.Frame(self.content, bg=T["bg"])
        cards.pack(fill="x", padx=14, pady=(0, 8))
        self.stat_card(cards, "Total Students",   stats["total_students"],        T["accent"])
        self.stat_card(cards, "Avg Attendance %", f"{stats['avg_attendance']}%",  T["green"])
        self.stat_card(cards, "Avg Marks %",      f"{stats['avg_marks']}%",       T["blue"])
        self.stat_card(cards, "Pending Fees",      stats["pending_fees"],          T["red"])

        chart_row = tk.Frame(self.content, bg=T["bg"])
        chart_row.pack(fill="x", padx=14, pady=(0, 8))
        self.mini_bar_chart(chart_row, models.get_grade_distribution(), "Grade Distribution")
        self.mini_bar_chart(chart_row, models.get_course_distribution(), "Students by Course")

        self.page_title("Attendance Summary")
        att  = models.get_attendance_summary()
        cols = ("ID", "Name", "Course", "Total Days", "Present", "Attendance %")
        rows = [(r[0], r[1], r[2], r[3], r[4], f"{r[5]}%") for r in att]
        tree = self.make_table(self.content, cols, rows,
                               [40, 160, 120, 80, 70, 90], height=6)
        for item in tree.get_children():
            vals = tree.item(item, "values")
            if float(str(vals[5]).replace("%", "")) < 75:
                tree.tag_configure(f"low_{item}", background="#f4433620")
                tree.item(item, tags=(f"low_{item}",))

        self.page_title("Recent Notifications")
        notifs = models.get_notifications(self.user["role"])[:5]
        nrows  = [(n[1], n[2][:60], n[3], n[6][:10]) for n in notifs]
        self.make_table(self.content, ("Title","Message","Type","Date"),
                        nrows, [160, 300, 80, 90], height=4)

    # ── Students (admin / faculty) ─────────────────────────────────────────────

    def tab_students(self):
        if self.is_student():
            self.access_denied("Students cannot access the student management panel.")
            return

        T = self.T
        self.page_title("Student Management",
                        "View all students" if self.is_faculty() else "Add, edit and manage students")

        top = tk.Frame(self.content, bg=T["bg"])
        top.pack(fill="x", padx=18, pady=(0, 6))
        self.student_search = tk.StringVar()
        self.student_search.trace("w", lambda *_: self._refresh_students())
        tk.Label(top, text="Search:", bg=T["bg"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(side="left", padx=(0, 4))
        tk.Entry(top, textvariable=self.student_search,
                 bg=T["surf"], fg=T["text"],
                 insertbackground=T["text"], relief="flat", width=26,
                 highlightthickness=1, highlightbackground=T["accent"],
                 highlightcolor=T["accent"],
                 font=("Helvetica", 10)).pack(side="left", padx=(0, 10))

        if self.is_admin():
            self.action_btn(top, "+ Add Student", T["green"], lambda: self._student_form())
        self.action_btn(top, "📤 Export CSV", T["blue"], self._export_students)

        cols = ("ID","Stu ID","Name","Course","Year","Sec","Phone","Email")
        self.student_tree = self.make_table(self.content, cols, [],
                                             [35,60,160,120,40,40,100,150], height=14)
        self._refresh_students()

        act = tk.Frame(self.content, bg=T["bg"])
        act.pack(fill="x", padx=18, pady=4)
        self.action_btn(act, "📋 View Details", T["accent"], self._view_student)
        if self.is_admin():
            self.action_btn(act, "✏ Edit",   T["blue"],  self._edit_student)
            self.action_btn(act, "🗑 Delete", T["red"],   self._delete_student)

    def _refresh_students(self):
        q    = self.student_search.get() if hasattr(self, "student_search") else ""
        rows = models.search_students(q) if q else models.get_all_students()
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for i, r in enumerate(rows):
            self.student_tree.insert("", "end", iid=str(r[0]),
                                      values=(r[0],r[1],r[2],r[7],r[8],r[9],r[4],r[3]),
                                      tags=("odd" if i%2==0 else "even",))

    def _get_selected_student(self):
        sel = self.student_tree.focus()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a student.")
            return None
        return int(sel)

    def _student_form(self, sid=None):
        T    = self.T
        data = models.get_student(sid) if sid else None
        win  = tk.Toplevel(self.root)
        win.title("Edit Student" if sid else "Add Student")
        win.geometry("520x540")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="Edit Student" if sid else "New Student",
                 font=("Helvetica", 14, "bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16, 4))

        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=10)
        form.pack(fill="both", expand=True)
        fields = {}
        self.input_row(form, "Student ID",    "sid",    fields, width=28)
        self.input_row(form, "Full Name",     "name",   fields, width=28)
        self.input_row(form, "Email",         "email",  fields, width=28)
        self.input_row(form, "Phone",         "phone",  fields, width=18)
        self.input_row(form, "Date of Birth", "dob",    fields, width=14)
        self.input_row(form, "Gender",        "gender", fields, is_combo=True,
                       values=["Male","Female","Other"])
        self.input_row(form, "Course",        "course", fields, is_combo=True,
                       values=["B.Tech CSE","B.Tech ECE","MBA","B.Sc CS","B.Com"])
        self.input_row(form, "Year",          "year",   fields, is_combo=True,
                       values=["1","2","3","4"])
        self.input_row(form, "Section",       "sec",    fields, is_combo=True,
                       values=["A","B","C","D"])
        self.input_row(form, "Address",       "addr",   fields, width=28)
        self.input_row(form, "Guardian Name", "gname",  fields, width=24)
        self.input_row(form, "Guardian Phone","gphone", fields, width=16)

        if data:
            defs = {"sid":data[1],"name":data[2],"email":data[3],"phone":data[4],
                    "dob":data[5],"gender":data[6],"addr":data[7],"course":data[8],
                    "year":str(data[9]),"sec":data[10],"gname":data[11],"gphone":data[12]}
            for k, v in defs.items():
                w = fields.get(k)
                if w is None: continue
                if isinstance(w, tk.StringVar): w.set(v or "")
                else: w.insert(0, v or "")

        def gv(k):
            w = fields[k]
            return w.get() if isinstance(w, tk.StringVar) else w.get().strip()

        slbl = tk.Label(win, text="", bg=T["surf"], fg=T["green"],
                         font=("Helvetica", 9))
        slbl.pack()

        def save():
            row_data = (gv("sid"),gv("name"),gv("email"),gv("phone"),
                        gv("dob"),gv("gender"),gv("addr"),gv("course"),
                        int(gv("year") or 1),gv("sec"),gv("gname"),gv("gphone"))
            if not row_data[1]:
                slbl.config(text="Name is required!", fg=T["red"]); return
            if sid:
                models.update_student(sid, row_data)
                slbl.config(text="Updated!")
            else:
                ok, msg = models.add_student(row_data)
                if not ok:
                    slbl.config(text=msg, fg=T["red"]); return
                slbl.config(text=msg)
            win.after(800, win.destroy)
            self._refresh_students()

        tk.Button(win, text="💾 Save", bg=T["accent"], fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat",
                  padx=20, pady=6, cursor="hand2",
                  command=save).pack(pady=10)

    def _edit_student(self):
        sid = self._get_selected_student()
        if sid: self._student_form(sid)

    def _delete_student(self):
        sid = self._get_selected_student()
        if sid and messagebox.askyesno("Confirm", f"Delete student ID {sid}?"):
            models.delete_student(sid)
            self._refresh_students()

    def _view_student(self):
        sid = self._get_selected_student()
        if not sid: return
        s = models.get_student(sid)
        if not s: return
        T   = self.T
        win = tk.Toplevel(self.root)
        win.title(f"Student: {s[2]}")
        win.geometry("400x460")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text=s[2], font=("Helvetica", 16, "bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(20, 2))
        tk.Label(win, text=f"{s[8]}  •  Year {s[9]}  •  Section {s[10]}",
                 bg=T["surf"], fg=T["muted"], font=("Helvetica", 10)).pack(pady=(0,16))

        frm = tk.Frame(win, bg=T["surf"], padx=24)
        frm.pack(fill="x")
        for lbl, val in [("Student ID",s[1]),("Email",s[3]),("Phone",s[4]),
                          ("DOB",s[5]),("Gender",s[6]),("Address",s[7]),
                          ("Guardian",s[11]),("Guardian Ph.",s[12])]:
            r = tk.Frame(frm, bg=T["surf"])
            r.pack(fill="x", pady=3)
            tk.Label(r, text=lbl+":", width=14, anchor="e",
                     bg=T["surf"], fg=T["muted"],
                     font=("Helvetica", 9)).pack(side="left")
            tk.Label(r, text=val or "—", bg=T["surf"],
                     fg=T["text"], font=("Helvetica", 9)).pack(side="left", padx=6)

        marks = models.get_marks(sid)
        if marks:
            avg = sum(m[4]/m[5]*100 for m in marks)/len(marks)
            tk.Label(win, text=f"Average Score: {avg:.1f}%",
                     bg=T["surf"], fg=T["accent"],
                     font=("Helvetica", 11, "bold")).pack(pady=10)

    def _export_students(self):
        self.export_to_csv(
            ["ID","StudentID","Name","Email","Phone","DOB","Gender",
             "Address","Course","Year","Section","Guardian","Guardian Ph","Created"],
            models.get_all_students(), "students_export.csv")

    # ── Attendance (admin / faculty) ────────────────────────────────────────────

    def tab_attendance(self):
        if self.is_student():
            self.access_denied("Use 'My Attendance' in the sidebar to view your own attendance.")
            return

        T     = self.T
        today = str(datetime.date.today())
        self.page_title("Attendance Tracking", "Mark and view attendance")

        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0, 8))

        tk.Label(ctrl, text="Date:", bg=T["bg"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(side="left", padx=(0, 4))
        date_e = tk.Entry(ctrl, bg=T["surf"], fg=T["text"],
                          insertbackground=T["text"], width=12,
                          relief="flat", font=("Helvetica", 10),
                          highlightthickness=1,
                          highlightbackground=T["accent"],
                          highlightcolor=T["accent"])
        date_e.insert(0, today)
        date_e.pack(side="left", padx=(0, 10))

        tk.Label(ctrl, text="Subject:", bg=T["bg"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(side="left", padx=(0, 4))
        subj_var = tk.StringVar(value="Programming")
        ttk.Combobox(ctrl, textvariable=subj_var, width=14,
                     values=["Mathematics","Physics","Programming","English","All"],
                     state="readonly").pack(side="left", padx=(0, 10))

        def load_att():
            d = date_e.get().strip()
            s = subj_var.get()
            rows = models.get_attendance(
                date=d if d else None,
                subject=s if s != "All" else None)
            for item in self.att_tree.get_children():
                self.att_tree.delete(item)
            for i, r in enumerate(rows):
                tag = "present" if r[5] == "Present" else "absent"
                self.att_tree.insert("", "end", iid=str(r[0]), values=r, tags=(tag,))

        self.action_btn(ctrl, "🔍 Load", T["blue"], load_att)

        def mark_all():
            d = date_e.get().strip() or today
            s = subj_var.get()
            for stu in models.get_all_students():
                models.mark_attendance(stu[0], d, s, "Present", self.user["email"])
            load_att()
            messagebox.showinfo("Done", "All students marked Present!")

        self.action_btn(ctrl, "✅ Mark All Present", T["green"], mark_all)

        cols = ("Log ID","Stu ID","Name","Date","Subject","Status","Marked By")
        self.att_tree = self.make_table(self.content, cols, [],
                                         [50,60,150,90,100,70,130], height=13)
        self.att_tree.tag_configure("present", background="#4caf5015")
        self.att_tree.tag_configure("absent",  background="#f4433615")
        load_att()

        act = tk.Frame(self.content, bg=T["bg"])
        act.pack(fill="x", padx=18, pady=4)
        tk.Label(act, text="Quick mark selected:", bg=T["bg"],
                 fg=T["muted"], font=("Helvetica", 9)).pack(side="left", padx=(0, 8))

        def quick_mark(status):
            sel = self.att_tree.focus()
            if not sel:
                messagebox.showwarning("No Selection", "Select a record first.")
                return
            vals = self.att_tree.item(sel, "values")
            models.mark_attendance(vals[0], vals[3], vals[4], status, self.user["email"])
            load_att()

        self.action_btn(act, "✅ Present", T["green"], lambda: quick_mark("Present"))
        self.action_btn(act, "❌ Absent",  T["red"],   lambda: quick_mark("Absent"))

    # ── Marks (admin / faculty) ────────────────────────────────────────────────

    def tab_marks(self):
        if self.is_student():
            self.access_denied("Use 'My Marks' in the sidebar to view your own marks.")
            return

        T = self.T
        self.page_title("Marks & Grade Management")

        tk.Label(self.content, text="Performance Summary",
                 font=("Helvetica", 12, "bold"),
                 bg=T["bg"], fg=T["text"]).pack(anchor="w", padx=18, pady=(0,4))
        gpa  = models.get_gpa_summary()
        gcols = ("ID","Name","Course","Avg Score %","Subjects")
        grows = [(r[0],r[1],r[2],f"{r[3]}%",r[4]) for r in gpa]
        gpa_tree = self.make_table(self.content, gcols, grows,
                                    [40,160,120,90,70], height=5)
        for item in gpa_tree.get_children():
            avg = float(str(gpa_tree.item(item,"values")[3]).replace("%",""))
            clr = T["green"] if avg>=75 else T["orange"] if avg>=60 else T["red"]
            gpa_tree.tag_configure(f"r_{item}", foreground=clr)
            gpa_tree.item(item, tags=(f"r_{item}",))

        tk.Label(self.content, text="Detailed Marks",
                 font=("Helvetica", 12, "bold"),
                 bg=T["bg"], fg=T["text"]).pack(anchor="w", padx=18, pady=(8,4))

        top = tk.Frame(self.content, bg=T["bg"])
        top.pack(fill="x", padx=18, pady=(0,4))
        students = models.get_all_students()
        filt     = tk.StringVar(value="All")

        def reload_marks(*_):
            sel = filt.get()
            sid = None if sel=="All" else int(sel.split(":")[0])
            rows = models.get_marks(sid)
            for item in self.marks_tree.get_children():
                self.marks_tree.delete(item)
            for i, r in enumerate(rows):
                self.marks_tree.insert("","end",
                                        values=(*r, f"{r[4]/r[5]*100:.1f}%"),
                                        tags=("odd" if i%2==0 else "even",))

        ttk.Combobox(top, textvariable=filt,
                     values=["All"]+[f"{s[0]}: {s[2]}" for s in students],
                     width=24, state="readonly").pack(side="left", padx=(0,8))
        filt.trace("w", reload_marks)
        self.action_btn(top, "📤 Export", T["blue"],
                         lambda: self.export_to_csv(
                             ["ID","Name","Subject","Exam","Marks","Max","Grade","Sem","Pct"],
                             [self.marks_tree.item(i,"values")
                              for i in self.marks_tree.get_children()],
                             "marks_export.csv"))
        self.action_btn(top, "+ Add Marks", T["green"], self._add_marks_form)

        mcols = ("ID","Name","Subject","Exam Type","Marks","Max","Grade","Semester","Score%")
        self.marks_tree = self.make_table(self.content, mcols, [],
                                           [40,130,110,90,60,50,55,80,60], height=9)
        reload_marks()

    def _add_marks_form(self):
        T   = self.T
        win = tk.Toplevel(self.root)
        win.title("Add Marks")
        win.geometry("380x360")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="Add / Update Marks",
                 font=("Helvetica", 13, "bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16,10))
        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=8)
        form.pack(fill="both", expand=True)
        fields = {}
        students = models.get_all_students()
        self.input_row(form,"Student","student",fields,is_combo=True,
                       values=[f"{s[0]}: {s[2]}" for s in students],width=26)
        self.input_row(form,"Subject","subject",fields,is_combo=True,
                       values=["Mathematics","Physics","Programming","English","Science"],width=26)
        self.input_row(form,"Exam Type","exam_type",fields,is_combo=True,
                       values=["Internal","External","Practical","Assignment"],width=20)
        self.input_row(form,"Marks","marks",fields,width=10)
        self.input_row(form,"Max Marks","max_marks",fields,width=10)
        self.input_row(form,"Semester","semester",fields,is_combo=True,
                       values=["Sem 1","Sem 2","Sem 3","Sem 4","Sem 5","Sem 6"],width=14)

        slbl = tk.Label(win, text="", bg=T["surf"],
                         fg=T["green"], font=("Helvetica", 9))
        slbl.pack()

        def save():
            stu_str = fields["student"].get()
            if not stu_str:
                slbl.config(text="Select a student",fg=T["red"]); return
            try:
                m  = float(fields["marks"].get())
                mm = float(fields["max_marks"].get())
            except ValueError:
                slbl.config(text="Enter valid numeric marks",fg=T["red"]); return
            if m > mm:
                slbl.config(text="Marks cannot exceed Max Marks!",fg=T["red"]); return
            models.add_marks(int(stu_str.split(":")[0]),
                             fields["subject"].get(), fields["exam_type"].get(),
                             m, mm, fields["semester"].get())
            slbl.config(text="Saved!")
            win.after(800, win.destroy)
            self.tab_marks()

        tk.Button(win, text="💾 Save Marks", bg=T["accent"], fg="white",
                  font=("Helvetica", 10,"bold"), relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=save).pack(pady=10)

    # ── Timetable (all roles — view; admin/faculty — add) ─────────────────────

    def tab_timetable(self):
        T = self.T
        self.page_title("Class Timetable", "Weekly schedule by course")

        courses    = ["B.Tech CSE","B.Tech ECE","MBA","B.Sc CS","B.Com"]
        sel_course = tk.StringVar(value="B.Tech CSE")

        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,8))
        tk.Label(ctrl, text="Course:", bg=T["bg"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(side="left", padx=(0,4))
        ttk.Combobox(ctrl, textvariable=sel_course, values=courses,
                     width=16, state="readonly").pack(side="left", padx=(0,10))

        def load_tt(*_):
            rows = models.get_timetable(sel_course.get())
            for item in self.tt_tree.get_children():
                self.tt_tree.delete(item)
            for i, r in enumerate(rows):
                self.tt_tree.insert("","end", values=r,
                                     tags=("odd" if i%2==0 else "even",))

        sel_course.trace("w", load_tt)
        if not self.is_student():
            self.action_btn(ctrl, "+ Add Slot", T["green"], self._add_timetable_form)

        cols = ("ID","Course","Day","Period","Time","Subject","Faculty","Room")
        self.tt_tree = self.make_table(self.content, cols, [],
                                        [35,100,85,55,80,110,110,70], height=16)
        load_tt()

    def _add_timetable_form(self):
        T   = self.T
        win = tk.Toplevel(self.root)
        win.title("Add Timetable Slot")
        win.geometry("360x320")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="Add Timetable Slot",
                 font=("Helvetica", 13,"bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16,10))
        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=8)
        form.pack(fill="both", expand=True)
        fields = {}
        self.input_row(form,"Course","course",fields,is_combo=True,
                       values=["B.Tech CSE","B.Tech ECE","MBA","B.Sc CS","B.Com"],width=20)
        self.input_row(form,"Day","day",fields,is_combo=True,values=DAYS_ORDER,width=14)
        self.input_row(form,"Period","period",fields,is_combo=True,
                       values=["1","2","3","4","5","6"],width=6)
        self.input_row(form,"Time Slot","time",fields,width=16)
        self.input_row(form,"Subject","subj",fields,width=20)
        self.input_row(form,"Faculty","faculty",fields,width=20)
        self.input_row(form,"Room","room",fields,width=10)

        def save():
            models.add_timetable(
                fields["course"].get(), fields["day"].get(),
                int(fields["period"].get() or 1),
                fields["time"].get().strip(), fields["subj"].get().strip(),
                fields["faculty"].get().strip(), fields["room"].get().strip())
            win.destroy()
            self.tab_timetable()

        tk.Button(win, text="💾 Save", bg=T["accent"], fg="white",
                  font=("Helvetica", 10,"bold"), relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=save).pack(pady=10)

    # ── Fees (admin only full; student → my_fees) ──────────────────────────────

    def tab_fees(self):
        if self.is_student():
            self.access_denied("Use 'My Fees' in the sidebar to view your own fees.")
            return
        if self.is_faculty():
            self.access_denied("Faculty members do not have access to fee management.")
            return

        T       = self.T
        summary = models.get_fee_summary()
        self.page_title("Fee Management", "Track payments, dues and receipts")

        cards   = tk.Frame(self.content, bg=T["bg"])
        cards.pack(fill="x", padx=14, pady=(0,8))
        totals  = {r[0]:(r[1],r[2]) for r in summary}
        paid    = totals.get("Paid",    (0,0))
        pending = totals.get("Pending", (0,0))
        self.stat_card(cards, "Paid Records",    paid[0],              T["green"])
        self.stat_card(cards, "Total Collected", f"Rs.{paid[1]:,.0f}", T["blue"])
        self.stat_card(cards, "Pending Records", pending[0],           T["orange"])
        self.stat_card(cards, "Pending Amount",  f"Rs.{pending[1]:,.0f}", T["red"])

        ctrl     = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,6))
        filt_var = tk.StringVar(value="All")
        ttk.Combobox(ctrl, textvariable=filt_var,
                     values=["All","Paid","Pending"],
                     width=10, state="readonly").pack(side="left", padx=(0,8))

        def reload_fees(*_):
            rows = models.get_fees()
            fv   = filt_var.get()
            if fv != "All":
                rows = [r for r in rows if r[6] == fv]
            for item in self.fees_tree.get_children():
                self.fees_tree.delete(item)
            for i, r in enumerate(rows):
                self.fees_tree.insert("","end", values=r,
                                       tags=("paid" if r[6]=="Paid" else "pending",))

        filt_var.trace("w", reload_fees)
        self.action_btn(ctrl, "📤 Export", T["blue"],
                         lambda: self.export_to_csv(
                             ["ID","Name","Type","Amount","Due","Paid","Status","Receipt"],
                             [self.fees_tree.item(i,"values")
                              for i in self.fees_tree.get_children()],
                             "fees_export.csv"))

        cols = ("ID","Student","Fee Type","Amount","Due Date","Paid Date","Status","Receipt")
        self.fees_tree = self.make_table(self.content, cols, [],
                                          [35,140,100,70,80,80,65,90], height=12)
        self.fees_tree.tag_configure("paid",    background="#4caf5018")
        self.fees_tree.tag_configure("pending", background="#f4433618")
        reload_fees()

        act = tk.Frame(self.content, bg=T["bg"])
        act.pack(fill="x", padx=18, pady=4)
        self.f_status = self.status_bar(act)

        def mark_paid():
            sel = self.fees_tree.focus()
            if not sel:
                messagebox.showwarning("No Selection","Select a fee record."); return
            vals = self.fees_tree.item(sel,"values")
            if vals[6] == "Paid":
                messagebox.showinfo("Already Paid","Already marked as paid."); return
            receipt = models.mark_fee_paid(int(vals[0]))
            self.set_status(self.f_status, f"Marked paid! Receipt: {receipt}")
            reload_fees()

        self.action_btn(act, "✅ Mark as Paid", T["green"], mark_paid)

    # ── Assignments (all roles) ────────────────────────────────────────────────

    def tab_assignments(self):
        T = self.T
        self.page_title("Assignments",
                        "View assignments" if self.is_student()
                        else "Post and track assignments")

        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,6))
        if not self.is_student():
            self.action_btn(ctrl, "+ Post Assignment", T["green"],
                             self._add_assignment_form)

        cols = ("ID","Title","Subject","Description","Due Date","Posted By","Posted On")
        self.make_table(self.content, cols, models.get_assignments(),
                         [35,150,100,200,80,120,90], height=16)

    def _add_assignment_form(self):
        T   = self.T
        win = tk.Toplevel(self.root)
        win.title("Post Assignment")
        win.geometry("420x340")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="Post New Assignment",
                 font=("Helvetica", 13,"bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16,10))
        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=8)
        form.pack(fill="both", expand=True)
        fields = {}
        self.input_row(form,"Title","title",fields,width=28)
        self.input_row(form,"Subject","subject",fields,is_combo=True,
                       values=["Mathematics","Physics","Programming","English"],width=20)
        self.input_row(form,"Due Date","due",fields,width=14)
        tk.Label(form, text="Description:", bg=T["surf"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(anchor="w", pady=(6,2))
        desc = tk.Text(form, height=4, bg=T["bg"], fg=T["text"],
                       font=("Helvetica", 10), relief="flat",
                       highlightthickness=1, highlightbackground=T["accent"])
        desc.pack(fill="x")

        def save():
            models.add_assignment(
                fields["title"].get().strip(), fields["subject"].get(),
                desc.get("1.0","end").strip(),
                fields["due"].get().strip(), self.user["email"])
            win.destroy()
            self.tab_assignments()

        tk.Button(win, text="📌 Post", bg=T["accent"], fg="white",
                  font=("Helvetica", 10,"bold"), relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=save).pack(pady=10)

    # ── Exams (all roles — view; admin/faculty — add) ──────────────────────────

    def tab_exams(self):
        T = self.T
        self.page_title("Exam Schedule",
                        "View upcoming exams" if self.is_student()
                        else "Schedule and manage exams")

        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,6))
        if not self.is_student():
            self.action_btn(ctrl, "+ Schedule Exam", T["green"], self._add_exam_form)

        cols = ("ID","Exam Name","Subject","Course","Date","Start","End","Room","Max Marks")
        self.make_table(self.content, cols, models.get_exams(),
                         [35,140,110,100,80,60,60,70,70], height=16)

    def _add_exam_form(self):
        T   = self.T
        win = tk.Toplevel(self.root)
        win.title("Schedule Exam")
        win.geometry("380x380")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="Schedule New Exam",
                 font=("Helvetica", 13,"bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16,10))
        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=8)
        form.pack(fill="both", expand=True)
        fields = {}
        self.input_row(form,"Exam Name","name",fields,width=24)
        self.input_row(form,"Subject","subject",fields,is_combo=True,
                       values=["Mathematics","Physics","Programming","English"],width=20)
        self.input_row(form,"Course","course",fields,is_combo=True,
                       values=["B.Tech CSE","B.Tech ECE","MBA","B.Sc CS"],width=20)
        self.input_row(form,"Exam Date","date",fields,width=14)
        self.input_row(form,"Start Time","start",fields,width=10)
        self.input_row(form,"End Time","end",fields,width=10)
        self.input_row(form,"Room","room",fields,width=10)
        self.input_row(form,"Max Marks","max_marks",fields,width=8)

        def save():
            try: mm = float(fields["max_marks"].get() or 100)
            except ValueError: mm = 100
            models.add_exam(fields["name"].get().strip(), fields["subject"].get(),
                            fields["course"].get(), fields["date"].get().strip(),
                            fields["start"].get().strip(), fields["end"].get().strip(),
                            fields["room"].get().strip(), mm)
            win.destroy()
            self.tab_exams()

        tk.Button(win, text="📅 Schedule", bg=T["accent"], fg="white",
                  font=("Helvetica", 10,"bold"), relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=save).pack(pady=10)

    # ── Library (all roles — view; admin — add) ────────────────────────────────

    def tab_library(self):
        T = self.T
        self.page_title("Library", "Book inventory and issue tracking")

        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,6))
        if self.is_admin():
            self.action_btn(ctrl, "+ Add Book", T["green"], self._add_book_form)

        cols = ("ID","Title","Author","ISBN","Student","Issued","Due","Returned","Status")
        tree = self.make_table(self.content, cols, models.get_library(),
                                [35,180,120,80,120,80,80,80,70], height=16)
        for item in tree.get_children():
            vals = tree.item(item,"values")
            tag  = "issued" if vals[8]=="Issued" else "avail"
            tree.tag_configure("issued", background="#2196f318")
            tree.tag_configure("avail",  background="#4caf5018")
            tree.item(item, tags=(tag,))

    def _add_book_form(self):
        T   = self.T
        win = tk.Toplevel(self.root)
        win.title("Add Book")
        win.geometry("360x240")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="Add New Book",
                 font=("Helvetica", 13,"bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16,10))
        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=8)
        form.pack(fill="both", expand=True)
        fields = {}
        self.input_row(form,"Book Title","title",fields,width=28)
        self.input_row(form,"Author","author",fields,width=24)
        self.input_row(form,"ISBN","isbn",fields,width=18)

        def save():
            models.add_book(fields["title"].get().strip(),
                            fields["author"].get().strip(),
                            fields["isbn"].get().strip())
            win.destroy()
            self.tab_library()

        tk.Button(win, text="📚 Add Book", bg=T["accent"], fg="white",
                  font=("Helvetica", 10,"bold"), relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=save).pack(pady=10)

    # ── Notifications (all roles) ──────────────────────────────────────────────

    def tab_notifications(self):
        T = self.T
        self.page_title("Notifications & Alerts")

        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,6))
        if not self.is_student():
            self.action_btn(ctrl, "+ New Notification", T["green"],
                             self._add_notif_form)

        notifs = models.get_notifications(self.user["role"])
        rows   = [(n[0], n[1], n[2][:60], n[3], n[4], n[5], n[6][:10],
                   "Yes" if n[7] else "No") for n in notifs]
        tree = self.make_table(
            self.content,
            ("ID","Title","Message","Type","Target","Created By","Date","Read"),
            rows, [35,140,250,60,65,120,80,40], height=16)
        type_bg = {"info":"#2196f318","warning":"#ff980018","error":"#f4433618"}
        for item in tree.get_children():
            vals = tree.item(item,"values")
            bg   = type_bg.get(vals[3],"")
            if bg:
                tree.tag_configure(f"nt_{item}", background=bg)
                tree.item(item, tags=(f"nt_{item}",))

    def _add_notif_form(self):
        T   = self.T
        win = tk.Toplevel(self.root)
        win.title("New Notification")
        win.geometry("420x360")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="Send Notification",
                 font=("Helvetica", 13,"bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16,10))
        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=8)
        form.pack(fill="both", expand=True)
        fields = {}
        self.input_row(form,"Title","title",fields,width=28)
        self.input_row(form,"Type","type",fields,is_combo=True,
                       values=["info","warning","error"],width=12)
        self.input_row(form,"Target Role","target",fields,is_combo=True,
                       values=["all","student","faculty","admin"],width=12)
        tk.Label(form, text="Message:", bg=T["surf"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(anchor="w", pady=(6,2))
        msg_box = tk.Text(form, height=5, bg=T["bg"], fg=T["text"],
                          font=("Helvetica", 10), relief="flat",
                          highlightthickness=1, highlightbackground=T["accent"])
        msg_box.pack(fill="x")

        def save():
            models.add_notification(
                fields["title"].get().strip(),
                msg_box.get("1.0","end").strip(),
                fields["type"].get(), fields["target"].get(),
                self.user["email"])
            win.destroy()
            self.tab_notifications()

        tk.Button(win, text="📢 Send", bg=T["accent"], fg="white",
                  font=("Helvetica", 10,"bold"), relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=save).pack(pady=10)

    # ── Messages (all roles) ───────────────────────────────────────────────────

    def tab_messages(self):
        T = self.T
        self.page_title("Internal Messages")

        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,6))
        self.action_btn(ctrl, "✉ Compose", T["accent"], self._compose_message)

        msgs = models.get_messages(self.user["name"])
        rows = [(m[0],m[1],m[2],m[3],
                 m[4][:50]+"..." if len(m[4])>50 else m[4],
                 m[5][:16], "Yes" if m[6] else "No") for m in msgs]
        tree = self.make_table(
            self.content,
            ("ID","From","To","Subject","Message","Sent At","Read"),
            rows, [35,120,120,150,250,100,40], height=16)
        for item in tree.get_children():
            if tree.item(item,"values")[6] == "No":
                tree.tag_configure(f"unread_{item}", background="#6c63ff15")
                tree.item(item, tags=(f"unread_{item}",))

    def _compose_message(self):
        T     = self.T
        win   = tk.Toplevel(self.root)
        win.title("Compose Message")
        win.geometry("420x360")
        win.configure(bg=T["surf"])
        win.grab_set()

        tk.Label(win, text="New Message",
                 font=("Helvetica", 13,"bold"),
                 bg=T["surf"], fg=T["text"]).pack(pady=(16,10))
        form   = tk.Frame(win, bg=T["surf"], padx=24, pady=8)
        form.pack(fill="both", expand=True)
        fields = {}
        users  = models.get_all_users()
        names  = [u[1] for u in users if u[1] != self.user["name"]]
        self.input_row(form,"To","to",fields,is_combo=True,values=names,width=24)
        self.input_row(form,"Subject","subject",fields,width=28)
        tk.Label(form, text="Message:", bg=T["surf"], fg=T["muted"],
                 font=("Helvetica", 9)).pack(anchor="w", pady=(6,2))
        msg_box = tk.Text(form, height=6, bg=T["bg"], fg=T["text"],
                          font=("Helvetica", 10), relief="flat",
                          highlightthickness=1, highlightbackground=T["accent"])
        msg_box.pack(fill="x")

        def send():
            models.send_message(self.user["name"], fields["to"].get(),
                                fields["subject"].get().strip(),
                                msg_box.get("1.0","end").strip())
            win.destroy()
            messagebox.showinfo("Sent","Message sent successfully!")

        tk.Button(win, text="📤 Send", bg=T["accent"], fg="white",
                  font=("Helvetica", 10,"bold"), relief="flat",
                  padx=18, pady=6, cursor="hand2",
                  command=send).pack(pady=10)

    # ── Users (admin only) ─────────────────────────────────────────────────────

    def tab_users(self):
        if not self.is_admin():
            self.access_denied("Only administrators can manage user accounts.")
            return
        self.page_title("User Accounts", "Admin only")
        cols = ("ID","Name","Email","Role","Created At")
        self.make_table(self.content, cols, models.get_all_users(),
                         [40,180,220,80,130], height=18)

    # ═══════════════════════════════════════════════════════════════════════════
    #  STUDENT-ONLY TABS
    # ═══════════════════════════════════════════════════════════════════════════

    def _no_record_warning(self):
        """Shown when a student account has no matching students table row."""
        T = self.T
        tk.Label(self.content,
                 text="⚠  Your student record was not found in the system.\n"
                      "Please contact the administrator to link your account.",
                 font=("Helvetica", 11), bg=T["bg"], fg=T["orange"],
                 justify="center", wraplength=500).pack(pady=60)

    # ── Student Dashboard ──────────────────────────────────────────────────────

    def _student_dashboard(self):
        T   = self.T
        sid = self.student_record_id
        self.page_title(f"My Dashboard", f"Hello, {self.user['name']}!")

        if not sid:
            self._no_record_warning()
            return

        # Personal stats
        marks  = models.get_marks(sid)
        avg    = round(sum(m[4]/m[5]*100 for m in marks)/len(marks), 1) if marks else 0
        att    = models.get_attendance(student_id=sid)
        total  = len(att)
        present= sum(1 for a in att if a[5]=="Present")
        att_pct= round(present/total*100, 1) if total else 0
        fees   = models.get_fees(sid)
        pending= sum(1 for f in fees if f[6]=="Pending")

        cards = tk.Frame(self.content, bg=T["bg"])
        cards.pack(fill="x", padx=14, pady=(0,8))
        self.stat_card(cards, "Avg Score %",    f"{avg}%",    T["accent"])
        self.stat_card(cards, "Attendance %",   f"{att_pct}%",T["green"] if att_pct>=75 else T["red"])
        self.stat_card(cards, "Subjects",        len(set(m[2] for m in marks)), T["blue"])
        self.stat_card(cards, "Pending Fees",    pending,      T["orange"])

        # Attendance alert
        if att_pct > 0 and att_pct < 75:
            alert = tk.Frame(self.content, bg="#f4433620", padx=14, pady=8)
            alert.pack(fill="x", padx=14, pady=(0,8))
            tk.Label(alert, text=f"⚠  Low Attendance Warning: {att_pct}%  — Minimum required is 75%",
                     bg="#f4433620", fg=T["red"],
                     font=("Helvetica", 10, "bold")).pack()

        # Grade distribution for this student
        if marks:
            chart_row = tk.Frame(self.content, bg=T["bg"])
            chart_row.pack(fill="x", padx=14, pady=(0,8))
            grade_data = {}
            for m in marks:
                grade_data[m[6]] = grade_data.get(m[6], 0) + 1
            self.mini_bar_chart(chart_row, list(grade_data.items()), "My Grade Distribution")

            # Subject-wise average
            subj_avg = {}
            for m in marks:
                subj_avg.setdefault(m[2], []).append(m[4]/m[5]*100)
            subj_data = [(s, round(sum(v)/len(v),1)) for s,v in subj_avg.items()]
            self.mini_bar_chart(chart_row, subj_data, "Subject Avg %")

        # Recent notifications
        self.page_title("Recent Notifications")
        notifs = models.get_notifications("student")[:5]
        nrows  = [(n[1], n[2][:60], n[3], n[6][:10]) for n in notifs]
        self.make_table(self.content, ("Title","Message","Type","Date"),
                        nrows, [160,300,80,90], height=4)

    # ── My Attendance ──────────────────────────────────────────────────────────

    def tab_my_attendance(self):
        T   = self.T
        sid = self.student_record_id
        self.page_title("My Attendance", "Your personal attendance record")

        if not sid:
            self._no_record_warning()
            return

        att    = models.get_attendance(student_id=sid)
        total  = len(att)
        present= sum(1 for a in att if a[5]=="Present")
        absent = total - present
        att_pct= round(present/total*100,1) if total else 0

        # Summary cards
        cards = tk.Frame(self.content, bg=T["bg"])
        cards.pack(fill="x", padx=14, pady=(0,8))
        self.stat_card(cards, "Total Classes", total,   T["accent"])
        self.stat_card(cards, "Present",       present, T["green"])
        self.stat_card(cards, "Absent",        absent,  T["red"])
        self.stat_card(cards, "Attendance %",  f"{att_pct}%",
                       T["green"] if att_pct>=75 else T["red"])

        # Alert
        if total > 0 and att_pct < 75:
            alert = tk.Frame(self.content, bg="#f4433620", padx=14, pady=8)
            alert.pack(fill="x", padx=14, pady=(0,8))
            tk.Label(alert,
                     text=f"⚠  Your attendance is {att_pct}% — below the required 75%.",
                     bg="#f4433620", fg=T["red"],
                     font=("Helvetica", 10,"bold")).pack()

        # Filter by subject
        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,6))
        tk.Label(ctrl, text="Filter by Subject:", bg=T["bg"],
                 fg=T["muted"], font=("Helvetica",9)).pack(side="left", padx=(0,4))
        subj_var = tk.StringVar(value="All")
        subjects = list(set(a[4] for a in att))
        ttk.Combobox(ctrl, textvariable=subj_var,
                     values=["All"]+subjects,
                     width=16, state="readonly").pack(side="left")

        def reload(*_):
            fv   = subj_var.get()
            rows = [a for a in att if fv=="All" or a[4]==fv]
            for item in self.my_att_tree.get_children():
                self.my_att_tree.delete(item)
            for i, r in enumerate(rows):
                tag = "present" if r[5]=="Present" else "absent"
                self.my_att_tree.insert("","end", values=r, tags=(tag,))

        subj_var.trace("w", reload)

        cols = ("Log ID","Stu ID","Name","Date","Subject","Status","Marked By")
        self.my_att_tree = self.make_table(self.content, cols, [],
                                            [50,60,150,90,100,70,130], height=13)
        self.my_att_tree.tag_configure("present", background="#4caf5015")
        self.my_att_tree.tag_configure("absent",  background="#f4433615")
        reload()

    # ── My Marks ───────────────────────────────────────────────────────────────

    def tab_my_marks(self):
        T   = self.T
        sid = self.student_record_id
        self.page_title("My Marks & Grades", "Your personal academic performance")

        if not sid:
            self._no_record_warning()
            return

        marks  = models.get_marks(sid)
        avg    = round(sum(m[4]/m[5]*100 for m in marks)/len(marks),1) if marks else 0
        best   = max(marks, key=lambda m: m[4]/m[5], default=None)
        worst  = min(marks, key=lambda m: m[4]/m[5], default=None)

        cards = tk.Frame(self.content, bg=T["bg"])
        cards.pack(fill="x", padx=14, pady=(0,8))
        self.stat_card(cards, "Overall Avg %", f"{avg}%", T["accent"])
        self.stat_card(cards, "Total Exams",   len(marks), T["blue"])
        self.stat_card(cards, "Best Subject",
                       best[2] if best else "—", T["green"])
        self.stat_card(cards, "Needs Attention",
                       worst[2] if worst else "—", T["orange"])

        # Charts
        if marks:
            chart_row = tk.Frame(self.content, bg=T["bg"])
            chart_row.pack(fill="x", padx=14, pady=(0,8))
            grade_data = {}
            for m in marks:
                grade_data[m[6]] = grade_data.get(m[6], 0) + 1
            self.mini_bar_chart(chart_row, list(grade_data.items()), "Grade Distribution")
            subj_avg = {}
            for m in marks:
                subj_avg.setdefault(m[2],[]).append(m[4]/m[5]*100)
            self.mini_bar_chart(chart_row,
                                [(s, round(sum(v)/len(v),1)) for s,v in subj_avg.items()],
                                "Subject Average %")

        # Filter by exam type
        ctrl = tk.Frame(self.content, bg=T["bg"])
        ctrl.pack(fill="x", padx=18, pady=(0,4))
        tk.Label(ctrl, text="Filter:", bg=T["bg"], fg=T["muted"],
                 font=("Helvetica",9)).pack(side="left", padx=(0,4))
        filt = tk.StringVar(value="All")
        ttk.Combobox(ctrl, textvariable=filt,
                     values=["All","Internal","External","Practical","Assignment"],
                     width=14, state="readonly").pack(side="left")

        def reload(*_):
            fv   = filt.get()
            rows = [m for m in marks if fv=="All" or m[3]==fv]
            for item in self.my_marks_tree.get_children():
                self.my_marks_tree.delete(item)
            for i, r in enumerate(rows):
                pct = round(r[4]/r[5]*100,1)
                self.my_marks_tree.insert("","end",
                                           values=(*r, f"{pct}%"),
                                           tags=("odd" if i%2==0 else "even",))

        filt.trace("w", reload)

        mcols = ("ID","Name","Subject","Exam Type","Marks","Max","Grade","Semester","Score%")
        self.my_marks_tree = self.make_table(self.content, mcols, [],
                                              [40,130,110,90,60,50,55,80,60], height=10)
        reload()

    # ── My Fees ────────────────────────────────────────────────────────────────

    def tab_my_fees(self):
        T   = self.T
        sid = self.student_record_id
        self.page_title("My Fees", "Your personal fee and payment status")

        if not sid:
            self._no_record_warning()
            return

        fees    = models.get_fees(sid)
        paid    = [f for f in fees if f[6]=="Paid"]
        pending = [f for f in fees if f[6]=="Pending"]
        total_paid    = sum(f[3] for f in paid)
        total_pending = sum(f[3] for f in pending)

        cards = tk.Frame(self.content, bg=T["bg"])
        cards.pack(fill="x", padx=14, pady=(0,8))
        self.stat_card(cards, "Paid",           len(paid),                  T["green"])
        self.stat_card(cards, "Amount Paid",    f"Rs.{total_paid:,.0f}",    T["blue"])
        self.stat_card(cards, "Pending",        len(pending),               T["orange"])
        self.stat_card(cards, "Amount Due",     f"Rs.{total_pending:,.0f}", T["red"])

        if pending:
            alert = tk.Frame(self.content, bg="#ff980020", padx=14, pady=8)
            alert.pack(fill="x", padx=14, pady=(0,8))
            tk.Label(alert,
                     text=f"⚠  You have {len(pending)} pending fee(s) totalling "
                          f"Rs.{total_pending:,.0f}. Please contact the admin to pay.",
                     bg="#ff980020", fg=T["orange"],
                     font=("Helvetica", 10,"bold")).pack()

        cols = ("ID","Student","Fee Type","Amount","Due Date","Paid Date","Status","Receipt")
        tree = self.make_table(self.content, cols, fees,
                                [35,140,100,70,80,80,65,90], height=12)
        tree.tag_configure("paid",    background="#4caf5018")
        tree.tag_configure("pending", background="#f4433618")
        for item in tree.get_children():
            vals = tree.item(item,"values")
            tree.item(item, tags=("paid" if vals[6]=="Paid" else "pending",))

    # ═══════════════════════════════════════════════════════════════════════════
    #  THEME + LOGOUT
    # ═══════════════════════════════════════════════════════════════════════════

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name=="dark" else "dark"
        self.T          = THEMES[self.theme_name]
        self.root.configure(bg=self.T["bg"])
        for w in self.root.winfo_children():
            w.destroy()
        self.build_layout()
        self.show_tab("dashboard")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.on_logout()