from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'WXL_E_SECRET_KEY'

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  points INTEGER DEFAULT 100, ref_code TEXT, 
                  last_gift TEXT, invited_by TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login_page'))
    
    conn = sqlite3.connect('database.db')
    user_data = conn.execute('SELECT points, ref_code FROM users WHERE username=?', (session['user'],)).fetchone()
    conn.close()
    
    return render_template('index.html', points=user_data[0], ref_code=user_data[1])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        ref = request.args.get('ref') # كود الشخص الذي دعا المستخدم
        
        try:
            conn = sqlite3.connect('database.db')
            new_ref = str(uuid.uuid4())[:8]
            conn.execute('INSERT INTO users (username, password, ref_code, invited_by) VALUES (?, ?, ?, ?)', 
                         (user, pwd, new_ref, ref))
            
            # إذا كان هناك دعوة، نعطي الداعي 50 نقطة
            if ref:
                conn.execute('UPDATE users SET points = points + 50 WHERE ref_code = ?', (ref,))
                
            conn.commit()
            session['user'] = user
            return redirect(url_for('index'))
        except:
            return "اسم المستخدم موجود مسبقاً!"
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        conn = sqlite3.connect('database.db')
        check = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pwd)).fetchone()
        conn.close()
        if check:
            session['user'] = user
            return redirect(url_for('index'))
        return "بيانات خاطئة!"
    return render_template('login.html')

@app.route('/claim_gift', methods=['POST'])
def claim_gift():
    conn = sqlite3.connect('database.db')
    user = conn.execute('SELECT last_gift FROM users WHERE username=?', (session['user'],)).fetchone()
    
    now = datetime.now()
    if user[0] and (now - datetime.strptime(user[0], '%Y-%m-%d %H:%M:%S')) < timedelta(days=1):
        return jsonify({"status": "error", "message": "لقد حصلت على هدية اليوم بالفعل!"})
    
    conn.execute('UPDATE users SET points = points + 70, last_gift = ? WHERE username = ?', 
                 (now.strftime('%Y-%m-%d %H:%M:%S'), session['user']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "تمت إضافة 70 نقطة لحسابك!"})

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=True)
