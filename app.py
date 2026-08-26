@app.route('/add-payment', methods=['POST'])
def add_payment():
    if session.get('role') == 'admin':
        # আপনার ভেতরের কোড এখানে থাকবে (যেমন পেমেন্ট যোগ করার লজিক)
        # উদাহরণস্বরূপ:
        # data = request.form
        # ...
        return redirect(url_for('some_route'))
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('index'))
