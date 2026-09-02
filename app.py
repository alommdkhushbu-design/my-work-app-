import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "btcl_kurigram_green_vibrant_pro_2026")
MAIN_ADMIN_USERNAME = "Khushbu23"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DB_PATH = os.path.join(BASE_DIR, 'database.db')

def db_exec(query, params=(), fetchone=False, fetchall=False, commit=False):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, params)
        res = None
        if fetchone:
            res = cur.fetchone()
        elif fetchall:
            res = cur.fetchall()
        if commit:
            conn.commit()
        conn.close()
        return res
    except Exception as e:
        print(f"Database Error: {e} | Query: {query}")
        return None

def init_db():
    db_exec('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, username TEXT UNIQUE, email TEXT, phone TEXT,
        password TEXT, raw_pass TEXT, role TEXT DEFAULT 'user', status TEXT DEFAULT 'pending',
        profile_pic TEXT DEFAULT '', added_by TEXT DEFAULT 'Khushbu23', is_deleted INTEGER DEFAULT 0,
        last_active DATETIME DEFAULT CURRENT_TIMESTAMP, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''', commit=True)
    
    db_exec('''CREATE TABLE IF NOT EXISTS phone_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT NOT NULL, mobile TEXT, service_type TEXT,
        connection_num TEXT, address TEXT, note TEXT, record_image TEXT DEFAULT '', added_by TEXT DEFAULT 'Khushbu23',
        is_deleted INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''', commit=True)
    
    db_exec('''CREATE TABLE IF NOT EXISTS activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT, action_type TEXT, details TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''', commit=True)
    
    db_exec('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, message TEXT, file_url TEXT,
        is_group INTEGER DEFAULT 0, is_read INTEGER DEFAULT 0, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''', commit=True)

    admin_check = db_exec("SELECT * FROM users WHERE username = ?", (MAIN_ADMIN_USERNAME,), fetchone=True)
    if not admin_check:
        db_exec("INSERT INTO users (name, username, email, phone, password, raw_pass, role, status) VALUES (?, ?, ?, ?, ?, ?, 'main_admin', 'active')",
                ('Md Khushbu Alom', MAIN_ADMIN_USERNAME, 'admin@btcl.com', '01751947523', generate_password_hash("01751947523"), '01751947523'), commit=True)

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম - Smart Control Desk</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: linear-gradient(135deg, #052e16 0%, #064e3b 50%, #022c22 100%); color: #ecfdf5; font-family: 'Segoe UI', sans-serif; min-height: 100vh; padding-bottom: 70px; }
        .green-vibrant-header { background: linear-gradient(90deg, #10b981 0%, #34d399 50%, #059669 100%); color: #022c22; font-weight: bold; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }
        .card-custom { background: rgba(6, 78, 59, 0.95); border: 1px solid #34d399; border-radius: 12px; box-shadow: 0 4px 20px rgba(52, 211, 153, 0.15); }
        .form-label, .form-control, .form-select { color: #fff; background-color: #022c22; border-color: #10b981; }
        .form-control:focus, .form-select:focus { background-color: #022c22; color: #fff; border-color: #34d399; box-shadow: 0 0 10px rgba(52, 211, 153, 0.5); }
        .btn-green-gold { background: linear-gradient(45deg, #10b981, #fbbf24); color: #000; font-weight: bold; border: none; }
        .btn-emerald { background: linear-gradient(45deg, #34d399, #059669); color: #000; font-weight: bold; border: none; }
        .stat-card { background: rgba(16, 185, 129, 0.2); border: 1px solid #34d399; text-align: center; cursor: pointer; padding: 10px; border-radius: 10px; transition: 0.3s; }
        .stat-card:hover { background: rgba(52, 211, 153, 0.4); transform: scale(1.02); }
        .stat-number { font-size: 18px; font-weight: bold; color: #fde047; }
        .close-cross { font-size: 1.5rem; color: #34d399; cursor: pointer; }
        .dropdown-menu-dark { background-color: #064e3b; border: 1px solid #34d399; }
        .dropdown-item { color: #ecfdf5; } .dropdown-item:hover { background-color: #10b981; color: #000; font-weight: bold; }
        .notification-badge { position: absolute; top: -5px; right: -5px; font-size: 11px; padding: 3px 7px; border-radius: 50%; background: #ef4444; color: white; font-weight: bold; }
        .chat-box { height: 380px; overflow-y: auto; background: #022c22; padding: 15px; border-radius: 8px; border: 1px solid #10b981; display: flex; flex-direction: column; }
        .message-bubble { padding: 8px 12px; border-radius: 10px; margin-bottom: 8px; max-width: 75%; word-break: break-word; }
        .msg-incoming { background: #064e3b; color: #fff; align-self: flex-start; border: 1px solid #34d399; }
        .msg-outgoing { background: #10b981; color: #000; align-self: flex-end; font-weight: 500; }
        .clickable-name { color: #fde047; cursor: pointer; text-decoration: underline; }
        .floating-add-btn { position: fixed; bottom: 25px; right: 25px; width: 65px; height: 65px; border-radius: 50%; background: linear-gradient(45deg, #10b981, #fbbf24); color: #000; font-size: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(16,185,129,0.7); border: none; z-index: 1000; cursor: pointer; }
        .status-dot { width: 10px; height: 10px; background-color: #22c55e; border-radius: 50%; display: inline-block; }
    </style>
</head>
<body>
<div class="green-vibrant-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Smart Control Desk & Messenger</small>
</div>
<div class="container py-3">
    {% if session.get('user') %}
    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div class="d-flex align-items-center gap-2 flex-wrap">
            <button class="btn btn-emerald btn-sm" onclick="showHome()"><i class="fa-solid fa-house"></i> হোম</button>
            {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
            <div class="dropdown">
                <button class="btn btn-green-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown"><i class="fa-solid fa-bars"></i> মেনু</button>
                <ul class="dropdown-menu dropdown-menu-dark">
                    <li><a class="dropdown-item" href="#" onclick="openUserListModal()"><i class="fa-solid fa-users me-2"></i>ইউজার ও এডমিন তালিকা (<span id="totalUsersCountMenu">0</span>)</a></li>
                    {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
                    <li><a class="dropdown-item" href="#" onclick="openCreateAdminModal()"><i class="fa-solid fa-user-shield me-2"></i>এডমিন তৈরি করুন</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus me-2"></i>ইউজার তৈরি করুন</a></li>
                    <li><a class="dropdown-item text-warning" href="#" onclick="openAccountRequestsModal()"><i class="fa-solid fa-user-check me-2"></i>রিকোয়েস্ট <span id="reqMenuBadge" class="badge bg-danger ms-1" style="display:none;">0</span></a></li>
                    {% endif %}
                </ul>
            </div>
            {% endif %}
            <button class="btn btn-outline-warning btn-sm position-relative fw-bold" onclick="openMessengerModal()"><i class="fa-solid fa-comments"></i> মেসেঞ্জার <span id="msgBadge" class="notification-badge" style="display:none;">0</span></button>
            <button class="btn btn-outline-success btn-sm fw-bold" onclick="openActiveUsersModal()"><i class="fa-solid fa-signal"></i> অ্যাক্টিভ <span id="activeCountBadge" class="badge bg-success ms-1">0</span></button>
        </div>
        <div class="d-flex align-items-center gap-2">
            <span class="badge bg-success border border-warning px-2 py-1"><i class="fa-solid fa-shield-halved"></i> এডমিন: <span id="totalAdminCount">0</span> জন</span>
            <div class="dropdown">
                <button class="btn btn-green-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown"><i class="fa-solid fa-circle-user"></i> প্রোফাইল</button>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                    <li><a class="dropdown-item" href="#" onclick="openProfileModal()"><i class="fa-solid fa-image me-2"></i>ছবি আপডেট</a></li>
                    {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
                    <li><a class="dropdown-item" href="#" onclick="openAdminHistoryModal()"><i class="fa-solid fa-clock-rotate-left me-2"></i>এডমিন হিস্ট্রি</a></li>
                    <li><a class="dropdown-item text-danger" href="#" onclick="openTrashBinModal()"><i class="fa-solid fa-trash-arrow-up me-2"></i>রিসাইকেল বিন</a></li>
                    {% endif %}
                </ul>
            </div>
            <a href="/logout" class="btn btn-danger btn-sm fw-bold"><i class="fa-solid fa-right-from-bracket"></i> লগআউট</a>
        </div>
    </div>

    <div class="row g-2 mb-3">
        <div class="col-md-6"><div class="input-group"><input type="text" id="searchInput" class="form-control" placeholder="নাম, মোবাইল বা সংযোগ নম্বর..." oninput="loadRecords()"><button class="btn btn-green-gold" onclick="loadRecords()"><i class="fa-solid fa-magnifying-glass"></i></button></div></div>
        <div class="col-md-6"><div class="input-group"><span class="input-group-text bg-dark text-warning">সর্ট:</span><select id="sortSelect" class="form-select" onchange="loadRecords()"><option value="id_desc">সর্বশেষ আগে</option><option value="id_asc">১ থেকে হাজার</option><option value="name_asc">নাম (A-Z)</option></select></div></div>
    </div>

    {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')"><div class="stat-card"><div class="stat-number" id="countTotal">0</div><div style="font-size:11px;">সকল</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন নাম্বার')"><div class="stat-card"><div class="stat-number" id="countTel">0</div><div style="font-size:11px;">টেলিফোন</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই নম্বর')"><div class="stat-card"><div class="stat-number" id="countBoth">0</div><div style="font-size:11px;">উভয়</div></div></div>
        <div class="col" onclick="filterService('ওয়াইফাই নাম্বার')"><div class="stat-card"><div class="stat-number" id="countWifi">0</div><div style="font-size:11px;">ওয়াইফাই</div></div></div>
    </div>
    {% endif %}

    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-success pb-2"><h5 class="text-warning mb-0">গ্রাহক নম্বরসমূহ</h5><span class="badge bg-warning text-dark" id="currentFilterLabel">সকল নম্বর</span></div>
        <div class="table-responsive"><table class="table table-dark table-striped align-middle mt-2"><thead><tr><th>নং</th><th>নাম</th><th>মোবাইল</th><th>সেবা</th><th>সংযোগ</th><th>ঠিকানা</th><th>যুক্তকারী</th>{% if session.get('user').get('role') in ['admin', 'main_admin'] %}<th>অ্যাকশন</th>{% endif %}</tr></thead><tbody id="recordsTableBody"></tbody></table></div>
    </div>

    <div id="userListSection" class="card-custom p-3 mb-4" style="display:none;">
        <div class="d-flex justify-content-between align-items-center border-bottom border-success pb-2"><h5 class="text-warning mb-0">ইউজার তালিকা</h5><button class="btn btn-sm btn-outline-warning" onclick="showHome()">বন্ধ</button></div>
        <div class="table-responsive mt-2"><table class="table table-dark table-striped align-middle"><thead><tr><th>নাম</th><th>ইউজারনেম</th><th>রোল</th><th>স্ট্যাটাস</th><th>অ্যাকশন</th></tr></thead><tbody id="userTableBody"></tbody></table></div>
    </div>

    {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
    <button class="floating-add-btn" onclick="openAddRecordModal()"><i class="fa-solid fa-plus"></i></button>
    {% endif %}
    {% else %}
    <div class="row justify-content-center mt-5"><div class="col-md-5"><div class="card-custom p-4 text-center shadow-lg"><h4 class="text-warning mb-3">লগইন করুন</h4><form action="/login" method="POST"><div class="mb-3 text-start"><label class="form-label">ইউজারনেম / জিমেইল</label><input type="text" name="username" class="form-control" required></div><div class="mb-3 text-start"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div><button type="submit" class="btn btn-green-gold w-100">প্রবেশ</button></form><div class="mt-3"><button class="btn btn-outline-warning btn-sm" onclick="new bootstrap.Modal(document.getElementById('registerModal')).show()">রেজিস্ট্রেশন রিকোয়েস্ট</button></div></div></div></div>
    {% endif %}
</div>

<!-- Modals -->
<div class="modal fade" id="activeUsersModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning">অ্যাক্টিভ ইউজারগণ</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><div class="modal-body" id="activeUsersListModalBody"></div></div></div></div>
<div class="modal fade" id="customerDetailsModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning">বিস্তারিত তথ্য</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><div class="modal-body" id="customerDetailsBody"></div></div></div></div>
<div class="modal fade" id="adminHistoryModal" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning">এডমিন হিস্ট্রি</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><div class="modal-body"><table class="table table-dark table-striped"><thead><tr><th>নাম</th><th>ইউজারনেম</th><th>শেষ অ্যাক্টিভ</th><th>মোট</th></tr></thead><tbody id="adminHistoryTableBody"></tbody></table></div></div></div></div>
<div class="modal fade" id="accountRequestsModal" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning">রিকোয়েস্ট তালিকা</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><div class="modal-body"><table class="table table-dark table-striped"><thead><tr><th>নাম</th><th>ইউজার</th><th>ইমেইল</th><th>অ্যাকশন</th></tr></thead><tbody id="requestTableBody"></tbody></table></div></div></div></div>
<div class="modal fade" id="registerModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning">রেজিস্ট্রেশন</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><form action="/api/register_request" method="POST" class="modal-body"><div class="mb-2"><input type="text" name="name" class="form-control" placeholder="নাম" required></div><div class="mb-2"><input type="text" name="username" class="form-control" placeholder="ইউজারনেম" required></div><div class="mb-2"><input type="email" name="email" class="form-control" placeholder="জিমেইল" required></div><div class="mb-2"><input type="text" name="phone" class="form-control" placeholder="মোবাইল"></div><div class="mb-3"><input type="password" name="password" class="form-control" placeholder="পাসওয়ার্ড" required></div><button type="submit" class="btn btn-green-gold w-100">পাঠান</button></form></div></div></div>
<div class="modal fade" id="messengerModal" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning">মেসেঞ্জার</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><div class="modal-body"><div class="row"><div class="col-md-4 border-end border-success"><div class="d-flex gap-1 mb-2"><button class="btn btn-sm btn-green-gold w-50" onclick="switchChat('users')">ইনবক্স</button><button class="btn btn-sm btn-emerald w-50" onclick="switchChat('group')">গ্রুপ</button></div><div id="chatUserList" style="max-height:350px; overflow-y:auto;"></div></div><div class="col-md-8 d-flex flex-column"><div id="activeChatTitle" class="text-warning fw-bold mb-2 pb-1 border-bottom border-success">সিলেক্ট করুন</div><div id="chatMessages" class="chat-box mb-2"></div><form id="chatForm" onsubmit="sendMessage(event)" class="input-group" style="display:none;"><input type="text" id="chatInput" class="form-control" placeholder="মেসেজ..."><input type="file" id="chatFile" class="d-none"><button type="submit" class="btn btn-green-gold"><i class="fa-solid fa-paper-plane"></i></button></form></div></div></div></div></div></div>
<div class="modal fade" id="recordModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning" id="recordModalTitle">নম্বর যোগ</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><form id="recordForm" onsubmit="saveRecord(event)" class="modal-body row g-2"><input type="hidden" id="rec_id" name="id"><div class="col-12"><input type="text" id="rec_name" name="customer_name" class="form-control" placeholder="গ্রাহকের নাম" required></div><div class="col-md-6"><input type="text" id="rec_mobile" name="mobile" class="form-control" placeholder="মোবাইল"></div><div class="col-md-6"><select id="rec_service" name="service_type" class="form-select"><option value="টেলিফোন নাম্বার">টেলিফোন</option><option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই</option><option value="ওয়াইফাই নাম্বার">ওয়াইফাই</option></select></div><div class="col-md-6"><input type="text" id="rec_conn" name="connection_num" class="form-control" placeholder="সংযোগ নম্বর"></div><div class="col-md-6"><input type="text" id="rec_address" name="address" class="form-control" placeholder="ঠিকানা"></div><div class="col-12"><input type="text" id="rec_note" name="note" class="form-control" placeholder="নোট"></div><div class="col-12"><input type="file" name="record_image_gallery" class="form-control" accept="image/*"></div><div class="col-12 text-end mt-2"><button type="submit" class="btn btn-green-gold">সেভ</button></div></form></div></div></div>
<div class="modal fade" id="createUserModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-warning" id="createUserModalTitle">ইউজার তৈরি</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><form action="/api/create_user" method="POST" class="modal-body"><input type="hidden" id="target_role_input" name="role" value="user"><div class="mb-2"><input type="text" name="name" class="form-control" placeholder="নাম" required></div><div class="mb-2"><input type="text" name="username" class="form-control" placeholder="ইউজারনেম" required></div><div class="mb-2"><input type="email" name="email" class="form-control" placeholder="জিমেইল"></div><div class="mb-2"><input type="text" name="phone" class="form-control" placeholder="মোবাইল"></div><div class="mb-3"><input type="password" name="password" class="form-control" placeholder="পাসওয়ার্ড" required></div><button type="submit" class="btn btn-green-gold w-100">তৈরি করুন</button></form></div></div></div>
<div class="modal fade" id="profileModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content card-custom text-center"><div class="modal-header border-success"><h5 class="modal-title text-warning">প্রোফাইল ছবি</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><form action="/update_profile_pic" method="POST" enctype="multipart/form-data" class="modal-body"><div class="mb-3 text-start"><input type="file" name="profile_pic" class="form-control" accept="image/*" required></div><button type="submit" class="btn btn-green-gold w-100">আপডেট</button></form></div></div></div>
<div class="modal fade" id="trashBinModal" tabindex="-1"><div class="modal-dialog modal-lg"><div class="modal-content card-custom"><div class="modal-header border-success"><h5 class="modal-title text-danger">রিসাইকেল বিন</h5><i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i></div><div class="modal-body"><table class="table table-dark table-striped"><thead><tr><th>নাম</th><th>অ্যাকশন</th></tr></thead><tbody id="trashTableBody"></tbody></table></div></div></div></div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let currentFilter = '', currentChatUser = '', currentChatTab = 'users';
document.addEventListener("DOMContentLoaded", () => {
    {% if session.get('user') %}
    loadRecords(); loadStats(); loadAdminCount(); loadActiveCount(); loadUsersMenuCount();
    setInterval(() => fetch('/api/ping').catch(()=>{}), 10000);
    setInterval(pollData, 4000);
    {% endif %}
});
function loadStats() {
    fetch('/api/stats').then(res => res.json()).then(d => {
        if(document.getElementById('countTotal')) {
            document.getElementById('countTotal').innerText = d.total;
            document.getElementById('countTel').innerText = d.tel;
            document.getElementById('countBoth').innerText = d.both;
            document.getElementById('countWifi').innerText = d.wifi;
        }
    });
}
function loadAdminCount() { fetch('/api/admin_count').then(r => r.json()).then(d => { if(document.getElementById('totalAdminCount')) document.getElementById('totalAdminCount').innerText = d.count; }); }
function loadUsersMenuCount() { fetch('/api/users').then(r => r.json()).then(d => { if(document.getElementById('totalUsersCountMenu')) document.getElementById('totalUsersCountMenu').innerText = d.length; }); }
function loadActiveCount() { fetch('/api/chat_users').then(r => r.json()).then(d => { document.getElementById('activeCountBadge').innerText = d.filter(u => u.is_online).length; }); }
function openActiveUsersModal() {
    fetch('/api/chat_users').then(r => r.json()).then(d => {
        let b = document.getElementById('activeUsersListModalBody'); b.innerHTML = '';
        d.filter(u => u.is_online).forEach(u => { b.innerHTML += `<div class="d-flex justify-content-between p-2 border-bottom border-success"><span>${u.name} (@${u.username})</span><span class="status-dot"></span></div>`; });
        new bootstrap.Modal(document.getElementById('activeUsersModal')).show();
    });
}
function showHome() { document.getElementById('recordsSection').style.display = 'block'; document.getElementById('userListSection').style.display = 'none'; }
function filterService(t) { currentFilter = t; document.getElementById('currentFilterLabel').innerText = t || 'সকল নম্বর'; loadRecords(); }
function loadRecords() {
    let s = document.getElementById('searchInput').value, sort = document.getElementById('sortSelect').value;
    fetch(`/api/records?search=${encodeURIComponent(s)}&sort=${sort}&service=${encodeURIComponent(currentFilter)}`).then(r => r.json()).then(d => {
        let tb = document.getElementById('recordsTableBody'); tb.innerHTML = '';
        if(!d || d.length === 0) { tb.innerHTML = `<tr><td colspan="8" class="text-center text-muted">রেকর্ড নেই</td></tr>`; return; }
        d.forEach((r, i) => {
            tb.innerHTML += `<tr><td>${i+1}</td><td class="clickable-name" onclick="openCustomerDetails(${r.id})">${r.customer_name}</td><td>${r.mobile||''}</td><td><span class="badge bg-success">${r.service_type}</span></td><td>${r.connection_num||''}</td><td>${r.address||''}</td><td><small class="text-warning">${r.added_by}</small></td>{% if session.get('user').get('role') in ['admin', 'main_admin'] %}<td><button class="btn btn-sm btn-outline-danger" onclick="deleteRecord(${r.id})"><i class="fa-solid fa-trash"></i></button></td>{% endif %}</tr>`;
        });
    });
}
function openUserListModal() {
    document.getElementById('recordsSection').style.display = 'none'; document.getElementById('userListSection').style.display = 'block';
    fetch('/api/users').then(r => r.json()).then(d => {
        let tb = document.getElementById('userTableBody'); tb.innerHTML = '';
        d.forEach(u => {
            let btn = u.username !== '{{ MAIN_ADMIN_USERNAME }}' ? `<button class="btn btn-danger btn-sm" onclick="deleteUser(${u.id})">ডিলিট</button>` : `<span class="badge bg-success">মূল এডমিন</span>`;
            tb.innerHTML += `<tr><td>${u.name}</td><td>${u.username}</td><td><span class="badge bg-warning text-dark">${u.role}</span></td><td><span class="badge bg-success">${u.status}</span></td><td>${btn}</td></tr>`;
        });
    });
}
function deleteUser(id) { if(confirm('ডিলিট করবেন?')) fetch(`/api/delete_user/${id}`, {method:'POST'}).then(r=>r.json()).then(d=>{if(d.success) openUserListModal();}); }
function openCreateUserModal() { document.getElementById('target_role_input').value='user'; document.getElementById('createUserModalTitle').innerText='ইউজার তৈরি'; new bootstrap.Modal(document.getElementById('createUserModal')).show(); }
function openCreateAdminModal() { document.getElementById('target_role_input').value='admin'; document.getElementById('createUserModalTitle').innerText='এডমিন তৈরি'; new bootstrap.Modal(document.getElementById('createUserModal')).show(); }
function openAddRecordModal() { document.getElementById('recordForm').reset(); document.getElementById('rec_id').value=''; new bootstrap.Modal(document.getElementById('recordModal')).show(); }
function saveRecord(e) {
    e.preventDefault();
    fetch('/api/save_record', {method:'POST', body:new FormData(document.getElementById('recordForm'))}).then(r=>r.json()).then(d=>{
        if(d.success) { bootstrap.Modal.getInstance(document.getElementById('recordModal')).hide(); loadRecords(); loadStats(); }
    });
}
function deleteRecord(id) { if(confirm('রিসাইকেল বিনে পাঠাবেন?')) fetch(`/api/delete_record/${id}`, {method:'POST'}).then(r=>r.json()).then(d=>{if(d.success){loadRecords();loadStats();}}); }
function openMessengerModal() { new bootstrap.Modal(document.getElementById('messengerModal')).show(); switchChat('users'); }
function switchChat(t) { currentChatTab = t; let l = document.getElementById('chatUserList'); l.innerHTML = '';
    if(t === 'users') {
        fetch('/api/chat_users').then(r=>r.json()).then(d=>{ d.forEach(u=>{ l.innerHTML += `<button class="list-group-item list-group-item-action bg-transparent text-light border-success d-flex justify-content-between" onclick="selectChat('${u.username}', '${u.name}')"><span>${u.name}</span><span class="${u.is_online?'status-dot':''}"></span></button>`; }); });
    } else { selectChat('group', 'গ্রুপ চ্যাট'); }
}
function selectChat(u, n) { currentChatUser = u; document.getElementById('activeChatTitle').innerText = n; document.getElementById('chatForm').style.display = 'flex'; loadMessages(); }
function loadMessages() {
    if(!currentChatUser) return;
    let g = currentChatUser === 'group'?1:0, t = g?'':currentChatUser;
    fetch(`/api/get_messages?is_group=${g}&target=${t}`).then(r=>r.json()).then(d=>{
        let b = document.getElementById('chatMessages'); b.innerHTML = '';
        d.forEach(m => {
            let out = m.sender === '{{ session.get("user", {}).get("username") }}';
            b.innerHTML += `<div class="message-bubble ${out?'msg-outgoing':'msg-incoming'}"><div style="font-size:10px; opacity:0.8;">${m.sender}</div><div>${m.message||''}</div></div>`;
        });
        b.scrollTop = b.scrollHeight;
    });
}
function sendMessage(e) {
    e.preventDefault();
    let fd = new FormData(); fd.append('message', document.getElementById('chatInput').value);
    fd.append('is_group', currentChatUser === 'group'?1:0);
    if(currentChatUser !== 'group') fd.append('receiver', currentChatUser);
    fetch('/api/send_message', {method:'POST', body:fd}).then(r=>r.json()).then(d=>{if(d.success){document.getElementById('chatInput').value=''; loadMessages();}});
}
function openCustomerDetails(id) {
    fetch(`/api/record_details/${id}`).then(r=>r.json()).then(d=>{
        document.getElementById('customerDetailsBody').innerHTML = `<p><b>নাম:</b> ${d.customer_name}</p><p><b>মোবাইল:</b> ${d.mobile||'নেই'}</p><p><b>সেবা:</b> ${d.service_type}</p><p><b>সংযোগ:</b> ${d.connection_num||'নেই'}</p><p><b>ঠিকানা:</b> ${d.address||'নেই'}</p>`;
        new bootstrap.Modal(document.getElementById('customerDetailsModal')).show();
    });
}
function openAdminHistoryModal() {
    fetch('/api/admin_history').then(r=>r.json()).then(d=>{
        let tb = document.getElementById('adminHistoryTableBody'); tb.innerHTML = '';
        d.forEach(h => { tb.innerHTML += `<tr><td>${h.name}</td><td>${h.username}</td><td>${h.last_active}</td><td>${h.total_added}</td></tr>`; });
        new bootstrap.Modal(document.getElementById('adminHistoryModal')).show();
    });
}
function openAccountRequestsModal() {
    fetch('/api/account_requests').then(r=>r.json()).then(d=>{
        let tb = document.getElementById('requestTableBody'); tb.innerHTML = '';
        d.forEach(r => { tb.innerHTML += `<tr><td>${r.name}</td><td>${r.username}</td><td>${r.email}</td><td><button class="btn btn-success btn-sm" onclick="approveUser(${r.id})">অনুমোদন</button></td></tr>`; });
        new bootstrap.Modal(document.getElementById('accountRequestsModal')).show();
    });
}
function approveUser(id) { fetch(`/api/approve_user/${id}`, {method:'POST'}).then(r=>r.json()).then(d=>{if(d.success) openAccountRequestsModal();}); }
function openTrashBinModal() {
    fetch('/api/trash_records').then(r=>r.json()).then(d=>{
        let tb = document.getElementById('trashTableBody'); tb.innerHTML = '';
        d.forEach(r => { tb.innerHTML += `<tr><td>${r.customer_name}</td><td><button class="btn btn-success btn-sm" onclick="restoreRecord(${r.id})">রিস্টোর</button></td></tr>`; });
        new bootstrap.Modal(document.getElementById('trashBinModal')).show();
    });
}
function restoreRecord(id) { fetch(`/api/restore_record/${id}`, {method:'POST'}).then(r=>r.json()).then(d=>{if(d.success) openTrashBinModal();}); }
function pollData() {
    fetch('/api/notifications_count').then(r=>r.json()).then(d=>{
        let mb = document.getElementById('msgBadge'); if(mb){ mb.innerText = d.messages; mb.style.display = d.messages>0?'block':'none'; }
        let rb = document.getElementById('reqMenuBadge'); if(rb){ rb.innerText = d.requests; rb.style.display = d.requests>0?'inline-block':'none'; }
    });
}
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    u = db_exec("SELECT * FROM users WHERE (username = ? OR email = ?) AND is_deleted = 0", (username, username), fetchone=True)
    if u and check_password_hash(u['password'], password):
        if u['status'] != 'active': return "অ্যাকাউন্ট অনুমোদিত নয়!", 403
        session['user'] = dict(u)
        return redirect(url_for('index'))
    return "ভুল তথ্য", 400

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('index'))

@app.route('/api/ping')
def ping():
    if 'user' in session:
        db_exec("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (session['user']['username'],), commit=True)
    return jsonify({"status": "alive"})

@app.route('/api/stats')
def api_stats():
    t_res = db_exec("SELECT COUNT(*) FROM phone_records WHERE is_deleted = 0", fetchone=True)
    tel_res = db_exec("SELECT COUNT(*) FROM phone_records WHERE service_type = 'টেলিফোন নাম্বার' AND is_deleted = 0", fetchone=True)
    both_res = db_exec("SELECT COUNT(*) FROM phone_records WHERE service_type = 'টেলিফোন+ওয়াইফাই নম্বর' AND is_deleted = 0", fetchone=True)
    wifi_res = db_exec("SELECT COUNT(*) FROM phone_records WHERE service_type = 'ওয়াইফাই নাম্বার' AND is_deleted = 0", fetchone=True)
    
    return jsonify({
        "total": t_res[0] if t_res else 0,
        "tel": tel_res[0] if tel_res else 0,
        "both": both_res[0] if both_res else 0,
        "wifi": wifi_res[0] if wifi_res else 0
    })

@app.route('/api/admin_count')
def api_admin_count():
    res = db_exec("SELECT COUNT(*) FROM users WHERE role IN ('admin', 'main_admin') AND is_deleted = 0", fetchone=True)
    return jsonify({"count": res[0] if res else 0})

@app.route('/api/records')
def api_records():
    search, sort, service = request.args.get('search', ''), request.args.get('sort', 'id_desc'), request.args.get('service', '')
    q = "SELECT * FROM phone_records WHERE is_deleted = 0"
    p = []
    if search:
        q += " AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ?)"
        p.extend([f"%{search}%"]*3)
    if service:
        q += " AND service_type = ?"
        p.append(service)
    q += " ORDER BY id " + ("ASC" if sort == 'id_asc' else "DESC")
    rows = db_exec(q, p, fetchall=True)
    return jsonify([dict(r) for r in rows] if rows else [])

@app.route('/api/save_record', methods=['POST'])
def save_record():
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']: return jsonify({'success': False}), 403
    f = request.files.get('record_image_gallery')
    img_url = ''
    if f and f.filename:
        fn = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        img_url = f"static/uploads/{fn}"
    db_exec("INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note, record_image, added_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (request.form.get('customer_name'), request.form.get('mobile', ''), request.form.get('service_type'), request.form.get('connection_num', ''), request.form.get('address', ''), request.form.get('note', ''), img_url, session['user']['username']), commit=True)
    return jsonify({'success': True})

@app.route('/api/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']: return jsonify({'success': False}), 403
    db_exec("UPDATE phone_records SET is_deleted = 1 WHERE id = ?", (id,), commit=True)
    return jsonify({'success': True})

@app.route('/api/record_details/<int:id>')
def record_details(id):
    r = db_exec("SELECT * FROM phone_records WHERE id = ?", (id,), fetchone=True)
    return jsonify(dict(r) if r else {})

@app.route('/api/users')
def api_users():
    if 'user' not in session: return jsonify([])
    rows = db_exec("SELECT id, name, username, email, role, status FROM users WHERE is_deleted = 0", fetchall=True)
    return jsonify([dict(u) for u in rows] if rows else [])

@app.route('/api/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']: return jsonify({'success': False}), 403
    db_exec("UPDATE users SET is_deleted = 1 WHERE id = ?", (user_id,), commit=True)
    return jsonify({'success': True})

@app.route('/api/create_user', methods=['POST'])
def create_user():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return redirect(url_for('index'))
    db_exec("INSERT INTO users (name, username, email, phone, password, raw_pass, role, status, added_by) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)",
            (request.form.get('name'), request.form.get('username'), request.form.get('email', ''), request.form.get('phone', ''), generate_password_hash(request.form.get('password')), request.form.get('password'), request.form.get('role', 'user'), session['user']['username']), commit=True)
    return redirect(url_for('index'))

@app.route('/api/register_request', methods=['POST'])
def register_request():
    db_exec("INSERT INTO users (name, username, email, phone, password, raw_pass, role, status, added_by) VALUES (?, ?, ?, ?, ?, ?, 'user', 'pending', 'Self')",
            (request.form.get('name'), request.form.get('username'), request.form.get('email'), request.form.get('phone'), generate_password_hash(request.form.get('password')), request.form.get('password')), commit=True)
    return redirect(url_for('index'))

@app.route('/api/account_requests')
def account_requests():
    if session.get('user', {}).get('username') != MAIN_ADMIN_USERNAME: return jsonify([])
    rows = db_exec("SELECT id, name, username, email FROM users WHERE status = 'pending' AND is_deleted = 0", fetchall=True)
    return jsonify([dict(r) for r in rows] if rows else [])

@app.route('/api/approve_user/<int:id>', methods=['POST'])
def approve_user(id):
    if session.get('user', {}).get('username') != MAIN_ADMIN_USERNAME: return jsonify({'success': False}), 403
    db_exec("UPDATE users SET status = 'active' WHERE id = ?", (id,), commit=True)
    return jsonify({'success': True})

@app.route('/api/chat_users')
def chat_users():
    if 'user' not in session: return jsonify([])
    now = datetime.now()
    res = []
    rows = db_exec("SELECT username, name, last_active FROM users WHERE is_deleted = 0 AND status = 'active'", fetchall=True)
    if rows:
        for u in rows:
            ud = dict(u)
            online = False
            try:
                if u['last_active'] and (now - datetime.strptime(u['last_active'], '%Y-%m-%d %H:%M:%S')).total_seconds() < 30: online = True
            except: pass
            ud['is_online'] = online
            res.append(ud)
    return jsonify(res)

@app.route('/api/get_messages')
def get_messages():
    if 'user' not in session: return jsonify([])
    g, t, un = int(request.args.get('is_group', 0)), request.args.get('target'), session['user']['username']
    if g:
        rows = db_exec("SELECT sender, receiver, message, timestamp FROM messages WHERE is_group = 1 ORDER BY timestamp ASC", fetchall=True)
    else:
        rows = db_exec("SELECT sender, receiver, message, timestamp FROM messages WHERE is_group = 0 AND ((sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)) ORDER BY timestamp ASC", (un, t, t, un), fetchall=True)
    return jsonify([{'sender': r[0], 'receiver': r[1], 'message': r[2], 'timestamp': r[3]} for r in rows] if rows else [])

@app.route('/api/send_message', methods=['POST'])
def send_message():
    if 'user' not in session: return jsonify({'success': False}), 403
    db_exec("INSERT INTO messages (sender, receiver, message, is_group) VALUES (?, ?, ?, ?)",
            (session['user']['username'], request.form.get('receiver', ''), request.form.get('message', ''), int(request.form.get('is_group', 0))), commit=True)
    return jsonify({'success': True})

@app.route('/api/notifications_count')
def notifications_count():
    if 'user' not in session: return jsonify({'messages': 0, 'requests': 0})
    un = session['user']['username']
    mc_res = db_exec("SELECT COUNT(*) FROM messages WHERE receiver = ? AND is_read = 0", (un,), fetchone=True)
    rc_res = db_exec("SELECT COUNT(*) FROM users WHERE status = 'pending' AND is_deleted = 0", fetchone=True) if un == MAIN_ADMIN_USERNAME else [0]
    return jsonify({
        'messages': mc_res[0] if mc_res else 0,
        'requests': rc_res[0] if rc_res else 0
    })

@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    f = request.files.get('profile_pic')
    if 'user' in session and f and f.filename:
        fn = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        pic = f"static/uploads/{fn}"
        db_exec("UPDATE users SET profile_pic = ? WHERE username = ?", (pic, session['user']['username']), commit=True)
        updated_user = db_exec("SELECT * FROM users WHERE username = ?", (session['user']['username'],), fetchone=True)
        if updated_user:
            session['user'] = dict(updated_user)
    return redirect(url_for('index'))

@app.route('/api/admin_history')
def admin_history():
    if session.get('user', {}).get('username') != MAIN_ADMIN_USERNAME: return jsonify([])
    res = []
    admins = db_exec("SELECT name, username, last_active FROM users WHERE role IN ('admin', 'main_admin') AND is_deleted = 0", fetchall=True)
    if admins:
        for a in admins:
            ad = dict(a)
            tot = db_exec("SELECT COUNT(*) FROM phone_records WHERE added_by = ?", (a['username'],), fetchone=True)
            ad['total_added'] = tot[0] if tot else 0
            res.append(ad)
    return jsonify(res)

@app.route('/api/trash_records')
def trash_records():
    if session.get('user', {}).get('username') != MAIN_ADMIN_USERNAME: return jsonify([])
    rows = db_exec("SELECT id, customer_name FROM phone_records WHERE is_deleted = 1", fetchall=True)
    return jsonify([dict(r) for r in rows] if rows else [])

@app.route('/api/restore_record/<int:id>', methods=['POST'])
def restore_record(id):
    if session.get('user', {}).get('username') != MAIN_ADMIN_USERNAME: return jsonify({'success': False}), 403
    db_exec("UPDATE phone_records SET is_deleted = 0 WHERE id = ?", (id,), commit=True)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)