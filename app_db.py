import sqlite3 as sq

con=sq.connect('books.db')

c=con.cursor()

c.execute("CREATE TABLE users(user_id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
c.execute("CREATE TABLE books(TITLE TEXT, AUTHORS TEXT, PG_COUNT INTEGER, AVG_RATING INTEGER, USER INTEGER, FOREIGN KEY (USER) REFERENCES USERS(USER_ID))")
c.execute("INSERT INTO users VALUES(1,'user1', 'password1')")
c.execute("INSERT INTO users VALUES(2,'user2', 'password2')")

con.commit()
con.close()
	
	