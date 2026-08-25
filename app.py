from flask import Flask, render_template_string, request, session, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'khushbu_secret_key'

USER_DATA = {
    "username": "Khushbu23",
    "password": "01751947523",
    "security_pin": "137955",
    "dob": "2000-01-01"
}

SAVED_ACCOUNTS = []

HTML_LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; margin: 20px; background: #f4f4f9; }
        .card { background: white; padding: 20px; border-radius: 8px; max-width: 400px; margin: 0 auto; }
        input { width: 90%; padding: 8px; margin: 5px 0; }
        button { background: #28a745; color: white; border: none; padding: 10px; width: 95%; cursor: pointer; }
        .btn-del { background: #dc3545; }
        table { width: 100%; margin-top: 10px; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; }
    </style>
</head>
<body>
    <div class="card">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for msg in messages %}<p style="color:blue;">{{ msg }}</p>{% endfor %}
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
            <h3>Welcome, {{ session['username'] }}</h3>
            <p><strong>DOB:</strong> {{ dob }}</p>
            <a href="/logout">Logout</a>
            <hr>
            <h4>Add Gmail / ID</h4>
            <form method="POST" action="/add">
                <input type="email" name="email" placeholder="Gmail" required><br>
                <input type="text" name="acc_password" placeholder="Password / Note" required><br>
                <button type="submit">Save Data</button>
            </form>
            <hr>
            <h4>Saved Accounts</h4>
            {% if accounts %}
            <table>
                <tr><th>Gmail</th><th>Pass/Note</th></tr>
                {% for acc in accounts %}
                <tr><td>{{ acc.email }}</td><td>{{ acc.password }}</td></tr>
                {% endfor %}
            </table>
            {% else %}
            <p>No data saved yet.</p>
            {% endif %}
            <hr>
            <h4>Change DOB (Need Security PIN)</h4>
            <form method="POST" action="/update-dob">
                <input type="date" name="new_dob" required><br>
                <input type="password" name="pin" placeholder="Enter Security PIN" required><br>
                <button type="submit">Update DOB</button>
            </form>
            <hr>
            <h4>Delete All Data (Need Security PIN)</h4>
            <form method="POST" action="/delete">
                <input type="password" name="pin" placeholder="Enter Security PIN" required><br>
                <button type="submit" class="btn-del">Delete All</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT, dob=USER_DATA["dob"], accounts=SAVED_ACCOUNTS)

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('username') == USER_DATA["username"] and request.form.get('password') == USER_DATA["password"]:
        session['logged_in'] = True
        session['username'] = USER_DATA["username"]
    else:
        flash('Invalid Username/Password!')
    return redirect('/')

@app.route('/add', methods=['POST'])
def add():
    if session.get('logged_in'):
        SAVED_ACCOUNTS.append({"email": request.form.get('email'), "password": request.form.get('acc_password')})
        flash('Gmail saved successfully!')
    return redirect('/')

@app.route('/update-dob', methods=['POST'])
def update_dob():
    if request.form.get('pin') == USER_DATA["security_pin"]:
        USER_DATA["dob"] = request.form.get('new_dob')
        flash('DOB updated!')
    else:
        flash('Wrong PIN!')
    return redirect('/')

@app.route('/delete', methods=['POST'])
def delete():
    if request.form.get('pin') == USER_DATA["security_pin"]:
        SAVED_ACCOUNTS.clear()
        flash('All data deleted!')
    else:
        flash('Wrong PIN!')
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run()
