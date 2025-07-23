from flask import Flask, render_template, request, redirect, session, flash, jsonify
import json, random, os

app = Flask(__name__)
app.secret_key = 'unibanksecret'

# File to store user data
USER_FILE = 'users.json'

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def generate_account():
    return str(random.randint(1000000000, 9999999999))

def generate_ifsc():
    return "UNI000" + str(random.randint(1000, 9999))

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['name']
        aadhar = request.form['aadhar']
        mobile = request.form['mobile']
        gmail = request.form['gmail']
        age = request.form['age']
        gender = request.form['gender']
        pin = request.form['pin']

        users = load_users()
        if mobile in users:
            flash("Mobile number already registered")
            return redirect('/register')

        account_no = generate_account()
        ifsc = generate_ifsc()

        users[mobile] = {
            'name': full_name,
            'aadhar': aadhar,
            'gmail': gmail,
            'mobile': mobile,
            'pin': pin,
            'age': age,
            'gender': gender,
            'balance': 0,
            'account_no': account_no,
            'ifsc': ifsc,
            'transactions': []
        }

        save_users(users)
        flash("Registration successful. Please log in.")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile']
        pin = request.form['pin']
        users = load_users()
        if mobile in users and users[mobile]['pin'] == pin:
            session['user'] = mobile
            return redirect('/dashboard')
        flash("Invalid login credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    user_data = load_users()[session['user']]
    return render_template('dashboard.html', user=user_data)

@app.route('/deposit', methods=['POST'])
def deposit():
    amount = int(request.form['amount'])
    users = load_users()
    user = users[session['user']]
    user['balance'] += amount
    user['transactions'].insert(0, f"Deposited ₹{amount}")
    save_users(users)
    flash("Successfully deposited")
    return redirect('/dashboard')

@app.route('/withdraw', methods=['POST'])
def withdraw():
    amount = int(request.form['amount'])
    users = load_users()
    user = users[session['user']]
    if user['balance'] >= amount:
        user['balance'] -= amount
        user['transactions'].insert(0, f"Withdrew ₹{amount}")
        save_users(users)
        flash("Successfully withdrawn")
    else:
        flash("Insufficient balance")
    return redirect('/dashboard')

@app.route('/transfer', methods=['POST'])
def transfer():
    receiver_acc = request.form['receiver_account']
    receiver_ifsc = request.form['receiver_ifsc']
    amount = int(request.form['amount'])

    users = load_users()
    sender = users[session['user']]

    # Find receiver by account number and IFSC
    receiver_key = None
    for key, u in users.items():
        if u['account_no'] == receiver_acc and u['ifsc'] == receiver_ifsc:
            receiver_key = key
            break

    if receiver_key:
        if sender['balance'] >= amount:
            sender['balance'] -= amount
            users[receiver_key]['balance'] += amount

            sender['transactions'].insert(0, f"Transferred ₹{amount} to {users[receiver_key]['name']} ({receiver_acc})")
            users[receiver_key]['transactions'].insert(0, f"Received ₹{amount} from {sender['name']} ({sender['account_no']})")

            save_users(users)
            flash("Transaction Successful")
        else:
            flash("Insufficient Balance")
    else:
        flash("Receiver account not found")

    return redirect('/dashboard')

@app.route('/get_name_by_account', methods=['POST'])
def get_name_by_account():
    data = request.json
    acc = data.get('account_no')
    users = load_users()
    for user in users.values():
        if user['account_no'] == acc:
            return jsonify({"name": user['name']})
    return jsonify({"name": ""})

@app.route('/change_pin', methods=['POST'])
def change_pin():
    old_pin = request.form['old_pin']
    new_pin = request.form['new_pin']
    users = load_users()
    user = users[session['user']]
    if user['pin'] == old_pin:
        user['pin'] = new_pin
        save_users(users)
        flash("PIN changed successfully")
    else:
        flash("Old PIN is incorrect")
    return redirect('/dashboard')

@app.route('/joint_account', methods=['POST'])
def joint_account():
    name = request.form['joint_name']
    aadhar = request.form['joint_aadhar']
    flash(f"Joint account request for {name} with Aadhar {aadhar} submitted.")
    return redirect('/dashboard')

@app.route('/update_info', methods=['POST'])
def update_info():
    users = load_users()
    user = users[session['user']]
    if request.form.get('new_mobile'):
        user['mobile'] = request.form['new_mobile']
    if request.form.get('new_gmail'):
        user['gmail'] = request.form['new_gmail']
    save_users(users)
    flash("Information updated")
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mobile = request.form['mobile'].strip()
        pin = request.form['pin'].strip()

        if len(mobile) != 10 or not mobile.isdigit():
            flash("❌ Invalid Mobile Number. It should be 10 digits.")
            return redirect('/login')

        users = load_users()
        if mobile not in users:
            flash("❌ Mobile number not registered.")
            return redirect('/login')

        if users[mobile]['pin'] != pin:
            flash("❌ Incorrect PIN. Please try again.")
            return redirect('/login')

        session['user'] = mobile
        return redirect('/dashboard')
    
    return render_template('login.html')
