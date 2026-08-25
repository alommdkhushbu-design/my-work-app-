import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'admin_super_secret_key'

SECURITY_PIN = "137955"  # আপনার নির্ধারিত সিকিউরিটি পিন

def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    
    # ইউজার টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT, 
                  role TEXT,
                  gmail TEXT,
                  gmail_pass TEXT,
                  mobile TEXT,
                  payment_method TEXT,
                  payment_number TEXT)''')
    
    # হাজিরা টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS attendance 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, check_in TEXT, check_out TEXT, date TEXT)''')
    
    # জিমেইল কাজের হিসাব টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS gmail_work 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, gmail_used TEXT, work_count INTEGER, comment_used TEXT, date TEXT)''')

    # পেমেন্ট হিস্ট্রি টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, month_year TEXT, amount REAL, payment_date TEXT)''')

    # এডমিন প্রিসেট কমেন্ট ও কনফিগারেশন টেবিল
    c.execute('''CREATE TABLE IF NOT EXISTS system_config 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, preset_comment TEXT)''')
    
    # ডিফল্ট এডমিন তৈরি (Khushbu23 / 01751947523)
    c.execute("SELECT * FROM users WHERE username='Khushbu23'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES ('Khushbu23', '01751947523', 'admin')")
    
    # ডিফল্ট কমেন্ট সেট
    c.execute("SELECT * FROM system_config")
    if not c.fetchone():
        c.execute("INSERT INTO system_config (preset_comment) VALUES ('Great service! Highly recommended.')")

    conn.commit()
    conn.close()

