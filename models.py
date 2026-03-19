from database import connect, hash_password
import datetime

# ── Auth ─────────────────────────────────────────────────────────────────────

def register_user(name, email, password, role="student"):
    conn = connect()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                  (name, email, hash_password(password), role))
        conn.commit()
        return True, "Account created successfully!"
    except Exception as e:
        return False, "Email already registered."
    finally:
        conn.close()

def login_user(email, password):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id,name,email,role FROM users WHERE email=? AND password=?",
              (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    if user:
        return True, {"id": user[0], "name": user[1], "email": user[2], "role": user[3]}
    return False, "Invalid email or password."

def get_all_users():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id,name,email,role,created_at FROM users ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ── Students ──────────────────────────────────────────────────────────────────

def add_student(data):
    conn = connect()
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO students
            (student_id,name,email,phone,dob,gender,address,course,year,section,guardian_name,guardian_phone)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", data)
        conn.commit()
        return True, "Student added!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_students():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM students ORDER BY id")
    rows = c.fetchall()
    conn.close()
    return rows

def get_student(sid):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (sid,))
    row = c.fetchone()
    conn.close()
    return row

def update_student(sid, data):
    conn = connect()
    c = conn.cursor()
    c.execute("""UPDATE students SET student_id=?,name=?,email=?,phone=?,dob=?,gender=?,
        address=?,course=?,year=?,section=?,guardian_name=?,guardian_phone=? WHERE id=?""",
              (*data, sid))
    conn.commit()
    conn.close()

def delete_student(sid):
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit()
    conn.close()

def search_students(q):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE name LIKE ? OR student_id LIKE ? OR course LIKE ?",
              (f"%{q}%", f"%{q}%", f"%{q}%"))
    rows = c.fetchall()
    conn.close()
    return rows

# ── Attendance ────────────────────────────────────────────────────────────────

def mark_attendance(student_id, date, subject, status, marked_by):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM attendance WHERE student_id=? AND date=? AND subject=?",
              (student_id, date, subject))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE attendance SET status=? WHERE id=?", (status, existing[0]))
    else:
        c.execute("INSERT INTO attendance (student_id,date,subject,status,marked_by) VALUES (?,?,?,?,?)",
                  (student_id, date, subject, status, marked_by))
    conn.commit()
    conn.close()

def get_attendance(student_id=None, date=None, subject=None):
    conn = connect()
    c = conn.cursor()
    query = """SELECT a.id, s.student_id, s.name, a.date, a.subject, a.status, a.marked_by
               FROM attendance a JOIN students s ON a.student_id=s.id WHERE 1=1"""
    params = []
    if student_id:
        query += " AND a.student_id=?"
        params.append(student_id)
    if date:
        query += " AND a.date=?"
        params.append(date)
    if subject:
        query += " AND a.subject=?"
        params.append(subject)
    query += " ORDER BY a.date DESC"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

def get_attendance_summary():
    conn = connect()
    c = conn.cursor()
    c.execute("""SELECT s.id, s.name, s.course,
        COUNT(*) as total,
        SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present,
        ROUND(SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END)*100.0/COUNT(*),1) as pct
        FROM attendance a JOIN students s ON a.student_id=s.id
        GROUP BY s.id ORDER BY pct""")
    rows = c.fetchall()
    conn.close()
    return rows

# ── Marks ─────────────────────────────────────────────────────────────────────

def add_marks(student_id, subject, exam_type, marks, max_marks, semester):
    grade = "A+" if marks/max_marks>=0.9 else "A" if marks/max_marks>=0.8 else \
            "B" if marks/max_marks>=0.7 else "C" if marks/max_marks>=0.6 else \
            "D" if marks/max_marks>=0.5 else "F"
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM marks WHERE student_id=? AND subject=? AND exam_type=? AND semester=?",
              (student_id, subject, exam_type, semester))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE marks SET marks_obtained=?,max_marks=?,grade=? WHERE id=?",
                  (marks, max_marks, grade, existing[0]))
    else:
        c.execute("INSERT INTO marks (student_id,subject,exam_type,marks_obtained,max_marks,semester,grade) VALUES (?,?,?,?,?,?,?)",
                  (student_id, subject, exam_type, marks, max_marks, semester, grade))
    conn.commit()
    conn.close()

def get_marks(student_id=None):
    conn = connect()
    c = conn.cursor()
    if student_id:
        c.execute("""SELECT m.id, s.name, m.subject, m.exam_type, m.marks_obtained,
            m.max_marks, m.grade, m.semester FROM marks m
            JOIN students s ON m.student_id=s.id WHERE m.student_id=?""", (student_id,))
    else:
        c.execute("""SELECT m.id, s.name, m.subject, m.exam_type, m.marks_obtained,
            m.max_marks, m.grade, m.semester FROM marks m
            JOIN students s ON m.student_id=s.id ORDER BY s.name""")
    rows = c.fetchall()
    conn.close()
    return rows

def get_gpa_summary():
    conn = connect()
    c = conn.cursor()
    c.execute("""SELECT s.id, s.name, s.course,
        ROUND(AVG(m.marks_obtained*100.0/m.max_marks),1) as avg_pct,
        COUNT(DISTINCT m.subject) as subjects
        FROM marks m JOIN students s ON m.student_id=s.id
        GROUP BY s.id ORDER BY avg_pct DESC""")
    rows = c.fetchall()
    conn.close()
    return rows

# ── Timetable ─────────────────────────────────────────────────────────────────

def get_timetable(course=None):
    conn = connect()
    c = conn.cursor()
    if course:
        c.execute("SELECT * FROM timetable WHERE course=? ORDER BY day,period", (course,))
    else:
        c.execute("SELECT * FROM timetable ORDER BY course,day,period")
    rows = c.fetchall()
    conn.close()
    return rows

