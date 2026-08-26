from flask import Flask, render_template, request, redirect, url_for, session, flash

# ১. ফ্লাস্ক অ্যাপ ইনিশিয়ালাইজেশন (সবার উপরে থাকতে হবে)
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # সেশন সিকিউরিটির জন্য একটি সিক্রেট কি দিন

# ২. হোম বা লগইন রাউট
@app.route('/')
def index():
    return render_template('index.html')

# ৩. অ্যাড পেমেন্ট রাউট (যেখানে আগে সিনট্যাক্স এরর হয়েছিল)
@app.route('/add-payment', methods=['POST'])
def add_payment():
    # কমা (,) এর বদলে কোলন (:) ব্যবহার করতে হবে
    if session.get('role') == 'admin':
        # পেমেন্ট প্রসেস করার কোড এখানে লিখবেন
        flash('Payment added successfully!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))

# ৪. অ্যাপ রান করার কোড
if __name__ == '__main__':
    app.run(debug=True)