init_db()

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure Staff & Task System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 15px; background: #eef2f3; }
        .card { background: white; padding: 20px; border-radius: 8px; max-width: 850px; margin: 0 auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input, select, textarea { width: 93%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px; }
        button, .btn-link { background: #007bff; color: white; border: none; padding: 10px; width: 97%; cursor: pointer; border-radius: 4px; font-weight: bold; margin-top: 5px; text-decoration: none; display: inline-block; text-align: center; }
        .btn-danger { background: #dc3545; }
        .btn-success { background: #28a745; }
        .btn-warning { background: #ffc107; color: black; }
        .stats-box { display: flex; gap: 10px; margin-bottom: 15px; }
        .stat-card { background: #007bff; color: white; padding: 10px; border-radius: 6px; flex: 1; text-align: center; }
        table { width: 100%; margin-top: 15px; border-collapse: collapse; font-size: 13px; overflow-x: auto; display: block; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background: #343a40; color: white; }
        .comment-box { background: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="card">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for msg in messages %}<p style="color: blue; text-align: center;"><b>{{ msg }}</b></p>{% endfor %}
          {% endif %}
        {% endwith %}

        {% if not session.get('user') %}
            <h2 style="text-align: center;">Staff & Admin Login</h2>
            <form method="POST" action="/login">
                <input type="text" name="username" placeholder="Username (Khushbu23)" required><br>
                <input type="password" name="password" placeholder="Password (01751947523)" required><br>
                <button type="submit">Login</button>
            </form>
        {% else %}
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>{{ session['user'] }} ({{ session['role'] | upper }})</h3>
                <a href="/logout" style="color: red; font-weight: bold;">Logout</a>
            </div>
            <hr>

            {% if session['role'] == 'admin' %}
                <div class="stats-box">
                    <div class="stat-card">
                        <h3>{{ total_staff }}</h3>
                        <p>মোট স্টাফ</p>
                    </div>
                </div>

                <h4>কাজের কমেন্ট (Comment) সেট বা আপডেট করুন</h4>
                <form method="POST" action="/update-preset-comment">
                    <textarea name="preset_comment" rows="3" placeholder="স্টাফদের জন্য কমেন্ট লিখুন..." required>{{ preset_comment }}</textarea><br>
                    <button type="submit" class="btn-warning">Update Default Comment</button>
                </form>

                <hr>
                <h4>নতুন স্টাফ ও পেমেন্ট তথ্য যোগ করুন</h4>
                <form method="POST" action="/create-staff">
                    <input type="text" name="staff_user" placeholder="কাজের আইডি (Username)" required><br>
                    <input type="password" name="staff_pass" placeholder="কাজের পাসওয়ার্ড" required><br>
                    <input type="email" name="gmail" placeholder="জিমেইল এড্রেস (Gmail)" required><br>
                    <input type="text" name="gmail_pass" placeholder="জিমেইল পাসওয়ার্ড" required><br>
                    <input type="text" name="mobile" placeholder="মোবাইল নম্বর" required><br>
                    <select name="payment_method">
                        <option value="bKash">বিকাশ (bKash)</option>
                        <option value="Nagad">নগদ (Nagad)</option>
                        <option value="Rocket">রকেট (Rocket)</option>
                        <option value="Upay">উপায় (Upay)</option>
                        <option value="Bank">ব্যাংক (Bank Account)</option>
                    </select><br>
                    <input type="text" name="payment_number" placeholder="পেমেন্ট নম্বর / ব্যাংক একাউন্ট বিবরণ" required><br>
                    <button type="submit" class="btn-success">Save Staff Profile</button>
                </form>

                <hr>
                <h4>স্টাফ ডিলিট করুন (সিকিউরিটি পিন প্রয়োজন)</h4>
                <form method="POST" action="/delete-staff">
                    <select name="staff_id" required>
                        <option value="">ডিলিট করার জন্য স্টাফ সিলেক্ট করুন</option>
                        {% for s in staff_list %}
                        <option value="{{ s[0] }}">{{ s[1] }} ({{ s[4] }})</option>
                        {% endfor %}
                    </select><br>
                    <input type="password" name="security_pin" placeholder="সিকিউরিটি পিন দিন (137955)" required><br>
                    <button type="submit" class="btn-danger">Delete Staff Profile</button>
                </form>

                <hr>
                <h4>মাসিক পেমেন্ট রেকর্ড যুক্ত করুন</h4>
                <form method="POST" action="/add-payment">
                    <select name="staff_name" required>
                        <option value="">স্টাফ নির্বাচন করুন</option>
                        {% for s in staff_list %}
                        <option value="{{ s[1] }}">{{ s[1] }}</option>
                        {% endfor %}
                    </select><br>
                    <input type="text" name="month_year" placeholder="মাস ও বছর (যেমন: August 2026)" required><br>
                    <input type="number" step="0.01" name="amount" placeholder="পেমেন্ট এর পরিমাণ (টাকা)" required><br>
                    <button type="submit">Save Payment</button>
                </form>

                <hr>
                <h4>জিমেইল অনুযায়ী কাজের জমা লিস্ট</h4>
                <table>
                    <tr>
                        <th>Staff</th>
                        <th>Gmail Used</th>
                        <th>Work Count</th>
                        <th>Comment Used</th>
                        <th>Date</th>
                    </tr>
                    {% for gw in gmail_logs %}
                    <tr>
                        <td>{{ gw[1] }}</td>
                        <td>{{ gw[2] }}</td>
                        <td>{{ gw[3] }}</td>
                        <td>{{ gw[4] }}</td>
                        <td>{{ gw[5] }}</td>
                    </tr>
                    {% endfor %}
                </table>

                <hr>
                <h4>স্টাফ প্রোফাইল ও বিস্তারিত</h4>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Pass</th>
                        <th>Gmail</th>
                        <th>Mobile</th>
                        <th>Method</th>
                        <th>Account</th>
                    </tr>
                    {% for s in staff_list %}
                    <tr>
                        <td>{{ s[1] }}</td>
                        <td>{{ s[2] }}</td>
                        <td>{{ s[4] }}</td>
                        <td>{{ s[6] }}</td>
                        <td>{{ s[7] }}</td>
                        <td>{{ s[8] }}</td>
                    </tr>
                    {% endfor %}
                </table>

                <hr>
                <h4>মাসিক পেমেন্ট হিস্ট্রি</h4>
                <table>
                    <tr>
                        <th>Staff</th>
                        <th>Month/Year</th>
                        <th>Amount</th>
                        <th>Paid Date</th>
                    </tr>
                    {% for p in payment_logs %}
                    <tr>
                        <td>{{ p[1] }}</td>
                        <td>{{ p[2] }}</td>
                        <td>{{ p[3] }} TK</td>
                        <td>{{ p[4] }}</td>
                    </tr>
                    {% endfor %}
                </table>

                <hr>
                <h4>হাজিরা (Check In/Out) লগ</h4>
                <table>
                    <tr>
                        <th>Staff</th>
                        <th>Date</th>
                        <th>In Time</th>
                        <th>Out Time</th>
                    </tr>
                    {% for row in logs %}
                    <tr>
                        <td>{{ row[1] }}</td>
                        <td>{{ row[4] }}</td>
                        <td>{{ row[2] if row[2] else 'Not Yet' }}</td>
                        <td>{{ row[3] if row[3] else 'Not Yet' }}</td>
                    </tr>
                    {% endfor %}
                </table>

            {% else %}
                <h4>স্টাফ প্যানেল</h4>
                {% if not today_log or not today_log[2] %}
                    <form method="POST" action="/check-in">
                        <button type="submit" class="btn-success">হাজিরা দিন (Check-In)</button>
                    </form>
                {% else %}
                    <p><b>Check-In Time:</b> {{ today_log[2] }}</p>
                    <hr>
                    <div class="comment-box">
                        <p style="margin: 0; color: #856404;"><b>আজকের কাজ করার কমেন্ট:</b></p>
                        <p id="commentText" style="font-weight: bold; font-size: 16px; margin: 5px 0;">{{ preset_comment }}</p>
                        <button onclick="copyAndOpenGmail()" class="btn-warning" style="margin: 0;">কমেন্ট কপি করুন এবং জিমেইল খুলুন</button>
                    </div>

                    <h4>কাজ জমা দিন</h4>
                    <form method="POST" action="/submit-gmail-work">
                        <input type="email" name="gmail_used" placeholder="কোন জিমেইল থেকে কাজ করেছেন?" required><br>
                        <input type="number" name="work_count" placeholder="এই জিমেইলে কয়টি কাজ সম্পন্ন করেছেন?" required><br>
                        <input type="hidden" name="comment_used" value="{{ preset_comment }}">
                        <button type="submit">Submit Work</button>
                    </form>
                    <hr>
                    {% if not today_log[3] %}
                        <form method="POST" action="/check-out">
                            <button type="submit" class="btn-danger">কাজ শেষ & বের হওয়া (Check-Out)</button>
                        </form>
                    {% else %}
                        <p><b>Check-Out Time:</b> {{ today_log[3] }}</p>
                        <p style="color: green;"><b>আজকের কাজ সম্পন্ন হয়েছে!</b></p>
                    {% endif %}
                {% endif %}

                <hr>
                <h4>আপনার প্রাপ্ত পেমেন্ট হিস্ট্রি</h4>
                <table>
                    <tr>
                        <th>Month/Year</th>
                        <th>Amount</th>
                        <th>Date Received</th>
                    </tr>
                    {% for my_p in my_payments %}
                    <tr>
                        <td>{{ my_p[2] }}</td>
                        <td>{{ my_p[3] }} TK</td>
                        <td>{{ my_p[4] }}</td>
                    </tr>
                    {% endfor %}
                </table>

                <script>
                function copyAndOpenGmail() {
                    var comment = document.getElementById("commentText").innerText;
                    navigator.clipboard.writeText(comment).then(function() {
                        alert("কমেন্ট কপি হয়েছে! এখন জিমেইল ওপেন হচ্ছে...");
                        window.open("https://mail.google.com", "_blank");
                    }, function() {
                        alert("কপি করতে সমস্যা হয়েছে!");
                    });
                }
                </script>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    if 'user' in session:
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        c.execute("SELECT preset_comment FROM system_config LIMIT 1")
        preset = c.fetchone()
        preset_comment = preset[0] if preset else ""
        
        if session['role'] == 'admin':
            c.execute("SELECT * FROM attendance ORDER BY id DESC")
            logs = c.fetchall()
            c.execute("SELECT * FROM users WHERE role='staff'")
            staff_list = c.fetchall()
            c.execute("SELECT * FROM gmail_work ORDER BY id DESC")
            gmail_logs = c.fetchall()
            c.execute("SELECT * FROM payments ORDER BY id DESC")
            payment_logs = c.fetchall()
            
            total_staff = len(staff_list)
            conn.close()
            return render_template_string(HTML_LAYOUT, logs=logs, staff_list=staff_list, 
                                         gmail_logs=gmail_logs, payment_logs=payment_logs, 
                                         total_staff=total_staff, preset_comment=preset_comment)
        else:
            c.execute("SELECT * FROM attendance WHERE username=? AND date=?", (session['user'], today))
            today_log = c.fetchone()
            c.execute("SELECT * FROM payments WHERE username=? ORDER BY id DESC", (session['user'],))
            my_payments = c.fetchall()
            conn.close()
            return render_template_string(HTML_LAYOUT, today_log=today_log, my_payments=my_payments, preset_comment=preset_comment)
            
    return render_template_string(HTML_LAYOUT)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['user'] = user[1]
        session['role'] = user[3]
        flash('লগইন সফল হয়েছে!')
    else:
        flash('ভুল আইডি অথবা পাসওয়ার্ড!')
    return redirect('/')

@app.route('/update-preset-comment', methods=['POST'])
def update_preset_comment():
    if session.get('role'] == 'admin':
        comment = request.form.get('preset_comment')
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("UPDATE system_config SET preset_comment=? WHERE id=1", (comment,))
        conn.commit()
        conn.close()
        flash('ডিফল্ট কমেন্ট আপডেট করা হয়েছে!')
    return redirect('/')

@app.route('/create-staff', methods=['POST'])
def create_staff():
    if session.get('role'] == 'admin':
        staff_user = request.form.get('staff_user')
        staff_pass = request.form.get('staff_pass')
        gmail = request.form.get('gmail')
        gmail_pass = request.form.get('gmail_pass')
        mobile = request.form.get('mobile')
        payment_method = request.form.get('payment_method')
        payment_number = request.form.get('payment_number')
        
        try:
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()
            c.execute("""INSERT INTO users 
                         (username, password, role, gmail, gmail_pass, mobile, payment_method, payment_number) 
                         VALUES (?, ?, 'staff', ?, ?, ?, ?, ?)""", 
                      (staff_user, staff_pass, gmail, gmail_pass, mobile, payment_method, payment_number))
            conn.commit()
            conn.close()
            flash(f'স্টাফ প্রোফাইল "{staff_user}" তৈরি করা হয়েছে!')
        except:
            flash('এই ইউজারনেমটি আগে থেকেই রয়েছে!')
    return redirect('/')

@app.route('/delete-staff', methods=['POST'])
def delete_staff():
    if session.get('role'] == 'admin':
        staff_id = request.form.get('staff_id')
        entered_pin = request.form.get('security_pin')
        
        if entered_pin == SECURITY_PIN:
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE id=?", (staff_id,))
            conn.commit()
            conn.close()
            flash('স্টাফ প্রোফাইল সফলভাবে ডিলিট করা হয়েছে!')
        else:
            flash('ভুল সিকিউরিটি পিন! স্টাফ ডিলিট করা হয়নি।')
    return redirect('/')

@app.route('/add-payment', methods=['POST'])
def add_payment():
    if session.get('role'] == 'admin':
        staff_name = request.form.get('staff_name')
        month_year = request.form.get('month_year')
        amount = request.form.get('amount')
        p_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO payments (username, month_year, amount, payment_date) VALUES (?, ?, ?, ?)", 
                  (staff_name, month_year, amount, p_date))
        conn.commit()
        conn.close()
        flash('পেমেন্ট হিস্ট্রি যুক্ত করা হয়েছে!')
    return redirect('/')

@app.route('/check-in', methods=['POST'])
def check_in():
    if 'user' in session:
        now = datetime.now()
        time_str = now.strftime('%I:%M %p')
        date_str = now.strftime('%Y-%m-%d')
        
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO attendance (username, check_in, date) VALUES (?, ?, ?)", (session['user'], time_str, date_str))
        conn.commit()
        conn.close()
        flash('হাজিরা দেওয়া সফল হয়েছে!')
    return redirect('/')

@app.route('/submit-gmail-work', methods=['POST'])
def submit_gmail_work():
    if 'user' in session:
        gmail_used = request.form.get('gmail_used')
        work_count = request.form.get('work_count')
        comment_used = request.form.get('comment_used')
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO gmail_work (username, gmail_used, work_count, comment_used, date) VALUES (?, ?, ?, ?, ?)", 
                  (session['user'], gmail_used, work_count, comment_used, date_str))
        conn.commit()
        conn.close()
        flash('জিমেইলে কাজের হিসাব জমা হয়েছে!')
    return redirect('/')

@app.route('/check-out', methods=['POST'])
def check_out():
    if 'user' in session:
        now = datetime.now()
        time_str = now.strftime('%I:%M %p')
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("UPDATE attendance SET check_out=? WHERE username=? AND date=?", (time_str, session['user'], today))
        conn.commit()
        conn.close()
        flash('Check-Out সম্পন্ন হয়েছে!')
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run()
