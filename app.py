from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import uuid
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'CyberVault_Secret'

# إعدادات الإيميل (يجب وضع إيميلك وكلمة مرور التطبيق لتعمل)
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"

def init_db():
    conn = sqlite3.connect('vault.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, 
                  card_number TEXT, cvv TEXT, points INTEGER DEFAULT 100)''')
    conn.commit()
    conn.close()

init_db()

def send_welcome_email(user_email):
    msg = MIMEText(f"مرحباً بك في CyberVault!\nتم فتح حسابك بنجاح. يمكنك الآن الدخول للمتجر واستخدام بطاقتك الإلكترونية.")
    msg['Subject'] = 'تم فتح حساب جديد في CyberVault'
    msg['From'] = EMAIL_SENDER
    msg['To'] = user_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except: pass

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    pwd = request.form['password']
    # إنشاء بيانات البطاقة الفريدة
    card_no = " ".join(["".join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)])
    cvv = str(random.randint(100, 999))
    
    try:
        conn = sqlite3.connect('vault.db')
        conn.execute('INSERT INTO users (email, password, card_number, cvv) VALUES (?, ?, ?, ?)', 
                     (email, pwd, card_no, cvv))
        conn.commit()
        send_welcome_email(email)
        session['user'] = email
        return redirect(url_for('index'))
    except:
        return "هذا الحساب موجود بالفعل!"

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login_page'))
    conn = sqlite3.connect('vault.db')
    user = conn.execute('SELECT * FROM users WHERE email=?', (session['user'],)).fetchone()
    conn.close()
    return render_template('index.html', user=user)

# بقية المسارات (Login, Purchase...) كما في الأكواد السابقة
