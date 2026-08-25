import sqlite3
import random
import os
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
                  account_type TEXT,
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
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, month_year TEXT, amount REAL, payment_method TEXT, payment_number TEXT, payment_date TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS personal_payment_notes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, note_title TEXT, note_details TEXT, date_saved TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS system_config 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, preset_comment TEXT, admin_contact TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS chats 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, image_url TEXT, timestamp TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS assigned_tasks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, task_details TEXT, assigned_date TEXT, status TEXT, start_time TEXT, end_time TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS staff_notes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, note TEXT, date_posted TEXT)''')

    # Trash / Recycle Bin Table for deleted items safety
    c.execute('''CREATE TABLE IF NOT EXISTS trash_bin 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, item_type TEXT, item_details TEXT, deleted_time TEXT)''')
    
    c.execute("SELECT * FROM users WHERE username='Khushbu23'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, staff_name, password, role, account_type) VALUES ('Khushbu23', 'Admin', '01751947523', 'admin', 'Admin')")
    
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
        .stat-card { background: #28a745; color: white; padding: 15px; border-radius: 6px; flex: 1; text-align: center; font-size: 16px; }
        table { width: 100%; margin-top: 15px; border-collapse: collapse; font-size: 13px; display: block; overflow-x: auto; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #343a40; color: white; text-align: center; }
        .comment-box { background: #fff3cd; border: 1px solid #ffeeba; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .note-box { background: #e2e3e5; border: 1px solid #d6d8db; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .chat-box { background: #f1f1f1; border: 1px solid #ccc; padding: 10px; border-radius: 5px; height: 220px; overflow-y: scroll; margin-bottom: 10px; }
        .chat-msg { margin: 8px 0; padding: 8px; border-radius: 6px; background: white; border: 1px solid #ddd; }
        .msg-admin { background: #d4edda; text-align: left; }
        .msg-staff { background: #d1ecf1; text-align: right; }
        .chat-img { max-width: 150px; border-radius: 5px; margin-top: 5px; display: block; }
        details { background: #f8f9fa; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-top: 15px; }
        summary { font-weight: bold; cursor: pointer; color: #333; }
        .search-box { background: #e9ecef; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .link-btn { text-align: center; margin-top: 15px; }
        .link-btn a { color: #007bff; text-decoration: none; font-weight: bold; }
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
            {% if request.path == '/register' %}
                <h2 style="text-align: center;">নতুন একাউন্ট রেজিস্টার করুন</h2>
                <form method="POST" action="/register-action">
                    <input type="text" name="staff_name" placeholder="আপনার নাম (Staff Name)" required><br>
                    <input type="email" name="gmail" placeholder="জিমেইল এড্রেস (Gmail)" required><br>
                    <input type="text" name="mobile" placeholder="মোবাইল নম্বর" required><br>
                    <select name="payment_method" required>
                        <option value="bKash">বিকাশ (bKash)</option>
                        <option value="Nagad">নগদ (Nagad)</option>
                        <option value="Rocket">রকেট (Rocket)</option>
                        <option value="Upay">উপায় (Upay)</option>
                        <option value="Bank">ব্যাংক (Bank)</option>
                    </select><br>
                    <input type="text" name="payment_number" placeholder="পেমেন্ট নম্বর (যে নাম্বারে টাকা তুলবেন)" required><br>
                    <input type="password" name="password" placeholder="পাসওয়ার্ড তৈরি করুন (Password)" required><br>
                    <button type="submit" class="btn-success">Register Account</button>
                </form>
                <div class="link-btn">
                    <a href="/">← লগইন পেজে ফিরে যান</a>
                </div>
            {% else %}
                <h2 style="text-align: center;">Staff & Admin Login</h2>
                <form method="POST" action="/login">
                    <input type="text" name="username" placeholder="Enter Username / Gmail / Staff ID" required><br>
                    <input type="password" name="password" placeholder="Enter Password" required><br>
                    <button type="submit">Login</button>
                </form>
                <div class="link-btn">
                    <p>একাউন্ট নেই? <a href="/register">নতুন একাউন্ট তৈরি করুন</a></p>
                </div>
            {% endif %}
        {% else %}
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3>{{ session['user'] }} ({{ session['role'] | upper }})</h3>
                <a href="/logout" style="color: red; font-weight: bold; text-decoration: none;">Logout</a>
            </div>
            <hr>

            {% if session['role'] == 'admin' %}
                <div class="stats-box">
                    <div class="stat-card">
                        <h3>👥 মোট রেজিস্টার্ড একাউন্ট: {{ total_staff }} টি</h3>
                    </div>
                </div>

                <h3>স্টাফকে নির্দিষ্ট কাজ এসাইন (Assign Task) করুন</h3>
                <form method="POST" action="/assign-task">
                    <select name="staff_username" required>
                        <option value="">কাজ দেওয়ার জন্য স্টাফ সিলেক্ট করুন</option>
                        <optgroup label="🟢 রেজিস্টার্ড অ্যাকাউন্টসমূহ">
                            {% for s in staff_list %}
                                {% if s[5] == 'Registered' %}
                                <option value="{{ s[1] }}">{{ s[2] }} (ID: {{ s[1] }})</option>
                                {% endif %}
                            {% endfor %}
                        </optgroup>
                        <optgroup label="🔵 অ্যাডমিনের পার্সোনাল সেভ করা আইডি">
                            {% for s in staff_list %}
                                {% if s[5] == 'Extra' %}
                                <option value="{{ s[1] }}">{{ s[2] }} (ID: {{ s[1] }})</option>
                                {% endif %}
                            {% endfor %}
                        </optgroup>
                    </select><br>
                    <textarea name="task_details" rows="3" placeholder="কাজের বিবরণ ও নির্দেশনা লিখুন..." required></textarea><br>
                    <button type="submit" class="btn-success">Send Task to Staff</button>
                </form>

                <details>
                    <summary>⚙️ পার্সোনাল আইডি তৈরি ও সিকিউর পেমেন্ট নোট টুলস</summary>
                    <div style="margin-top: 10px;">
                        <h4>নতুন পার্সোনাল আইডি সেভ করুন (Extra Account)</h4>
                        <form method="POST" action="/create-staff">
                            <input list="registered_users_list" name="staff_user" placeholder="স্টাফ ইউজার আইডি" autocomplete="off" required><br>
                            <datalist id="registered_users_list">
                                {% for s in staff_list %}
                                    {% if s[5] == 'Registered' %}
                                    <option value="{{ s[1] }}">{{ s[2] }}</option>
                                    {% endif %}
                                {% endfor %}
                            </datalist>

                            <input type="text" name="staff_name" placeholder="স্টাফ নাম" required><br>
                            <input type="email" name="gmail" placeholder="জিমেইল এড্রেস" required><br>
                            <input type="text" name="gmail_pass" placeholder="জিমেইল পাসওয়ার্ড" required><br>
                            <input type="text" name="staff_pass" placeholder="সাধারণ পাসওয়ার্ড" required><br>
                            <input type="text" name="mobile" placeholder="মোবাইল নম্বর" required><br>
                            <select name="payment_method" required>
                                <option value="bKash">বিকাশ (bKash)</option>
                                <option value="Nagad">নগদ (Nagad)</option>
                                <option value="Rocket">রকেট (Rocket)</option>
                                <option value="Upay">উপায় (Upay)</option>
                                <option value="Bank">ব্যাংক (Bank)</option>
                            </select><br>
                            <input type="text" name="payment_number" placeholder="পেমেন্ট নম্বর" required><br>
                            <input type="password" name="security_pin" placeholder="সিকিউরিটি কোড (137955)" required><br>
                            <button type="submit" class="btn-success">Save Personal Profile</button>
                        </form>
                        <hr>
                        <h4>মাসিক পেমেন্ট রেকর্ড যুক্ত করুন</h4>
                        <form method="POST" action="/add-payment">
                            <select name="staff_name" required>
                                <option value="">স্টাফ নির্বাচন করুন</option>
                                {% for s in staff_list %}
                                <option value="{{ s[1] }}">{{ s[2] }} (ID: {{ s[1] }})</option>
                                {% endfor %}
                            </select><br>
                            <input type="text" name="month_year" placeholder="মাস ও বছর (যেমন: August 2026)" required><br>
                            <input type="number" step="0.01" name="amount" placeholder="টাকার পরিমাণ" required><br>
                            <select name="payment_method" required>
                                <option value="bKash">বিকাশ</option>
                                <option value="Nagad">নগদ</option>
                                <option value="Rocket">রকেট</option>
                                <option value="Upay">উপায়</option>
                                <option value="Bank">ব্যাংক</option>
                            </select><br>
                            <input type="text" name="payment_number" placeholder="পেমেন্ট নম্বর" required><br>
                            <button type="submit">Save Payment History</button>
                        </form>
                    </div>
                </details>

                <hr>
                <h4>🔒 আমার পার্সোনাল সিকিউর পেমেন্ট ও ডকুমেন্ট নোট</h4>
                <div style="background: #f8f9fa; padding: 10px; border: 1px solid #ced4da; border-radius: 5px;">
                    <form method="POST" action="/save-admin-doc">
                        <input type="text" name="note_title" placeholder="নোটের শিরোনাম" required><br>
                        <textarea name="note_details" rows="2" placeholder="বিস্তারিত তথ্য লিখে রাখুন..." required></textarea><br>
                        <input type="password" name="security_pin" placeholder="সিকিউরিটি পিন (137955) দিন" required><br>
                        <button type="submit" class="btn-success">Save Secure Note</button>
                    </form>
                    
                    {% if admin_docs %}
                        <h5 style="margin-bottom: 5px;">সেভ করা ডকুমেন্ট ও নোটসমূহ:</h5>
                        {% for doc in admin_docs %}
                            <div style="background: white; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #ddd;">
                                <p style="margin:0;"><b>{{ doc[2] }}</b>: {{ doc[3] }} <small style="color:gray;">({{ doc[4] }})</small></p>
                                <form method="POST" action="/delete-admin-doc" style="margin-top: 5px;">
                                    <input type="hidden" name="doc_id" value="{{ doc[0] }}">
                                    <input type="password" name="security_pin" placeholder="পিন কোড (137955)" style="width: 130px; padding: 3px;" required>
                                    <button type="submit" class="btn-danger" style="padding: 3px 6px; width: auto; font-size: 11px;">Delete to Trash</button>
                                </form>
                            </div>
                        {% endfor %}
                    {% endif %}
                </div>

                <details style="background: #fff3cd; border-color: #ffeeba; margin-top: 15px;">
                    <summary style="color: #856404;">🗑️ রিসাইকেল বিন / ট্র্যাশ হিস্ট্রি (ডিলিট করা আইটেমসমূহ)</summary>
                    <div style="margin-top: 10px;">
                        <p style="font-size: 12px; color: #666;">আপনি বা এডমিন সিকিউরিটি পিন দিয়ে যা যা ডিলিট করেছেন তা এখানে সংরক্ষিত আছে।</p>
                        {% if trash_items %}
                            <table>
                                <tr>
                                    <th>টাইপ / ক্যাটাগরি</th>
                                    <th>ডিলিট হওয়া তথ্য ও বিবরণ</th>
                                    <th>ডিলিটের সময়</th>
                                </tr>
                                {% for t in trash_items %}
                                <tr>
                                    <td><b>{{ t[1] }}</b></td>
                                    <td>{{ t[2] }}</td>
                                    <td><small>{{ t[3] }}</small></td>
                                </tr>
                                {% endfor %}
                            </table>
                        {% else %}
                            <p style="color: gray;">রিসাইকেল বিন খালি রয়েছে।</p>
                        {% endif %}
                    </div>
                </details>

                <hr>
                <div class="search-box">
                    <h4>🔍 স্টাফ খুঁজুন</h4>
                    <form method="GET" action="/">
                        <input type="text" name="search" value="{{ search_query }}" placeholder="নাম, আইডি, জিমেইল বা মোবাইল দিয়ে খুঁজুন..." style="width: 80%;">
                        <button type="submit" style="width: 15%; display: inline-block; background: #17a2b8;">Search</button>
                    </form>
                </div>

                <h4>স্টাফ প্রোফাইল, পাসওয়ার্ড ও ডিউটি ডিটেলস চেক করুন</h4>
                <table>
                    <tr>
                        <th style="text-align:center;">ID</th>
                        <th style="text-align:center;">Name</th>
                        <th style="text-align:center;">Gmail & Password</th>
                        <th style="text-align:center;">Mobile</th>
                        <th style="text-align:center;">Payment Info</th>
                        <th style="text-align:center;">Action (পাসওয়ার্ড দিন)</th>
                    </tr>
                    {% for s in staff_list %}
                    <tr style="text-align:center;">
                        <td><b>{{ s[1] }}</b></td>
                        <td><a href="/?view_details={{ s[1] }}" style="color: #007bff; font-weight: bold; text-decoration: underline;">{{ s[2] }}</a></td>
                        <td>{{ s[6] }}<br><b style="color: red;">Pass: {{ s[3] }}</b></td>
                        <td>{{ s[8] }}</td>
                        <td>{{ s[9] }} - {{ s[10] }}</td>
                        <td>
                            <form method="POST" action="/delete-staff" style="margin:0;">
                                <input type="hidden" name="username" value="{{ s[1] }}">
                                <input type="password" name="security_pin" placeholder="পিন (137955)" style="width: 85px; padding: 3px;" required>
                                <button type="submit" class="btn-danger" style="padding: 4px 6px; font-size: 11px; width: auto;">Delete</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>

                {% if detail_staff %}
                    <div style="background: #e2e3e5; padding: 15px; margin-top: 15px; border-radius: 5px; border: 1px solid #ccc;">
                        <h4 style="margin-top: 0; color: #333;">📊 স্টাফ ডিটেলস রিপোর্ট: {{ detail_staff[2] }} (ID: {{ detail_staff[1] }})</h4>
                        <p><b>জিমেইল:</b> {{ detail_staff[6] }} | <b>মোবাইল:</b> {{ detail_staff[8] }}</p>
                        <p><b>পেমেন্ট মাধ্যম:</b> {{ detail_staff[9] }} (নম্বর: {{ detail_staff[10] }})</p>
                        
                        <h5>হাজিরা ও ডিউটি রেকর্ড:</h5>
                        {% if staff_attendance_logs %}
                            <ul>
                            {% for att in staff_attendance_logs %}
                                <li>তারিখ: {{ att[4] }} | Check-In: {{ att[2] }} | Check-Out: {{ att[3] if att[3] else 'চলমান' }}</li>
                            {% endfor %}
                            </ul>
                        {% else %}
                            <p style="color: gray;">কোনো হাজিরা রেকর্ড নেই।</p>
                        {% endif %}
                        
                        <h5>জমা দেওয়া কাজের হিসাব:</h5>
                        {% if staff_work_logs %}
                            <ul>
                            {% for wk in staff_work_logs %}
                                <li>তারিখ: {{ wk[5] }} | জিমেইল: {{ wk[2] }} | কাজ সংখ্যা: {{ wk[3] }} টি</li>
                            {% endfor %}
                            </ul>
                        {% else %}
                            <p style="color: gray;">কোনো কাজের হিসাব নেই।</p>
                        {% endif %}
                        <a href="/" class="btn-success" style="display: block; text-align: center; text-decoration: none; padding: 6px;">বন্ধ করুন</a>
                    </div>
                {% endif %}

                <hr>
                <h4>💬 স্টাফদের মেসেজ ও লাইভ চ্যাট</h4>
                <form method="GET" action="/">
                    <select name="chat_with" onchange="this.form.submit()">
                        <option value="">স্টাফ সিলেক্ট করুন</option>
                        {% for s in staff_list %}
                        <option value="{{ s[1] }}" {% if selected_chat_user == s[1] %}selected{% endif %}>{{ s[2] }} (ID: {{ s[1] }})</option>
                        {% endfor %}
                    </select>
                </form>

                {% if selected_chat_user %}
                    <div class="chat-box">
                        {% for msg in chat_messages %}
                            <div class="chat-msg {% if msg[1] == 'Khushbu23' %}msg-admin{% else %}msg-staff{% endif %}">
                                <small><b>{{ msg[1] }}</b> ({{ msg[5] }}):</small><br>
                                <span>{{ msg[3] }}</span>
                                {% if msg[4] %}
                                    <a href="{{ msg[4] }}" target="_blank"><img src="{{ msg[4] }}" class="chat-img"></a>
                                {% endif %}
                            </div>
                        {% endfor %}
                    </div>
                    <form method="POST" action="/send-message" enctype="multipart/form-data">
                        <input type="hidden" name="receiver" value="{{ selected_chat_user }}">
                        <input type="text" name="message" placeholder="উত্তর লিখুন..." autocomplete="off"><br>
                        <input type="file" name="image" accept="image/*" style="padding: 3px;"><br>
                        <button type="submit">Send Message & Screenshot</button>
                    </form>
                {% endif %}

            {% else %}
                <!-- STAFF PANEL -->
                <h4>স্টাফ প্যানেল</h4>
                <div style="display: flex; flex-direction: column; gap: 15px;">
                    <div style="background: #e8f4fd; border: 1px solid #b8daff; padding: 10px; border-radius: 5px;">
                        <h4 style="margin-top: 0; color: #004085;">📝 আমার পেমেন্ট ও আয়ের হিসাব (নিজের নোট)</h4>
                        <form method="POST" action="/save-my-payment-note">
                            <input type="text" name="note_title" placeholder="নোটের শিরোনাম" required><br>
                            <textarea name="note_details" rows="2" placeholder="বিস্তারিত লিখুন..." required></textarea>
                            <button type="submit" class="btn-success" style="padding: 8px;">Save My Payment Note</button>
                        </form>

                        {% if my_payment_notes %}
                            <h5 style="margin-bottom: 5px; margin-top: 10px;">আপনার সেভ করা নোটসমূহ:</h5>
                            {% for mnote in my_payment_notes %}
                                <div style="background: white; padding: 8px; margin-top: 5px; border-radius: 4px; border: 1px solid #b8daff;">
                                    <p style="margin:0;"><b>{{ mnote[2] }}</b>: {{ mnote[3] }} <small style="color:gray;">({{ mnote[4] }})</small></p>
                                    <form method="POST" action="/delete-my-payment-note" style="margin-top: 5px;">
                                        <input type="hidden" name="note_id" value="{{ mnote[0] }}">
                                        <button type="submit" class="btn-danger" style="padding: 3px 6px; width: auto; font-size: 11px;">Delete</button>
                                    </form>
                                </div>
                            {% endfor %}
                        {% endif %}
                    </div>

                    <!-- Task Section -->
                    {% if assigned_tasks %}
                        <div style="background: #e8f4fd; border: 1px solid #b8daff; padding: 10px; border-radius: 5px;">
                            <h4 style="margin-top: 0; color: #004085;">📥 এডমিন কর্তৃক প্রদত্ত কাজসমূহ:</h4>
                            {% for task in assigned_tasks %}
                                <div style="background: white; padding: 10px; margin-bottom: 8px; border-radius: 4px; border: 1px solid #b8daff;">
                                    <p><b>কাজের বিবরণ:</b> {{ task[2] }}</p>
                                    <p><b>স্ট্যাটাস:</b> <span style="color: {% if task[4] == 'Pending' %}orange{% elif task[4] == 'Accepted' %}blue{% else %}green{% endif %}; font-weight: bold;">{{ task[4] }}</span></p>
                                    
                                    {% if task[4] == 'Pending' %}
                                        <form method="POST" action="/accept-task">
                                            <input type="hidden" name="task_id" value="{{ task[0] }}">
                                            <button type="submit" class="btn-success">Accept Task</button>
                                        </form>
                                    {% elif task[4] == 'Accepted' %}
                                        {% if not task[5] %}
                                            <form method="POST" action="/start-task">
                                                <input type="hidden" name="task_id" value="{{ task[0] }}">
                                                <button type="submit" class="btn-warning">Start Work</button>
                                            </form>
                                        {% else %}
                                            <form method="POST" action="/finish-task">
                                                <input type="hidden" name="task_id" value="{{ task[0] }}">
                                                <button type="submit" class="btn-danger">Finish Work</button>
                                            </form>
                                        {% endif %}
                                    {% endif %}
                                </div>
                            {% endfor %}
                        </div>
                    {% endif %}

                    <div>
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

                            <h4>প্রতিদিনের কাজের হিসাব জমা দিন</h4>
                            <form method="POST" action="/submit-gmail-work">
                                <input type="email" name="gmail_used" placeholder="কোন জিমেইল থেকে কাজ করেছেন?" required><br>
                                <input type="number" name="work_count" placeholder="এই জিমেইলে কয়টি কাজ?" required><br>
                                <input type="hidden" name="comment_used" value="{{ preset_comment }}">
                                <button type="submit" class="btn-success">Submit Work Count</button>
                            </form>
                            <hr>
                            {% if not today_log[3] %}
                                <form method="POST" action="/check-out">
                                    <button type="submit" class="btn-danger">Check-Out</button>
                                </form>
                            {% else %}
                                <p style="color: green;"><b>আজকের কাজ সম্পন্ন হয়েছে!</b></p>
                            {% endif %}
                        {% endif %}
                    </div>
                </div>

                <hr>
                <h4>💬 এডমিনের সাথে চ্যাট করুন</h4>
                <div class="chat-box">
                    {% for msg in chat_messages %}
                        <div class="chat-msg {% if msg[1] == session['user'] %}msg-staff{% else %}msg-admin{% endif %}">
                            <small><b>{{ msg[1] }}</b> ({{ msg[5] }}):</small><br>
                            <span>{{ msg[3] }}</span>
                            {% if msg[4] %}
                                <a href="{{ msg[4] }}" target="_blank"><img src="{{ msg[4] }}" class="chat-img"></a>
                            {% endif %}
                        </div>
                    {% endfor %}
                </div>
                <form method="POST" action="/send-message" enctype="multipart/form-data">
                    <input type="hidden" name="receiver" value="Khushbu23">
                    <input type="text" name="message" placeholder="মেসেজ লিখুন..." autocomplete="off"><br>
                    <input type="file" name="image" accept="image/*" style="padding: 3px;"><br>
                    <button type="submit">Send to Admin</button>
                </form>

                <script>
                function copyAndOpenGmail() {
                    var comment = document.getElementById("commentText").innerText;
                    navigator.clipboard.writeText(comment).then(function() {
                        alert("কমেন্ট কপি হয়েছে! জিমেইল ওপেন হচ্ছে...");
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
            search_query = request.args.get('search', '').strip()
            if search_query:
                q = f"%{search_query}%"
                c.execute("SELECT * FROM users WHERE role='staff' AND (username LIKE ? OR staff_name LIKE ? OR gmail LIKE ? OR mobile LIKE ?)", (q, q, q, q))
            else:
                c.execute("SELECT * FROM users WHERE role='staff'")
            staff_list = c.fetchall()
            
            c.execute("SELECT * FROM personal_payment_notes WHERE username='Khushbu23' ORDER BY id DESC")
            admin_docs = c.fetchall()

            c.execute("SELECT * FROM trash_bin ORDER BY id DESC")
            trash_items = c.fetchall()
            
            selected_chat_user = request.args.get('chat_with')
            chat_messages = []
            if selected_chat_user:
                c.execute("SELECT * FROM chats WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id ASC", 
                          ('Khushbu23', selected_chat_user, selected_chat_user, 'Khushbu23'))
                chat_messages = c.fetchall()
                
            c.execute("SELECT COUNT(*) FROM users WHERE role='staff'")
            total_staff = c.fetchone()[0]
            
            view_staff_id = request.args.get('view_details')
            detail_staff = None
            staff_attendance_logs = []
            staff_work_logs = []
            if view_staff_id:
                c.execute("SELECT * FROM users WHERE username=?", (view_staff_id,))
                detail_staff = c.fetchone()
                c.execute("SELECT * FROM attendance WHERE username=? ORDER BY id DESC", (view_staff_id,))
                staff_attendance_logs = c.fetchall()
                c.execute("SELECT * FROM gmail_work WHERE username=? ORDER BY id DESC", (view_staff_id,))
                staff_work_logs = c.fetchall()

            conn.close()
            return render_template_string(HTML_LAYOUT, staff_list=staff_list, 
                                         total_staff=total_staff, preset_comment=preset_comment, 
                                         admin_contact=admin_contact, selected_chat_user=selected_chat_user, 
                                         chat_messages=chat_messages, search_query=search_query, 
                                         admin_docs=admin_docs, trash_items=trash_items,
                                         detail_staff=detail_staff, staff_attendance_logs=staff_attendance_logs,
                                         staff_work_logs=staff_work_logs)
        else:
            c.execute("SELECT * FROM attendance WHERE username=? AND date=?", (session['user'], today))
            today_log = c.fetchone()
            
            c.execute("SELECT * FROM chats WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) ORDER BY id ASC", 
                      (session['user'], 'Khushbu23', 'Khushbu23', session['user']))
            chat_messages = c.fetchall()

            c.execute("SELECT * FROM assigned_tasks WHERE username=? ORDER BY id DESC", (session['user'],))
            assigned_tasks = c.fetchall()
            
            c.execute("SELECT * FROM personal_payment_notes WHERE username=? ORDER BY id DESC", (session['user'],))
            my_payment_notes = c.fetchall()
            
            conn.close()
            return render_template_string(HTML_LAYOUT, today_log=today_log, preset_comment=preset_comment, 
                                         admin_contact=admin_contact, chat_messages=chat_messages, 
                                         assigned_tasks=assigned_tasks, my_payment_notes=my_payment_notes)
            
    return render_template_string(HTML_LAYOUT)

@app.route('/register')
def register_page():
    return render_template_string(HTML_LAYOUT)

@app.route('/register-action', methods=['POST'])
def register_action():
    staff_name = request.form.get('staff_name')
    gmail = request.form.get('gmail')
    mobile = request.form.get('mobile')
    payment_method = request.form.get('payment_method')
    payment_number = request.form.get('payment_number')
    password = request.form.get('password')
    
    rand_num = random.randint(1000, 9999)
    username = f"staff_{rand_num}"
    
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO users 
                     (username, staff_name, password, role, account_type, gmail, gmail_pass, mobile, payment_method, payment_number) 
                     VALUES (?, ?, ?, 'staff', 'Registered', ?, ?, ?, ?, ?)""", 
                  (username, staff_name, password, gmail, 'User Set', mobile, payment_method, payment_number))
        conn.commit()
        conn.close()
        flash(f'একাউন্ট সফলভাবে রেজিস্টার হয়েছে! ইউজার আইডি: {username}')
    except:
        flash('এই জিমেইল দিয়ে ইতিমধ্যে একাউন্ট রয়েছে!')
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE (username=? OR gmail=?) AND password=?", (username, username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['user'] = user[1]
        session['role'] = user[4]
        flash('লগইন সফল হয়েছে!')
    else:
        flash('ভুল আইডি অথবা পাসওয়ার্ড!')
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
                             (username, staff_name, password, role, account_type, gmail, gmail_pass, mobile, payment_method, payment_number) 
                             VALUES (?, ?, ?, 'staff', 'Extra', ?, ?, ?, ?, ?)""", 
                          (staff_user, staff_name, staff_pass, gmail, gmail_pass, mobile, payment_method, payment_number))
                conn.commit()
                conn.close()
                flash('পার্সোনাল আইডি সফলভাবে সেভ করা হয়েছে!')
            except:
                flash('এই ইউজার আইডিটি আগে থেকেই ডাটাবেসে রয়েছে!')
        else:
            flash('ভুল সিকিউরিটি কোড (137955) দিন!')
    return redirect('/')

@app.route('/save-admin-doc', methods=['POST'])
def save_admin_doc():
    if session.get('role') == 'admin':
        note_title = request.form.get('note_title')
        note_details = request.form.get('note_details')
        entered_pin = request.form.get('security_pin')
        date_saved = datetime.now().strftime('%d %b, %Y %I:%M %p')
        
        if entered_pin == SECURITY_PIN:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO personal_payment_notes (username, note_title, note_details, date_saved) VALUES ('Khushbu23', ?, ?, ?)", 
                      (note_title, note_details, date_saved))
            conn.commit()
            conn.close()
            flash('নোট সেভ হয়েছে!')
        else:
            flash('ভুল সিকিউরিটি পিন (137955)!')
    return redirect('/')

@app.route('/delete-admin-doc', methods=['POST'])
def delete_admin_doc():
    if session.get('role') == 'admin':
        doc_id = request.form.get('doc_id')
        entered_pin = request.form.get('security_pin')
        
        if entered_pin == SECURITY_PIN:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT note_title, note_details FROM personal_payment_notes WHERE id=?", (doc_id,))
            doc = c.fetchone()
            if doc:
                trash_detail = f"Secure Note: {doc[0]} - {doc[1]}"
                deleted_time = datetime.now().strftime('%d %b, %Y %I:%M %p')
                c.execute("INSERT INTO trash_bin (item_type, item_details, deleted_time) VALUES ('Admin Note', ?, ?)", (trash_detail, deleted_time))
                c.execute("DELETE FROM personal_payment_notes WHERE id=?", (doc_id,))
                conn.commit()
            conn.close()
            flash('নোটটি মুছে রিসাইকেল বিনে পাঠানো হয়েছে!')
        else:
            flash('ভুল সিকিউরিটি পিন (137955)! নোট ডিলিট হয়নি।')
    return redirect('/')

@app.route('/save-my-payment-note', methods=['POST'])
def save_my_payment_note():
    if 'user' in session:
        note_title = request.form.get('note_title')
        note_details = request.form.get('note_details')
        date_saved = datetime.now().strftime('%d %b, %Y')
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO personal_payment_notes (username, note_title, note_details, date_saved) VALUES (?, ?, ?, ?)", 
                  (session['user'], note_title, note_details, date_saved))
        conn.commit()
        conn.close()
        flash('নোট সেভ হয়েছে!')
    return redirect('/')

@app.route('/delete-my-payment-note', methods=['POST'])
def delete_my_payment_note():
    if 'user' in session:
        note_id = request.form.get('note_id')
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT note_title, note_details FROM personal_payment_notes WHERE id=? AND username=?", (note_id, session['user']))
        note = c.fetchone()
        if note:
            trash_detail = f"Staff Note ({session['user']}): {note[0]} - {note[1]}"
            deleted_time = datetime.now().strftime('%d %b, %Y %I:%M %p')
            c.execute("INSERT INTO trash_bin (item_type, item_details, deleted_time) VALUES ('User Note', ?, ?)", (trash_detail, deleted_time))
            c.execute("DELETE FROM personal_payment_notes WHERE id=? AND username=?", (note_id, session['user']))
            conn.commit()
        conn.close()
        flash('নোটটি মুছে ফেলা হয়েছে!')
    return redirect('/')

@app.route('/delete-staff', methods=['POST'])
def delete_staff():
    if session.get('role') == 'admin':
        username = request.form.get('username')
        entered_pin = request.form.get('security_pin')
        
        if entered_pin == SECURITY_PIN:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT staff_name, gmail, mobile FROM users WHERE username=?", (username,))
            user_data = c.fetchone()
            if user_data:
                trash_detail = f"Staff Account: ID: {username}, Name: {user_data[0]}, Gmail: {user_data[1]}"
                deleted_time = datetime.now().strftime('%d %b, %Y %I:%M %p')
                c.execute("INSERT INTO trash_bin (item_type, item_details, deleted_time) VALUES ('Staff Account', ?, ?)", (trash_detail, deleted_time))
                
                c.execute("DELETE FROM users WHERE username=?", (username,))
                c.execute("DELETE FROM assigned_tasks WHERE username=?", (username,))
                c.execute("DELETE FROM payments WHERE username=?", (username,))
                c.execute("DELETE FROM attendance WHERE username=?", (username,))
                c.execute("DELETE FROM personal_payment_notes WHERE username=?", (username,))
                conn.commit()
            conn.close()
            flash('অ্যাকাউন্ট সফলভাবে ডিলিট করে রিসাইকেল বিনে সংরক্ষণ করা হয়েছে!')
        else:
            flash('ভুল সিকিউরিটি পিন (137955)! অ্যাকাউন্ট ডিলিট করা হয়নি।')
    return redirect('/')

@app.route('/add-payment', methods=['POST'])
def add_payment():
    if session.get('role') == 'admin':
        staff_username = request.form.get('staff_name')
        month_year = request.form.get('month_year')
        amount = request.form.get('amount')
        payment_method = request.form.get('payment_method')
        payment_number = request.form.get('payment_number')
        p_date = datetime.now().strftime('%d %b, %Y')
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO payments (username, month_year, amount, payment_method, payment_number, payment_date) VALUES (?, ?, ?, ?, ?, ?)", 
                  (staff_username, month_year, amount, payment_method, payment_number, p_date))
        conn.commit()
        conn.close()
        flash('পেমেন্ট হিস্ট্রি যুক্ত করা হয়েছে!')
    return redirect('/')

@app.route('/assign-task', methods=['POST'])
def assign_task():
    if session.get('role') == 'admin':
        staff_username = request.form.get('staff_username')
        task_details = request.form.get('task_details')
        assigned_date = datetime.now().strftime('%Y-%m-%d %I:%M %p')
        
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO assigned_tasks (username, task_details, assigned_date, status) VALUES (?, ?, ?, ?)", 
                  (staff_username, task_details, assigned_date, 'Pending'))
        conn.commit()
        conn.close()
        flash('কাজ পাঠানো হয়েছে!')
    return redirect('/')

@app.route('/accept-task', methods=['POST'])
def accept_task():
    if 'user' in session:
        task_id = request.form.get('task_id')
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE assigned_tasks SET status='Accepted' WHERE id=? AND username=?", (task_id, session['user']))
        conn.commit()
        conn.close()
        flash('কাজ এক্সেপ্ট করা হয়েছে!')
    return redirect('/')

@app.route('/start-task', methods=['POST'])
def start_task():
    if 'user' in session:
        task_id = request.form.get('task_id')
        start_time = datetime.now().strftime('%I:%M %p, %d %b')
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE assigned_tasks SET start_time=? WHERE id=? AND username=?", (start_time, task_id, session['user']))
        conn.commit()
        conn.close()
        flash('কাজ শুরু হয়েছে!')
    return redirect('/')

@app.route('/finish-task', methods=['POST'])
def finish_task():
    if 'user' in session:
        task_id = request.form.get('task_id')
        end_time = datetime.now().strftime('%I:%M %p, %d %b')
        conn = get_db()
        c = conn.cursor()
        c.execute("UPDATE assigned_tasks SET end_time=?, status='Completed' WHERE id=? AND username=?", (end_time, task_id, session['user']))
        conn.commit()
        conn.close()
        flash('কাজ সম্পন্ন হয়েছে!')
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
        flash('হাজিরা সম্পন্ন!')
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
        flash('Check-Out সম্পন্ন!')
    return redirect('/')

@app.route('/send-message', methods=['POST'])
def send_message():
    if 'user' in session:
        sender = session['user']
        receiver = request.form.get('receiver')
        message = request.form.get('message', '')
        timestamp = datetime.now().strftime('%I:%M %p, %d %b')
        
        image_url = ""
        file = request.files.get('image')
        if file and file.filename != '':
            upload_dir = 'static/uploads'
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, file.filename)
            file.save(file_path)
            image_url = f"/{file_path}"
        
        if message or image_url:
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO chats (sender, receiver, message, image_url, timestamp) VALUES (?, ?, ?, ?, ?)", 
                      (sender, receiver, message, image_url, timestamp))
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
