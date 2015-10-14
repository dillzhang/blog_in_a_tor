from os import urandom
from hashlib import sha512
from uuid import uuid4
from re import search
import sqlite3

# a 32-byte key that should be used to secure the Flask session
secret_key = urandom(32);

# the connection and cursor for the SQLite database containing all the data
# for testing purposes (database only resides in RAM):
conn = sqlite3.connect(':memory:')
#conn = sqlite3.connect("data.db")
c = conn.cursor()

# checks whether the database contains a user with the given information
def check_login_info(username, password):
	# If the user_info table doesn't exist, return false.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "user_info"'
	c.execute(q)
	if not c.fetchone():
		return False
	# If the table does exist, check the given username and password.
	q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.execute(q, (username,)).fetchone()
	if (
		sha512((password + salt_n_hash[0]) * 10000).hexdigest() == salt_n_hash[1]
		):
		return True
	return False

# enters new login information into the database
def register_new_user(username, password, confirm_password, email):
	# Check if the passwords match.
	if password != confirm_password:
		return 'Passwords do not match.'
	# Check if the password is valid.
	if len(password) < 8:
		return 'Password must be at least 8 characters long.'
	if not (
		bool(search(r'\d', password)) and
		bool(search('[a-zA-Z]', password))
		):
		return 'Password must contain both letters and digits.'
	# Check if the email is valid.
	if not bool(search(
		r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@"+
		r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|edu"+
		r"|gov|mil|biz|info|mobi|name|aero|asia|jobs|museum)\b", email)):
		return 'Email is invalid.'
	# If the user_info table doesn't exist, create it.
	q = 'CREATE TABLE IF NOT EXISTS user_info \
	(id INT, username TEXT, salt INT, hash_value INT, email TEXT)'
	c.execute(q)
	# Check if the username or email is taken.
	q = 'SELECT username, email FROM user_info'
	users = c.execute(q).fetchall()
	if username in [user[0] for user in users]:
		return 'Username already taken.'
	if email in [user[1] for user in users]:
		return 'Email already taken.'
	# Create a random salt to add to the hash.
	salt = uuid4().hex
	# Create a hash, and use string concatenation to make the hash function slow
	# for added security.
	hash_value = sha512((password + salt) * 10000).hexdigest()
	# Enter the new information and return None.
	q = 'SELECT COUNT(*) FROM user_info'
	num_rows = c.execute(q).fetchone()[0]
	q = 'INSERT INTO user_info (id, username, salt, hash_value, email) \
	VALUES (?, ?, ?, ?, ?)'
	c.execute(q, (num_rows + 1, username, salt, hash_value, email))
	conn.commit()
	return None

# changes the user's hashed password in the database
def modify_password(username, password, confirm_password, new_password):
	# Check if the old passwords match.
	if password != confirm_password:
		return 'Passwords do not match.'
	# Check if the new password is valid.
	if len(new_password) < 8:
		return 'Password must be at least 8 characters long.'
	if not (
		bool(search(r'\d', new_password)) and
		bool(search('[a-zA-Z]', new_password))
		):
		return 'Password must contain both letters and digits.'
	# If the user_info table doesn't exist, return an error message.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "user_info"'
	c.execute(q)
	if not c.fetchone():
		return 'User not found.'
	# If the table does exist, check the old username and password.
	q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.execute(q, (username,)).fetchone()
	if not (
		sha512((password + salt_n_hash[0]) * 10000).hexdigest() == salt_n_hash[1]
		):
		return 'Incorrect username or password.'
	# Create a random salt to add to the hash.
	salt = uuid4().hex
	# Create a hash, and use string concatenation to make the hash function slow
	# for added security.
	hash_value = sha512((new_password + salt) * 10000).hexdigest()
	# Change the old salt and hash_value to the new ones and return None.
	q = 'UPDATE user_info SET salt = ?, hash_value = ? WHERE username = ?'
	c.execute(q, (salt, hash_value, username))
	conn.commit()
	return None

# changes the user's email in the database
def modify_email(username, password, confirm_password, new_email):
	# Check if the passwords match.
	if password != confirm_password:
		return 'Passwords do not match.'
	# Check if the new email is valid.
	if not bool(search(
		r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@"+
		r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|edu"+
		r"|gov|mil|biz|info|mobi|name|aero|asia|jobs|museum)\b", new_email)):
		return 'Email is invalid.'
	# If the user_info table doesn't exist, return an error message.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "user_info"'
	c.execute(q)
	if not c.fetchone():
		return 'User not found.'
	# If the table does exist, check the username and password.
	q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.execute(q, (username,)).fetchone()
	if not (
		sha512((password + salt_n_hash[0]) * 10000).hexdigest() == salt_n_hash[1]
		):
		return 'Incorrect username or password.'
	# Change the old email to the new one and return None.
	q = 'UPDATE user_info SET email = ? WHERE username = ?'
	c.execute(q, (new_email, username))
	conn.commit()
	return None
