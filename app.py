from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'CyberVault_Elite_Key'

# قاعدة البيانات الشاملة
def init_db():
    conn = sqlite3.connect('vault_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, 
                  card_number TEXT, cvv TEXT, points INTEGER DEFAULT 1000, card_color TEXT DEFAULT '#1a0505')''')
    conn.commit()
    conn.close()

init_db()

# قائمة المنتجات الكاملة (7 أدوات + 3 كورسات)
PRODUCTS = {
    "IPGRAM": 150, "SOLX": 250, "DDOS_V2": 150, "BLACK_WINDOW": 200,
    "WEB_ANALYZER": 100, "SCAN_SORS": 120, "FRIDA": 180,
    "C_HACKING": 300, "C_TRADING": 500, "C_PYTHON": 400
}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email, pwd = request.form['email'], request.form['password']
        card_no = " ".join(["".join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)])
        cvv = str(random.randint(100, 999))
        try:
            conn = sqlite3.connect('vault_pro.db')
            conn.execute('INSERT INTO users (email, password, card_number, cvv) VALUES (?, ?, ?, ?)', (email, pwd, card_no, cvv))
            conn.commit()
            session['user'] = email
            return redirect(url_for('index'))
        except: return "الحساب موجود!"
    return render_template('register.html')

@app.route('/purchase', methods=['POST'])
def purchase():
    p_id = request.json.get('product_id')
    cost = PRODUCTS.get(p_id)
    conn = sqlite3.connect('vault_pro.db')
    user = conn.execute('SELECT points FROM users WHERE email=?', (session['user'],)).fetchone()
    if user[0] >= cost:
        conn.execute('UPDATE users SET points = points - ? WHERE email=?', (cost, session['user']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "تم الشراء بنجاح! تفقد بريدك."})
    return jsonify({"status": "error", "message": "نقاط غير كافية!"})

@app.route('/update_color', methods=['POST'])
def update_color():
    color = request.json.get('color')
    conn = sqlite3.connect('vault_pro.db')
    conn.execute('UPDATE users SET card_color = ? WHERE email=?', (color, session['user']))
    conn.commit()
    return jsonify({"status": "success"})

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('register'))
    conn = sqlite3.connect('vault_pro.db')
    user = conn.execute('SELECT * FROM users WHERE email=?', (session['user'],)).fetchone()
    return render_template('index.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
