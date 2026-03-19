import sqlite3
import hashlib
import os

DB_PATH = "sms.db"

def connect():
    return sqlite3.connect(DB_PATH)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = connect()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        dob TEXT,
        gender TEXT,
        address TEXT,
        course TEXT,
        year INTEGER DEFAULT 1,
        section TEXT,
        guardian_name TEXT,
        guardian_phone TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        subject TEXT,
        status TEXT DEFAULT 'Present',
        marked_by TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        exam_type TEXT,
        marks_obtained REAL,
        max_marks REAL DEFAULT 100,
        semester TEXT,
        grade TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT,
        day TEXT,
        period INTEGER,
        time_slot TEXT,
        subject TEXT,
        faculty TEXT,
        room TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        fee_type TEXT,
        amount REAL,
        due_date TEXT,
        paid_date TEXT,
        status TEXT DEFAULT 'Pending',
        receipt_no TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        subject TEXT,
        description TEXT,
        due_date TEXT,
        posted_by TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER,
        student_id INTEGER,
        submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        grade TEXT,
        remarks TEXT,
        FOREIGN KEY(assignment_id) REFERENCES assignments(id),
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        type TEXT DEFAULT 'info',
        target_role TEXT DEFAULT 'all',
        created_by TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_name TEXT,
        receiver_name TEXT,
        subject TEXT,
        message TEXT,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS library (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title TEXT,
        author TEXT,
        isbn TEXT,
        student_id INTEGER,
        issued_date TEXT,
        due_date TEXT,
        return_date TEXT,
        status TEXT DEFAULT 'Available',
        FOREIGN KEY(student_id) REFERENCES students(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_name TEXT,
        subject TEXT,
        course TEXT,
        exam_date TEXT,
        start_time TEXT,
        end_time TEXT,
        room TEXT,
        max_marks REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Seed default admin
    admin_pw = hash_password("admin123")
    c.execute("INSERT OR IGNORE INTO users (name,email,password,role) VALUES (?,?,?,?)",
              ("Administrator", "admin@sms.com", admin_pw, "admin"))

    # Seed sample students
    sample_students = [
        ("STU001","Rahul Sharma","rahul@email.com","9876543210","2003-05-10","Male","123 MG Road","B.Tech CSE",2,"A","Suresh Sharma","9876543211"),
        ("STU002","Priya Singh","priya@email.com","9876543212","2004-02-20","Female","456 Park St","B.Tech ECE",1,"B","Ramesh Singh","9876543213"),
        ("STU003","Aman Verma","aman@email.com","9876543214","2002-11-15","Male","789 Lake View","MBA",3,"A","Vikas Verma","9876543215"),
        ("STU004","Sneha Patel","sneha@email.com","9876543216","2003-08-25","Female","321 Hill Top","B.Sc CS",2,"C","Nilesh Patel","9876543217"),
        ("STU005","Rohan Das","rohan@email.com","9876543218","2004-01-05","Male","654 River Rd","B.Tech CSE",1,"A","Biplab Das","9876543219"),
    ]
    for s in sample_students:
        c.execute("INSERT OR IGNORE INTO students (student_id,name,email,phone,dob,gender,address,course,year,section,guardian_name,guardian_phone) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", s)

    # Seed sample marks
    for sid in range(1, 6):
        for subj in ["Mathematics","Physics","Programming","English"]:
            for etype in ["Internal","External"]:
                import random
                m = round(random.uniform(55, 98), 1)
                mm = 50 if etype == "Internal" else 100
                g = "A+" if m/mm >= 0.9 else "A" if m/mm >= 0.8 else "B" if m/mm >= 0.7 else "C"
                c.execute("INSERT OR IGNORE INTO marks (student_id,subject,exam_type,marks_obtained,max_marks,semester,grade) VALUES (?,?,?,?,?,?,?)",
                          (sid, subj, etype, min(m, mm), mm, "Sem 1", g))

    # Seed attendance
    import datetime
    today = datetime.date.today()
    for sid in range(1, 6):
        for day_offset in range(10):
            d = today - datetime.timedelta(days=day_offset)
            import random
            status = "Present" if random.random() > 0.2 else "Absent"
            c.execute("INSERT OR IGNORE INTO attendance (student_id,date,subject,status,marked_by) VALUES (?,?,?,?,?)",
                      (sid, str(d), "Programming", status, "admin@sms.com"))

    # Seed notifications
    c.execute("INSERT OR IGNORE INTO notifications (title,message,type,target_role,created_by) VALUES (?,?,?,?,?)",
              ("Welcome!", "Welcome to the Student Management System.", "info", "all", "admin@sms.com"))
    c.execute("INSERT OR IGNORE INTO notifications (title,message,type,target_role,created_by) VALUES (?,?,?,?,?)",
              ("Exam Notice", "End semester exams begin on April 10th. Check timetable.", "warning", "all", "admin@sms.com"))

    # Seed timetable
    timetable_data = [
        ("B.Tech CSE","Monday",1,"9:00-10:00","Mathematics","Dr. Sharma","R101"),
        ("B.Tech CSE","Monday",2,"10:00-11:00","Physics","Dr. Gupta","R102"),
        ("B.Tech CSE","Monday",3,"11:00-12:00","Programming","Prof. Mehta","Lab1"),
        ("B.Tech CSE","Tuesday",1,"9:00-10:00","English","Ms. Verma","R103"),
        ("B.Tech CSE","Tuesday",2,"10:00-11:00","Mathematics","Dr. Sharma","R101"),
        ("B.Tech CSE","Wednesday",1,"9:00-10:00","Programming","Prof. Mehta","Lab1"),
        ("B.Tech CSE","Wednesday",2,"10:00-11:00","Physics","Dr. Gupta","R102"),
    ]
    for t in timetable_data:
        c.execute("INSERT OR IGNORE INTO timetable (course,day,period,time_slot,subject,faculty,room) VALUES (?,?,?,?,?,?,?)", t)

    # Seed fees
    for sid in range(1, 6):
        import random
        for ftype, amt in [("Tuition Fee", 50000), ("Library Fee", 2000), ("Lab Fee", 5000)]:
            status = random.choice(["Paid", "Paid", "Pending"])
            c.execute("INSERT OR IGNORE INTO fees (student_id,fee_type,amount,due_date,status,receipt_no) VALUES (?,?,?,?,?,?)",
                      (sid, ftype, amt, "2025-03-31", status, f"RCP{sid:03d}{random.randint(100,999)}" if status=="Paid" else None))

    # Seed assignments
    c.execute("INSERT OR IGNORE INTO assignments (title,subject,description,due_date,posted_by) VALUES (?,?,?,?,?)",
              ("Python Project", "Programming", "Build a CRUD application using Python and SQLite.", "2025-04-01", "admin@sms.com"))
    c.execute("INSERT OR IGNORE INTO assignments (title,subject,description,due_date,posted_by) VALUES (?,?,?,?,?)",
              ("Integration Assignment", "Mathematics", "Solve all problems from Chapter 5.", "2025-03-28", "admin@sms.com"))

    # Seed exams
    c.execute("INSERT OR IGNORE INTO exams (exam_name,subject,course,exam_date,start_time,end_time,room,max_marks) VALUES (?,?,?,?,?,?,?,?)",
              ("Mid Semester Exam", "Mathematics", "B.Tech CSE", "2025-04-10", "10:00", "13:00", "Hall A", 100))
    c.execute("INSERT OR IGNORE INTO exams (exam_name,subject,course,exam_date,start_time,end_time,room,max_marks) VALUES (?,?,?,?,?,?,?,?)",
              ("Lab Practical", "Programming", "B.Tech CSE", "2025-04-12", "09:00", "12:00", "Lab 1", 50))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")