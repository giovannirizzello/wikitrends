import sqlite3
from telegram_daily import greet_new_user
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
DB_NAME = "users.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, username TEXT)")
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/short')
def short_page():
    return render_template('short.html')

@app.route('/long')
def long_page():
    return render_template('long.html')

@app.route('/subscribe')
def subscribe_page():
    return render_template('subscribe.html')

@app.route('/add', methods=['POST'])
def add_user():
    name = request.form['name']
    username = request.form['username']
    
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO users VALUES (?, ?)", (name, username))
        conn.commit()
    
    greet_new_user(name, username)

    return redirect('/')

def run_server(port=5000):
    init_db()
    app.run(debug=False, port=port, use_reloader=False)