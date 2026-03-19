# 🎓 Student Management System

A full-featured desktop application built with **Python** and **Tkinter** for managing student records, attendance, marks, fees, and more — with a secure login system and role-based access control.

---

## 👩‍💻 Author

| | |
|---|---|
| **Name** | Dasari Nandini |
| **Email** | [dasarinandini08@gmail.com](mailto:dasarinandini08@gmail.com) |
| **GitHub** | [github.com/dasarinandini08-blip](https://github.com/dasarinandini08-blip) |
| **LinkedIn** | [linkedin.com/in/nandini-dasari](https://linkedin.com/in/nandini-dasari) |

---

## 🚀 Getting Started

### Requirements
- Python 3.8 or higher
- No external libraries needed — uses only Python built-ins (`tkinter`, `sqlite3`, `hashlib`, `csv`)

### Run the App
```bash
python run.py
```

### Default Login
| Email | Password | Role |
|---|---|---|
| admin@sms.com | admin123 | Admin |

> You can also create new accounts from the login screen using **"Create Account"**.

---

## 📁 Project Structure

```
Student Management System/
├── run.py              # Entry point — launches the app
├── database.py         # Database setup, all 12 tables, seed data
├── models.py           # All CRUD operations and data functions
├── auth_window.py      # Login and Register screen
└── main_window.py      # Full app UI with all 11 modules
```

> ⚠️ All 5 files **must** be in the same folder. Do not rename them.

---

## ✨ Features

### 🔐 Authentication
- Secure login with SHA-256 password hashing
- Create new account with role selection (Admin / Faculty / Student)
- Window auto-resizes for login vs register form
- Auto-redirect after successful login or logout

### 🎭 Role-Based Access Control

| Feature | Admin | Faculty | Student |
|---|---|---|---|
| Dashboard | ✅ Full stats | ✅ Full stats | ✅ Personal stats only |
| Students | ✅ Full CRUD | ✅ View only | ❌ Blocked |
| Attendance | ✅ Mark & manage | ✅ Mark & manage | ✅ Own records only |
| Marks & Grades | ✅ Add & view all | ✅ Add & view all | ✅ Own marks only |
| Timetable | ✅ Add & view | ✅ Add & view | ✅ View only |
| Fees | ✅ Full control | ❌ Blocked | ✅ Own fees only |
| Assignments | ✅ Post & view | ✅ Post & view | ✅ View only |
| Exam Schedule | ✅ Schedule & view | ✅ Schedule & view | ✅ View only |
| Library | ✅ Add & view | ✅ View | ✅ View only |
| Notifications | ✅ Post & view | ✅ Post & view | ✅ View only |
| Messages | ✅ Send & receive | ✅ Send & receive | ✅ Send & receive |
| User Accounts | ✅ View all | ❌ Blocked | ❌ Blocked |

---

### 📊 Dashboard
- Total students, average attendance %, average marks %, pending fees
- Grade distribution bar chart
- Students by course bar chart
- Recent attendance summary with low attendance (< 75%) highlighted
- Latest notifications preview

### 👨‍🎓 Student Management *(Admin / Faculty)*
- Add, edit, delete student records
- Search by name, student ID, or course
- View full student profile in a popup window
- Store personal info, guardian details, course and section
- Export all records to CSV

### 📋 Attendance Tracking
- **Admin / Faculty:** Mark attendance by date and subject, mark all present in one click, quick mark selected student present or absent
- **Student:** View own attendance with present/absent count, attendance percentage, low attendance warning, filter by subject

### 📝 Marks & Grade Management
- Auto-calculate grade (A+, A, B, C, D, F) based on percentage
- GPA / average score per student with colour-coded performance
- **Admin / Faculty:** Add/update marks for any student, filter and export
- **Student:** View own marks with subject-wise average chart, best and worst subject cards

### 📅 Timetable Management
- Weekly class schedule per course
- **Admin / Faculty:** Add new time slots with faculty and room details
- **Student:** View only

### 💳 Fee Management *(Admin only)*
- Track tuition, library, lab fees per student
- Mark fees as paid — auto-generates receipt number
- Summary cards: total collected, pending amount
- Filter by Paid / Pending status
- Export fee records to CSV
- **Student:** View own fee status with pending amount alert

### 📌 Assignments
- Post assignments with subject, description, due date
- **Admin / Faculty:** Post new assignments
- **Student:** View all assignments

### 📃 Exam Schedule
- Schedule exams with date, time, room, max marks
- **Admin / Faculty:** Add new exams
- **Student:** View upcoming exams

### 📚 Library Management
- Book inventory with author and ISBN
- Track issued and available books
- Colour-coded: blue = Issued, green = Available
- **Admin:** Add new books

### 🔔 Notifications & Alerts
- Send notifications targeted by role (All / Student / Faculty / Admin)
- Types: Info, Warning, Error — each colour-coded
- Unread count badge shown in the top bar
- **Student:** View only

### 💬 Internal Messages
- Send messages to any registered user
- Inbox view with unread message highlighting
- Available to all roles

---

## 🗄️ Database

The app uses **SQLite** — no installation needed. The database file `sms.db` is auto-created in the same folder on first run.

### Tables

| Table | Purpose |
|---|---|
| users | Login accounts and roles |
| students | Student personal and academic info |
| attendance | Daily subject-wise attendance records |
| marks | Subject marks and calculated grades |
| timetable | Weekly class schedule |
| fees | Fee records and payment status |
| assignments | Posted assignments |
| submissions | Assignment submission tracking |
| notifications | System alerts by role |
| messages | Internal user-to-user messages |
| library | Book inventory and issue tracking |
| exams | Exam schedule |

---

## 🎨 UI Features

- **Dark / Light mode** toggle
- Sidebar navigation with active tab highlight
- Role badge in top bar (🔴 Admin · 🟠 Faculty · 🟢 Student)
- Alternating row colours in all tables
- Popup forms for add / edit operations
- Status messages with auto-clear
- Notification badge counter in top bar
- Low attendance and pending fee alerts

---

## 🛠️ Tools & Technologies

| Tool | Purpose |
|---|---|
| Python 3 | Core programming language |
| Tkinter | Desktop GUI framework |
| SQLite3 | Local database (built-in) |
| Hashlib | SHA-256 password hashing |
| CSV module | Data export |
| Datetime | Date and time handling |

---

## 📌 Notes

- The app seeds **5 sample students** with marks, attendance, and fees automatically on first run
- Password must be at least **6 characters** when creating a new account
- Attendance below **75%** is highlighted in red on the dashboard and attendance pages
- All CSV exports are saved to your home directory (`C:\Users\YourName\` on Windows)
- Students must have a matching email in the `students` table to see their personal data — contact admin if not linked

---

## 📷 App Flow

```
 run.py
   └── Login Screen (auth_window.py)
         ├── Sign In
         └── Create Account
               └── Main App (main_window.py)
                     │
                     ├── ADMIN ─────────────────────────────────────────
                     │     ├── Dashboard       (full stats + charts)
                     │     ├── Students        (add, edit, delete, export)
                     │     ├── Attendance      (mark all, quick mark)
                     │     ├── Marks & Grades  (add marks, GPA, export)
                     │     ├── Timetable       (add slots, view schedule)
                     │     ├── Fees            (payments, receipts)
                     │     ├── Assignments     (post, view)
                     │     ├── Exam Schedule   (schedule, view)
                     │     ├── Library         (add books, track issues)
                     │     ├── Notifications   (post alerts by role)
                     │     ├── Messages        (compose, inbox)
                     │     └── User Accounts   (view all users)
                     │
                     ├── FACULTY ───────────────────────────────────────
                     │     ├── Dashboard       (full stats + charts)
                     │     ├── Students        (view only)
                     │     ├── Attendance      (mark attendance)
                     │     ├── Marks & Grades  (add + view marks)
                     │     ├── Timetable       (add + view)
                     │     ├── Assignments     (post + view)
                     │     ├── Exam Schedule   (schedule + view)
                     │     ├── Library         (view only)
                     │     ├── Notifications   (post + view)
                     │     └── Messages        (compose, inbox)
                     │
                     └── STUDENT ───────────────────────────────────────
                           ├── My Dashboard    (personal stats + alerts)
                           ├── My Attendance   (own records + % warning)
                           ├── My Marks        (own grades + subject chart)
                           ├── Timetable       (view only)
                           ├── My Fees         (own payments + due alert)
                           ├── Assignments     (view only)
                           ├── Exam Schedule   (view only)
                           ├── Library         (view only)
                           ├── Notifications   (view only)
                           └── Messages        (compose, inbox)
```

---

## 📜 License

This project is developed for educational purposes.

---

*Built by **Dasari Nandini** — [GitHub](https://github.com/dasarinandini08-blip) · [LinkedIn](https://linkedin.com/in/nandini-dasari) · [dasarinandini08@gmail.com](mailto:dasarinandini08@gmail.com)*