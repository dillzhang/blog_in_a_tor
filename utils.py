from os import urandom
from hashlib import sha512
from uuid import uuid4
from re import search
import sqlite3

# a 32-byte key that should be used to secure the Flask session
secret_key = urandom(32);

# the connection and cursor for the SQLite database containing all the data
conn = sqlite3.connect("data.db")
c = conn.cursor()

# enters new login information into the database
def enter_login_info(username, password):
	# If the info table doesn't exist, create it.
	q = '''CREATE TABLE IF NOT EXISTS info
		(id INT, username TEXT, salt INT, hash_value INT)'''
	c.execute(q)
	q = 'SELECT username FROM info'
	c.execute(q)
	if username in c:
		return 'Username already exists.'
	if len(password) < 8:
		return 'Password must be at least 8 characters long.'
	if not bool(search(r'\d', password)):
		return 'Password must contain both letters and digits.'
	# Create a random salt to add to the hash.
	salt = uuid4().hex
	# Create a hash, and use string concatenation to make the hash function slow.
	hash_value = sha512((password + salt) * 10000).hexdigest()
	q = 'SELECT COUNT(*) FROM info'
	c.execute(q)
	num_rows = c.fetchone()[0]
	q = 'INSERT INTO info (id, username, salt, hash_value) VALUES (?, ?, ?, ?)'
	c.execute(q, (num_rows + 1, username, salt, hash_value))
	conn.commit()
	return None

# checks whether the database contains a user with the given login information
def login_check(username, password):
	# If the info table doesn't exist, return false.
	q = 'SELECT name FROM sqlite_master WHERE TYPE = "table" AND NAME = "info"'
	c.execute(q)
	if not c.fetchone():
		return False
	q = 'SELECT username, salt, hash_value FROM info'
	c.execute(q)
	for user in c:
		if (
			username == user[0] and
			sha512((password + user[1]) * 10000).hexdigest() == user[2]
			):
			return True
	return False
