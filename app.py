from flask import Flask, render_template_string, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'

# ইউজার ও সিকিউরিটি তথ্য
USER_DATA = {
    "username": "Khushbu23",
    "password": "01751947523",
    "security_pin": "137955",
    "dob": "2000-01-01"  # প্রাথমিক জন্মতারিখ
}

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard & Security</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; max-width: 400px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type="text"], input[type="password"], input[type="date"] { width: 90%; padding: 8px; margin: 8px 0; }
        button { background: #28a745; color: white; border: none; padding: 10px 15px; border-radius: 4px; cursor: pointer; }
        .btn-danger { background: #dc3545; }
        .alert { color: red; margin-bottom: 10px; }
        .success { color: green; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="card">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        {% if not session.get('logged_in') %}
            <h2>Login</h2>
            <form method="POST" action="/login">
                <input type="text" name="username" placeholder="Username" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <button type="submit">Login</button>
            </form>
        {% else %}
            <h2>Welcome, {{ session['username'] }}!</h2>
            <p><strong>বর্তমান জন্মতারিখ:</strong> {{ dob }}</p>
            <hr>
            
            <h3>জন্মতারিখ পরিবর্তন করুন</h3>
            <form method="POST" action="/update-dob">
                <label>নতুন জন্মতারিখ:</label><br>
                <input type="date" name="new_dob" required><br>
                <label>সিকিউরিটি পিন দিন:</label><br>
                <input type="password" name="pin" placeholder="Enter Security Pin" required><br>
                <button type="submit">Update DOB</button>
            </form>
            <hr>

            <h3>ডাটা ডিলিট করুন</h3>
            <form method="POST" action="/delete-data">
                <label>সিকিউরিটি পিন দিন:</label><br>
                <input type="password" name="pin" placeholder="Enter Security Pin" required><br>
                <button type="submit" class="btn-danger">Delete Data</button>
            </form>
            <br>
            <a href="/logout">Logout</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT, dob=USER_DATA["dob"])

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == USER_DATA["username"] and password == USER_DATA["password"]:
        session['logged_in'] = True
        session['username'] = username
        flash('সফলভাবে লগইন হয়েছে!', 'success')
    else:
        flash('ভুল ইউজারনেম অথবা পাসওয়ার্ড!', 'alert')
    return redirect(url_for('home'))

@app.route('/update-dob', methods=['POST'])
def update_dob():
    pin = request.form.get('pin')
    new_dob = request.form.get('new_dob')
    
    if pin == USER_DATA["security_pin"]:
        USER_DATA["dob"] = new_dob
        flash('জন্মতারিখ সফলভাবে পরিবর্তন করা হয়েছে!', 'success')
    else:
        flash('ভুল সিকিউরিটি পিন! জন্মতারিখ পরিবর্তন করা যায়নি।', 'alert')
    return redirect(url_for('home'))

@app.route('/delete-data', methods=['POST'])
def delete_data():
    pin = request.form.get('pin')
    
    if pin == USER_DATA["security_pin"]:
        flash('ডাটা সফলভাবে ডিলিট করা হয়েছে!', 'success')
    else:
        flash('ভুল সিকিউরিটি পিন! ডিলিট করা সম্ভব নয়।', 'alert')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash('লগআউট করা হয়েছে।', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
