from flask import Flask, request, render_template, session, redirect, g, url_for
from os import urandom
import requests
import sqlite3 as sq
import re
isbn_reg=r"^(?:ISBN(?:-1[03])?:?)?(?=[0-9X]{10}$|(?=(?:[0-9]+[-]){3})[-0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[-]){4})[-0-9]{17}$)(?:97[89][-]?)?[0-9]{1,5}[-]?[0-9]+[-]?[0-9]+[-]?[0-9X]$"
app = Flask(__name__)
sec_key = repr(urandom(24))
app.secret_key = sec_key

def get_db():
	db = getattr(g, 'database', None)
	if db is None:
		g.database = sq.connect('books.db')
		db = g.database
	return db

@app.route('/', methods=['GET', 'POST'])
def start():
	return render_template('login.html')
@app.route('/login', methods=['POST'])
def login():
	username = request.form['username']
	passw = request.form['passw']
	wrong_creds = False
	db = get_db()
	cur = db.cursor()
	cur.execute('SELECT * FROM users')
	credentials=cur.fetchall()
	for cred in credentials:
		if username == cred[1] and passw == cred[2]:
			session['username'] = username
			return redirect(url_for("dashboard"))
	else:
		wrong_creds = True
		return render_template('/login.html', methods=['GET', 'POST'], wrong_creds=wrong_creds)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	if 'username' not in session:
		return redirect(url_for('/login'))
	else:
		db = get_db()
		cur = db.cursor()
		cur.execute('select user_id from users where username=(?)',(session['username'],))
		uid=cur.fetchone()
		cur.execute('SELECT * FROM books WHERE user=(?)', (uid[0],))
		book_rows=cur.fetchall()
		return render_template("dashboard.html", methods=['GET','POST'], book_rows=book_rows)
@app.route('/submit', methods=["GET","POST"])
def submit():
	if request.method == 'POST':
		db = get_db()
		cur = db.cursor()
		isbn_title=request.form["isbn_title"]
		if re.search(isbn_reg,isbn_title):
			url='https://www.googleapis.com/books/v1/volumes?q=isbn:'+isbn_title
		else:
			url='https://www.googleapis.com/books/v1/volumes?q=title:'+isbn_title
		book_data=requests.get(url)
		try:
			authors=book_data.json()['items'][0]['volumeInfo']['authors']
		except:
			authors='Authors not found!'
		try:
			title=book_data.json()['items'][0]['volumeInfo']['title']
		except:
			title='Title not found!'
		try:
			p_count=book_data.json()['items'][0]['volumeInfo']['pageCount']
		except:
			p_count='Page count not found!'
		try:
			avg_rating=book_data.json()['items'][0]['volumeInfo']['averageRating']
		except:
			avg_rating='Average rating not found!'
		cur.execute('select user_id from users where username=(?)',(session['username'],))
		uid=cur.fetchone()
		cur.execute('INSERT INTO books VALUES (?, ?, ?, ?, ?)', (title,authors[0],p_count,avg_rating,uid[0]))
		db.commit()
		return redirect(url_for('dashboard'))

@app.route('/delete', methods=["GET","POST"])
def delete():
	if request.method == 'POST':
		db = get_db()
		cur = db.cursor()
		delete_book=request.form["delete_book"]
		cur.execute('select user_id from users where username=(?)',(session['username'],))
		uid=cur.fetchone()
		cur.execute('delete from books where title=(?) AND user=(?)',(delete_book.title(), uid[0]))
		db.commit()
		return redirect(url_for('dashboard'))

@app.teardown_request
def close_connection(exception):
	db = getattr(g, 'database', None)
	if db is not None:
		db.close()

if __name__ == "__main__":
	app.run(debug=True)