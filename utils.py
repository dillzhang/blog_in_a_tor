from os import urandom
from hashlib import sha512
from uuid import uuid4
from re import search
from time import time
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

# enters new login information into the database, returns None or possible errors
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
	(user_id INT, username TEXT, salt INT, hash_value INT, email TEXT)'
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
	q = 'INSERT INTO user_info (user_id, username, salt, hash_value, email) \
	VALUES (?, ?, ?, ?, ?)'
	c.execute(q, (num_rows + 1, username, salt, hash_value, email))
	conn.commit()
	return None

# changes the user's hashed password in the database, returns None or possible errors
def modify_password(username, password, new_password, confirm_password):
	# Check if the passwords match.
	if new_password != confirm_password:
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
		return 'Incorrect username or password.'
	# If the table does exist, check the old username and password.
	q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.execute(q, (username,)).fetchone()
	if not (
		bool(salt_n_hash) and
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

# changes the user's email in the database, returns None or possible errors
def modify_email(username, password, new_email):
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
		return 'Incorrect username or password.'
	# If the table does exist, check the username and password.
	q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.execute(q, (username,)).fetchone()
	if not (
		bool(salt_n_hash) and
		sha512((password + salt_n_hash[0]) * 10000).hexdigest() == salt_n_hash[1]
		):
		return 'Incorrect username or password.'
	# Change the old email to the new one and return None.
	q = 'UPDATE user_info SET email = ? WHERE username = ?'
	c.execute(q, (new_email, username))
	conn.commit()
	return None

# enters a new post into the database, returns post_id or possible errors
def new_post(username, post, heading=post[:10]+'...'):
	# If the posts table doesn't exist, create it.
	q = 'CREATE TABLE IF NOT EXISTS posts \
	(post_id INT, user_id INT, time REAL, heading TEXT, post TEXT)'
	c.execute(q)
	# Get the user_id associated with username.
	q = 'SELECT user_id FROM user_info WHERE username = ?'
	user_id = c.execute(q, (username,)).fetchone()
	if not user_id:
		'Incorrect username.'
	# Enter the new information and return the new post's id.
	q = 'SELECT COUNT(*) FROM posts'
	num_rows = c.execute(q).fetchone()[0]
	q = 'INSERT INTO posts (post_id, user_id, time, heading, post) \
	VALUES (?, ?, ?, ?, ?)'
	c.execute(q, (num_rows + 1, user_id, time.time(), heading, post))
	return num_rows + 1

# enters a new comment into the database, returns comment_id or possible errors
def new_comment(username, post_id, comment):
	# If the comments table doesn't exist, create it.
	q = 'CREATE TABLE IF NOT EXISTS comments \
	(comment_id INT, post_id INT, user_id INT, time REAL, comment TEXT)'
	c.execute(q)
	# Get the user_id associated with username.
	q = 'SELECT user_id FROM user_info WHERE username = ?'
	user_id = c.execute(q, (username,)).fetchone()
	if not user_id:
		'Incorrect username.'
	# Enter the new information and return the new comment's id.
	q = 'SELECT COUNT(*) FROM comments'
	num_rows = c.execute(q).fetchone()[0]
	q = 'INSERT INTO comments (comment_id, post_id, user_id, time, comment) \
	VALUES (?, ?, ?, ?, ?)'
	c.execute(q, (num_rows + 1, post_id, user_id, time.time(), comment))
	return num_rows + 1

# returns the post, heading,and timestamp from the database, or None
def get_post(post_id):
	# If the posts table doesn't exist, return an error message.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return None
	# Return the list [post, heading, time]
	q = 'SELECT post, heading, time FROM posts WHERE post_id = ?'
	info = c.execute(q, (post_id,)).fetchone()
	return info

# returns the comments, usernames, times, and comment_ids from the database, or []
def get_comments(post_id):
	# If the comments table doesn't exist, return an empty list.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "comments"'
	c.execute(q)
	if not c.fetchone():
		return []
	# Return the list of lists [comment, username, time, comment_id].
	q = 'SELECT comments, username, time, comment_id FROM comments, user_info \
	WHERE comments.post_id = ?, user_info.post_id = ?'
	return c.execute(q, (post_id, post_id)).fetchall()

# returns the post, heading,and timestamp from the database, or []
def get_user_posts(username):
	# If the posts table doesn't exist, return an empty list.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return []
	# Get the user_id associated with username.
	q = 'SELECT user_id FROM user_info WHERE username = ?'
	user_id = c.execute(q, (username,)).fetchone()
	if not user_id:
		[]
	# Return the list of lists [post, heading, time]
	q = 'SELECT post, heading, time FROM posts WHERE user_id = ?'
	return c.execute(q, (user_id,)).fetchall()

# returns the post, heading,and timestamp from the database, or []
def get_recent_posts():
	# If the posts table doesn't exist, return an empty list.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return []
	# Get the last post_id in posts.
	q = 'SELECT COUNT(*) FROM posts'
	num_rows = c.execute(q).fetchone()[0]
	# Return the list of lists [post, heading, time]
	q = 'SELECT post, heading, time FROM posts WHERE post_id > ?'
	return c.execute(q, (num_rows - 11,)).fetchall()