def add_timetable(course, day, period, time_slot, subject, faculty, room):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO timetable (course,day,period,time_slot,subject,faculty,room) VALUES (?,?,?,?,?,?,?)",
              (course, day, period, time_slot, subject, faculty, room))
    conn.commit()
    conn.close()

# ── Fees ─────────────────────────────────────────────────────────────────────

def get_fees(student_id=None):
    conn = connect()
    c = conn.cursor()
    if student_id:
        c.execute("""SELECT f.id, s.name, f.fee_type, f.amount, f.due_date,
            f.paid_date, f.status, f.receipt_no FROM fees f
            JOIN students s ON f.student_id=s.id WHERE f.student_id=?""", (student_id,))
    else:
        c.execute("""SELECT f.id, s.name, f.fee_type, f.amount, f.due_date,
            f.paid_date, f.status, f.receipt_no FROM fees f
            JOIN students s ON f.student_id=s.id ORDER BY f.status,s.name""")
    rows = c.fetchall()
    conn.close()
    return rows

def mark_fee_paid(fee_id):
    import random, string
    receipt = "RCP" + "".join(random.choices(string.digits, k=6))
    conn = connect()
    c = conn.cursor()
    c.execute("UPDATE fees SET status='Paid', paid_date=?, receipt_no=? WHERE id=?",
              (str(datetime.date.today()), receipt, fee_id))
    conn.commit()
    conn.close()
    return receipt

def get_fee_summary():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*), SUM(amount) FROM fees GROUP BY status")
    rows = c.fetchall()
    conn.close()
    return rows

# ── Assignments ───────────────────────────────────────────────────────────────

def get_assignments():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM assignments ORDER BY due_date")
    rows = c.fetchall()
    conn.close()
    return rows

def add_assignment(title, subject, desc, due_date, posted_by):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO assignments (title,subject,description,due_date,posted_by) VALUES (?,?,?,?,?)",
              (title, subject, desc, due_date, posted_by))
    conn.commit()
    conn.close()

def submit_assignment(assignment_id, student_id):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO submissions (assignment_id,student_id) VALUES (?,?)",
              (assignment_id, student_id))
    conn.commit()
    conn.close()

# ── Notifications ─────────────────────────────────────────────────────────────

def get_notifications(role="all"):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM notifications WHERE target_role=? OR target_role='all' ORDER BY created_at DESC",
              (role,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_notification(title, message, ntype, target_role, created_by):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO notifications (title,message,type,target_role,created_by) VALUES (?,?,?,?,?)",
              (title, message, ntype, target_role, created_by))
    conn.commit()
    conn.close()

# ── Messages ──────────────────────────────────────────────────────────────────

def get_messages(user_name):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM messages WHERE receiver_name=? ORDER BY sent_at DESC", (user_name,))
    rows = c.fetchall()
    conn.close()
    return rows

def send_message(sender, receiver, subject, message):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender_name,receiver_name,subject,message) VALUES (?,?,?,?)",
              (sender, receiver, subject, message))
    conn.commit()
    conn.close()

# ── Library ───────────────────────────────────────────────────────────────────

def get_library():
    conn = connect()
    c = conn.cursor()
    c.execute("""SELECT l.id, l.book_title, l.author, l.isbn,
        COALESCE(s.name,'—') as student, l.issued_date, l.due_date, l.return_date, l.status
        FROM library l LEFT JOIN students s ON l.student_id=s.id ORDER BY l.status,l.book_title""")
    rows = c.fetchall()
    conn.close()
    return rows

def add_book(title, author, isbn):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO library (book_title,author,isbn) VALUES (?,?,?)", (title, author, isbn))
    conn.commit()
    conn.close()

# ── Exams ─────────────────────────────────────────────────────────────────────

def get_exams():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * FROM exams ORDER BY exam_date")
    rows = c.fetchall()
    conn.close()
    return rows

def add_exam(exam_name, subject, course, exam_date, start_time, end_time, room, max_marks):
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO exams (exam_name,subject,course,exam_date,start_time,end_time,room,max_marks) VALUES (?,?,?,?,?,?,?,?)",
              (exam_name, subject, course, exam_date, start_time, end_time, room, max_marks))
    conn.commit()
    conn.close()

# ── Dashboard Stats ────────────────────────────────────────────────────────────

def get_dashboard_stats():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM students WHERE year=1")
    new_students = c.fetchone()[0]
    c.execute("SELECT ROUND(AVG(marks_obtained*100.0/max_marks),1) FROM marks")
    avg_marks = c.fetchone()[0] or 0
    c.execute("SELECT ROUND(AVG(CASE WHEN status='Present' THEN 100.0 ELSE 0 END),1) FROM attendance")
    avg_att = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM fees WHERE status='Pending'")
    pending_fees = c.fetchone()[0]
    c.execute("SELECT SUM(amount) FROM fees WHERE status='Pending'")
    pending_amt = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM notifications WHERE is_read=0")
    unread_notifs = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM assignments")
    total_assignments = c.fetchone()[0]
    conn.close()
    return {
        "total_students": total_students,
        "new_students": new_students,
        "avg_marks": avg_marks,
        "avg_attendance": avg_att,
        "pending_fees": pending_fees,
        "pending_amount": pending_amt,
        "unread_notifications": unread_notifs,
        "total_assignments": total_assignments,
    }

def get_grade_distribution():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT grade, COUNT(*) FROM marks GROUP BY grade ORDER BY grade")
    rows = c.fetchall()
    conn.close()
    return rows

def get_course_distribution():
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
    rows = c.fetchall()
    conn.close()
    return rows