import sqlite3
from flask import Flask, render_template, request, redirect, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

conn = sqlite3.connect('kstw_database.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS members (
                membership_number TEXT PRIMARY KEY,
                name TEXT,
                institution TEXT,
                cluster TEXT,
                safaricom_number TEXT,
                amount_contributed REAL DEFAULT 0)''')
conn.commit()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        institution = request.form.get('institution')
        cluster = request.form.get('cluster')
        safaricom_number = request.form.get('safaricom_number')
        
        if not name or not institution or not cluster or not safaricom_number:
            flash('All fields are required.', 'error')
            return redirect(request.url) 
            
        if not safaricom_number.isdigit() or len(safaricom_number) != 10:
            flash('Safaricom number must be a 10-digit number.', 'error')
            return redirect(request.url) 
        
        try:
            membership_number = generate_membership_number()
            cursor.execute('''INSERT INTO members 
                            (membership_number, name, institution, cluster, safaricom_number)
                            VALUES (?, ?, ?, ?, ?)''',
                            (membership_number, name, institution, cluster, safaricom_number))
            conn.commit()
            flash(f'Registration successful! Your membership number is: {membership_number}', 'success')
            return redirect('/login')  
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'password':
            flash('Login successful!', 'success')
            return redirect('/dashboard') 
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(request.url)
    
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    return render_template('dashboard.html', members=members)

@app.route('/contribute')
def contribute():
    return redirect('tel:+254727284993')

@app.route('/download_report/<format>')
def download_report(format):
    cursor.execute("SELECT * FROM members")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['Membership Number', 'Name', 'Institution', 'Cluster', 'Safaricom Number', 'Amount Contributed'])
    if format == 'csv':
        filename = 'kstw_report.csv'
        df.to_csv(filename, index=False)
    elif format == 'excel':
        filename = 'kstw_report.xlsx'
        df.to_excel(filename, index=False)
    elif format == 'pdf':
        filename = 'kstw_report.pdf'
        df.to_pdf(filename, index=False)
    else:
        flash('Invalid file format.', 'error')
        return redirect('/dashboard')
    return send_file(filename, as_attachment=True)


def generate_membership_number():
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0] + 1
    return f"KSTW{count:04d}-24"

if __name__ == '__main__':
    app.run(debug=True)