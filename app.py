import sqlite3
from datetime import datetime
from flask import Flask, render_template_string, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'admin_super_secret_key'

SECURITY_PIN = "137955"

def get_db():
    conn = sqlite3.connect('attendance.db')
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  staff_name TEXT,
                  password TEXT, 
                  role TEXT,
                  gmail TEXT,
                  gmail_pass TEXT,
                  mobile TEXT,
                  payment_method TEXT,
                  payment_number TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS attendance 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, check_in TEXT, check_out TEXT, date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS gmail_work 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, gmail_used TEXT, work_count INTEGER, comment_used TEXT, date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS payments 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, month_year TEXT, amount REAL, payment_date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS system_config 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, preset_comment TEXT, admin_contact TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS chats 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, timestamp TEXT)''')
    
    c.execute("SELECT * FROM users WHERE username='Khushbu23'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, staff_name, password, role) VALUES ('Khushbu23', 'Admin', '01751947523', 'admin')")
    
    c.execute("SELECT * FROM system_config")
    if not c.fetchone():
        c.execute("INSERT INTO system_config (preset_comment, admin_contact) VALUES ('Great service! Highly recommended.', 'WhatsApp / Call: 01751947523')")

    conn.commit()
    conn.close()

init_db()

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Staff & Task Management System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 15px; background: #eef2f3; }
        .card { background: white; padding: 20px; border-radius: 8px; max-width: 850px; margin: 0 auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        input, select, textarea { width: 93%; padding: 8px; margin: 5px 0; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #007bff; color: white; border: none; padding: 10px; width: 97%; cursor: pointer; border-radius: 4px; font-weight: bold; margin-top: 5px; }
        .btn-danger { background: #dc3545; }
        .btn-success { background: #28a745; }
        .btn-warning { background: #ffc107; color: black; }
        .stats-box { display: flex; gap: 10px; margin-bottom: 15px; }
        .stat-card { background: #007bff; color: white; padding: 10px; border-radius: 6px; flex: 1; text-align: center; }
        table { width: 100%; margin-top: 15px; border-collapse: collapse; font-size: 13px; display: block; overflow-x: auto; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background: #343a40; color: white; }
        .comment-box { background: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .chat-box { background: #f1f1f1; border: 1px solid #ccc; padding: 10px; border-radius: 5px; height: 200px; overflow-y: scroll; margin-bottom: 10px; }
        .chat-msg { margin: 5px 0; padding: 5px; border-radius: 4px; }
        .msg-admin { background: #d4edda; text-align: left; }
        .msg-staff { background: #d1ecf1; text-align: right; }
        details { background: #f8f9fa; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-top: 15px; }
        summary { font-weight: bold; cursor: pointer; color: #333; }
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
                <input type="text" name="username" placeholder="Enter Username / Staff ID" required><br>
                <input type="password" name="password" placeholder="Enter Password" required><br>
                <button type="submit">Login</button>
            </form>
        {% else %}
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>{{ session['user'] }} ({{ session['role'] | upper }})</h3>
                <a href="/logout" style="color: red; font-weight: bold; text-decoration: none;">Logout</a>
            </div>
            <hr>

            {% if session['role'] == 'admin' %}
                <div class="stats-box">
                    <div class="stat-card">
                        <h3>{{ total_staff }}</h3>
                        <p>মোট স্টাফ</p>
                    </div>
                </div>

                <h3>নতুন স্টাফ অ্যাকাউন্ট তৈরি করুন</h3>
                <form method="POST" action="/create-staff">
                    <input type="text" name="staff_user" placeholder="স্টাফ ইউজার আইডি (Login ID)" required><br>
                    <input type="text" name="staff_name" placeholder="স্টাফ নাম (Staff Name)" required><br>
                    <input type="email" name="gmail" placeholder="জিমেইল এড্রেস (Gmail)" required><br>
                    <input type="text" name="gmail_pass" placeholder="জিমেইল পাসওয়ার্ড" required><br>
                    <input type="text" name="staff_pass" placeholder="সাধারণ পাসওয়ার্ড (লগইনের জন্য)" required><br>
                    <input type="text" name="mobile" placeholder="মোবাইল নম্বর" required><br>
                    <select name="payment_method" required>
                        <option value="bKash">বিকাশ (bKash)</option>
                        <option value="Nagad">নগদ (Nagad)</option>
                        <option value="Rocket">রকেট (Rocket)</option>
                        <option value="Upay">উপায় (Upay)</option>
                        <option value="Bank">ব্যাংক অ্যাকাউন্ট (Bank)</option>
                    </select><br>
                    <input type="text" name="payment_number" placeholder="পেমেন্ট নম্বর / অ্যাকাউন্ট নম্বর" required><br>
                    <input type="password" name="security_pin" placeholder="সিকিউরিটি কোড দিন (137955)" required><br>
                    <button type="submit" class="btn-success">Create Staff Account</button>
                </form>

                <details>
                    <summary>⚙️ অন্যান্য সেটিংস ও এডমিন টুলস</summary>
                    <div style="margin-top: 10px;">
                        <h4>কাজের কমেন্ট (Comment) সেট করুন</h4>
                        <form method="POST" action="/update-preset-comment">
                            <textarea name="preset_comment" rows="3" placeholder="স্টাফদের জন্য কমেন্ট লিখুন..." required>{{ preset_comment }}</textarea><br>
                            <button type="submit" class="btn-warning">Update Default Comment</button>
                        </form>
                        <hr>
                        <h4>স্টাফ ডিলিট করুন</h4>
                        <form method="POST" action="/delete-staff">
                            <select name="staff_id" required>
                                <option value="">ডিলিট করার জন্য স্টাফ সিলেক্ট করুন</option>
                                {% for s in staff_list %}
                                <option value="{{ s[0] }}">{{ s[2] }} (ID: {{ s[1] }})</option>
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
                                <option value="{{ s[2] }}">{{ s[2] }} (ID: {{ s[1] }})</option>
                                {% endfor %}
                            </select><br>
                            <input type="text" name="month_year" placeholder="মাস ও বছর (যেমন: August 2026)" required><br>
                            <input type="number" step="0.01" name="amount" placeholder="পেমেন্ট এর পরিমাণ (টাকা)" required><br>
                            <button type="submit">Save Payment</button>
                        </form>
                    </div>
                </details>

                <hr>
                <h4>স্টাফ প্রোফাইল ও পাসওয়ার্ড তালিকা</h4>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Password</th>
                        <th>Gmail</th>
                        <th>Mobile</th>
                        <th>Method & Number</th>
                    </tr>
                    {% for s in staff_list %}
                    <tr>
                        <td><b>{{ s[1] }}</b></td>
                        <td>{{ s[2] }}</td>
                        <td>{{ s[3] }}</td>
                        <td>{{ s[5] }}</td>
                        <td>{{ s[7] }}</td>
                        <td>{{ s[8] }}: {{ s[9] }}</td>
                    </tr>
                    {% endfor %}
                </table>

                <hr>
                <h4>💬 স্টাফদের সাথে লাইভ চ্যাট</h4>
                <form method="GET" action="/">
                    <select name="chat_with" onchange="this.form.submit()">
                        <option value="">চ্যাট করার জন্য স্টাফ সিলেক্ট করুন</option>
                        {% for s in staff_list %}
                        <option value="{{ s[1] }}" {% if selected_chat_user == s[1] %}selected{% endif %}>{{ s[2] }} (ID: {{ s[1] }})</option>
                        {% endfor %}
                    </select>
                </form>

                {% if selected_chat_user %}
                    <div class="chat-box">
                        {% for msg in chat_messages %}
                            <div class="chat-msg {% if msg[1] == 'Khushbu23' %}msg-admin{% else %}msg-staff{% endif %}">
                                <small><b>{{ msg[1] }}</b> ({{ msg[4] }}):</small><br>
                                <span>{{ msg[3] }}</span>
                            </div>
                        {% endfor %}
                    </div>
                    <form method="POST" action="/send-message">
                        <input type="hidden" name="receiver" value="{{ selected_chat_user }}">
                        <input type="text" name="message" placeholder="মেসেজ লিখুন..." required autocomplete="off">
                        <button type="submit">Send Message</button>
                    </form>
                {% endif %}

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
                <h4>💬 এডমিনের সাথে সরাসরি কথা বলুন (চ্যাট)</h4>
                <div class="chat-box">
                    {% for msg in chat_messages %}
                        <div class="chat-msg {% if msg[1] == session['user'] %}msg-staff{% else %}msg-admin{% endif %}">
                            <small><b>{{ msg[1] }}</b> ({{ msg[4] }}):</small><br>
                            <span>{{ msg[3] }}</span>
                        </div>
                    {% endfor %}
                </div>
                <form method="POST" action="/send-message">
                    <input type="hidden" name="receiver" value="Khushbu23">
                    <input type="text" name="message" placeholder="এডমিনকে মেসেজ লিখুন..." required autocomplete="off">
                    <button type="submit">Send to Admin</button>
                </form>

                <script>
                function copyAndOpenGmail() {
                    var comment = document.getElementById("commentText").innerText;
                    navigator.clipboard.writeText(comment).then(function() {
                        alert("কমেন্ট কপি হয়েছে! এখন জিমেইল ওপেন হচ্ছে...");
                        window.open("https://mail.google.com", "_blank");
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
        conn = get_db()
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        c.execute("SELECT preset_comment, admin_contact FROM system_config LIMIT 1")
        config = c.fetchone()
        preset_comment = config[0] if config else ""
        admin_contact = config[1] if config else ""
        
        if session['role'] == 'admin':
            c.execute("SELECT * FROM users WHERE role='staff'")
            staff_list = c.fetchall()
            
            selected_chat_user = request.args.get('chat_with')
            chat_messages = []
            if selected_chat_user:
                c.execute("SELECT * FROM chats WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id ASC", 
                          ('Khushbu23', selected_chat_user, selected_chat_user, 'Khushbu23'))
                chat_messages = c.fetchall()
                
            total_staff = len(staff_list)
            conn.close()
            return render_template_string(HTML_LAYOUT, staff_list=staff_list, 
                                         total_staff=total_staff, preset_comment=preset_comment, 
                                         admin_contact=admin_contact, selected_chat_user=selected_chat_user, 
                                         chat_messages=chat_messages)
        else:
            c.execute("SELECT * FROM attendance WHERE username=? AND date=?", (session['user'], today))
            today_log = c.fetchone()
            
            c.execute("SELECT * FROM chats WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id ASC", 
                      (session['user'], 'Khushbu23', 'Khushbu23', session['user']))
            chat_messages = c.fetchall()
            
            conn.close()
            return render_template_string(HTML_LAYOUT, today_log=today_log, preset_comment=preset_comment, 
                                         admin_contact=admin_contact, chat_messages=chat_messages)
            
    return render_template_string(HTML_LAYOUT)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['user'] = user[1]
        session['role'] = user[4]
        flash('লগইন সফল হয়েছে!')
    else:
        flash('ভুল আইডি অথবা পাসওয়ার্ড!')
    return redirect('/')

@app.route('/update-preset-comment', methods=['POST'])
def update_preset_comment():
    if session.get('role') == 'admin':
        comment = request.form.get('preset_comment')
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE system_config SET preset_comment=? WHERE id=1", (comment,))
        conn.commit()
        conn.close()
        flash('ডিফল্ট কমেন্ট আপডেট করা হয়েছে!')
    return redirect('/')

@app.route('/create-staff', methods=['POST'])
def create_staff():
    if session.get('role') == 'admin':
        staff_user = request.form.get('staff_user')
        staff_name = request.form.get('staff_name')
        gmail = request.form.get('gmail')
        gmail_pass = request.form.get('gmail_pass')
        staff_pass = request.form.get('staff_pass')
        mobile = request.form.get('mobile')
        payment_method = request.form.get('payment_method')
        payment_number = request.form.get('payment_number')
        entered_pin = request.form.get('security_pin')
        
        if entered_pin == SECURITY_PIN:
            try:
                conn = get_db()
                c = conn.cursor()
                c.execute("""INSERT INTO users 
                             (username, staff_name, password, role, gmail, gmail_pass, mobile, payment_method, payment_number) 
                             VALUES (?, ?, ?, 'staff', ?, ?, ?, ?, ?)""", 
                          (staff_user, staff_name, staff_pass, gmail, gmail_pass, mobile, payment_method, payment_number))
                conn.commit()
                conn.close()
                flash('স্টাফ অ্যাকাউন্ট সফলভাবে তৈরি করা হয়েছে!')
            except:
                flash('এই ইউজার আইডিটি আগে থেকেই রয়েছে!')
        else:
            flash('ভুল সিকিউরিটি কোড!')
    return redirect('/')

@app.route('/delete-staff', methods=['POST'])
def delete_staff():
    if session.get('role') == 'admin':
        staff_id = request.form.get('staff_id')
        entered_pin = request.form.get('security_pin')
        if entered_pin == SECURITY_PIN:
            conn = get_db()
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE id=?", (staff_id,))
            conn.commit()
            conn.close()
            flash('স্টাফ প্রোফাইল ডিলিট করা হয়েছে!')
        else:
            flash('ভুল সিকিউরিটি পিন!')
    return redirect('/')

@app.route('/add-payment', methods=['POST'])
def add_payment():
    if session.get('role') == 'admin':
        staff_name = request.form.get('staff_name')
        month_year = request.form.get('month_year')
        amount = request.form.get('amount')
        p_date = datetime.now().strftime('%Y-%m-%d')
        conn = get_db()
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
        conn = get_db()
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
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO gmail_work (username, gmail_used, work_count, comment_used, date) VALUES (?, ?, ?, ?, ?)", 
                  (session['user'], gmail_used, work_count, comment_used, date_str))
        conn.commit()
        conn.close()
        flash('কাজের হিসাব জমা হয়েছে!')
    return redirect('/')

@app.route('/check-out', methods=['POST'])
def check_out():
    if 'user' in session:
        now = datetime.now()
        time_str = now.strftime('%I:%M %p')
        today = datetime.now().strftime('%Y-%m-%d')
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE attendance SET check_out=? WHERE username=? AND date=?", (time_str, session['user'], today))
        conn.commit()
        conn.close()
        flash('Check-Out সম্পন্ন হয়েছে!')
    return redirect('/')

@app.route('/send-message', methods=['POST'])
def send_message():
    if 'user' in session:
        sender = session['user']
        receiver = request.form.get('receiver')
        message = request.form.get('message')
        timestamp = datetime.now().strftime('%I:%M %p, %d %b')
        
        if message:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO chats (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)", 
                      (sender, receiver, message, timestamp))
            conn.commit()
            conn.close()
            
        if session['role'] == 'admin':
            return redirect(f'/?chat_with={receiver}')
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run()
