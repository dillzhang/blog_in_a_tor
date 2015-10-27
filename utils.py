from os import urandom
from hashlib import sha512
from uuid import uuid4
from re import search
from time import gmtime, strftime
from pymongo import MongoClient
import sqlite3
'''
	Things Finished And Tested:
	Things Finished But not Tested: Check_Login_Info, modify_password, modify_email
	Things Partially Finished: register_new_user (Find way to check all users and emails easily)
	Things to Finish: Everything Else, Delete Extra Comments when finished
'''
# a 32-byte key that should be used to secure the Flask session
secret_key = urandom(32);

# checks whether the database contains a user with the given information
def check_login_info(username, password):
	#Creates Connection to MongoClient and Connects to the database
	connection = MongoClient()
	c = connection['data']
	print c.collection_names()
	# If the user_info table doesn't exist, return false.
	if not "user_info" in c.collection_names():
			return False
	# If the table does exist, check the given username and password.
	#q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.user_info.find({'username':username})
	# If the username does not exist, return false.
	if not salt_n_hash:
		return False
	# If the password is wrong, return false.
	if (
		sha512((password + salt_n_hash['salt']) * 10000).hexdigest() != salt_n_hash['hash_value']
		):
		return False
	# Finally, return true.
	return True

# enters new login information into the database, returns None or possible errors
def register_new_user(username, password, confirm_password, email):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# Check if the passwords match.
	if password != confirm_password:
		return 'Passwords do not match.'
	# Check if the username is valid.
	if len(username) < 1:
		return 'Username must be at least 1 character long.'
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
	#q = 'CREATE TABLE IF NOT EXISTS user_info \
	#(user_id INT, username TEXT, salt INT, hash_value INT, email TEXT)'
	#c.execute(q)
	# Check if the username or email is taken.
	#q = 'SELECT username, email FROM user_info'
	if c.user_info.find({'username':username}) != None:
		return 'Username already taken.'
	if c.user_info.find({'email':email}) != None:
		return 'Email already taken.'
	# Create a random salt to add to the hash.
	salt = uuid4().hex
	# Create a hash, and use string concatenation to make the hash function slow
	# for added security.
	hash_value = sha512((password + salt) * 10000).hexdigest()
	# Enter the new information and return None.
	#q = 'SELECT COUNT(*) FROM user_info'
	num_rows = c.user_info.count()
	#q = 'INSERT INTO user_info (user_id, username, salt, hash_value, email) \
	#VALUES (?, ?, ?, ?, ?)'
	d = {'user_id':num_rows + 1,
		'username':username,
		'salt':salt,
		'hash_value':hash_value,
		'email':email}
	c.user_info.insert(d)
	return None

# changes the user's hashed password in the database, returns None or possible errors
def modify_password(username, password, new_password, confirm_password):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
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
	if not "user_info" in c.collection_names():
		return 'Incorrect username or password.'
	# If the table does exist, check the old username and password.
	#q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.user_info.find({'username':username})
	if not (
		bool(salt_n_hash) and
		sha512((password + salt_n_hash['salt']) * 10000).hexdigest() == salt_n_hash['hash_value']
		):
		return 'Incorrect username or password.'
	# Create a random salt to add to the hash.
	salt = uuid4().hex
	# Create a hash, and use string concatenation to make the hash function slow
	# for added security.
	hash_value = sha512((new_password + salt) * 10000).hexdigest()
	# Change the old salt and hash_value to the new ones and return None.
	#q = 'UPDATE user_info SET salt = ?, hash_value = ? WHERE username = ?'
	c.user_info.update({'username':username}, {"$set":{'salt':salt,'hash_value':hash_value}})
	#conn.commit()
	return None

# changes the user's email in the database, returns None or possible errors
def modify_email(username, password, new_email):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# Check if the new email is valid.
	if not bool(search(
		r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@"+
		r"(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:[A-Z]{2}|com|org|net|edu"+
		r"|gov|mil|biz|info|mobi|name|aero|asia|jobs|museum)\b", new_email)):
		return 'Email is invalid.'
	# If the user_info table doesn't exist, return an error message.
	#q = 'SELECT name FROM sqlite_master WHERE \
	#TYPE = "table" AND NAME = "user_info"'
	if not "user_info" in c.collection_names():
		return 'Incorrect username or password.'
	# If the table does exist, check the username and password.
	#q = 'SELECT salt, hash_value FROM user_info WHERE username = ?'
	salt_n_hash = c.user_info.find({'username':username})
	if not (
		bool(salt_n_hash) and
		sha512((password + salt_n_hash['salt']) * 10000).hexdigest() == salt_n_hash['hash_value']
		):
		return 'Incorrect username or password.'
	# Change the old email to the new one and return None.
	#q = 'UPDATE user_info SET email = ? WHERE username = ?'
	c.user_info.update({'username':username}, {"$set":{'email':new_email}})
	conn.commit()
	return None

# enters a new post into the database, returns post_id or possible errors
def new_post(username, post, heading=''):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the posts table doesn't exist, create it.
	q = 'CREATE TABLE IF NOT EXISTS posts \
	(post_id INT, user_id INT, time TEXT, heading TEXT, post TEXT)'
	c.execute(q)
	# Get the user_id associated with username.
	q = 'SELECT user_id FROM user_info WHERE username = ?'
	user_id = c.execute(q, (username,)).fetchone()[0]
	if not user_id:
		return 'Incorrect username.'
	# If no heading was provided, set a default heading.
	if heading == '':
		heading = post[:10]+'...'
	# Enter the new information and return the new post's id.
	q = 'SELECT COUNT(*) FROM posts'
	num_rows = c.execute(q).fetchone()[0]
	q = 'INSERT INTO posts (post_id, user_id, time, heading, post) \
	VALUES (?, ?, ?, ?, ?)'
	c.execute(
		q,
		(
			num_rows + 1,
			user_id,
			strftime("%a, %d %b %Y %H:%M:%S", gmtime()),
			heading,
			post
			)
		)
	conn.commit()
	return num_rows + 1

# enters a new comment into the database, returns comment_id or possible errors
def new_comment(username, post_id, comment):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the comments table doesn't exist, create it.
	q = 'CREATE TABLE IF NOT EXISTS comments \
	(comment_id INT, post_id INT, user_id INT, time TEXT, comment TEXT)'
	c.execute(q)
	# Get the user_id associated with username.
	q = 'SELECT user_id FROM user_info WHERE username = ?'
	user_id = c.execute(q, (username,)).fetchone()[0]
	if not user_id:
		'Incorrect username.'
	# Enter the new information and return the new comment's id.
	q = 'SELECT COUNT(*) FROM comments'
	num_rows = c.execute(q).fetchone()[0]
	q = 'INSERT INTO comments (comment_id, post_id, user_id, time, comment) \
	VALUES (?, ?, ?, ?, ?)'
	c.execute(
		q,
		(
			num_rows + 1,
			post_id,
			user_id,
			strftime("%a, %d %b %Y %H:%M:%S", gmtime()),
			comment
			)
		)
	conn.commit()
	return num_rows + 1

# returns the post, heading,and timestamp from the database, or None
def get_post(post_id):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the posts table doesn't exist, return None.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return None
	# Return the list [post, heading, time]
	q = 'SELECT post, heading, time FROM posts WHERE post_id = ?'
	info = c.execute(q, (post_id,)).fetchone()
	conn.commit()
	return info

# returns the comments, usernames, times, and comment_ids from the database, or []
def get_comments(post_id):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the comments table doesn't exist, return an empty list.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "comments"'
	c.execute(q)
	if not c.fetchone():
		return []
	# Return the list of lists [comment, username, time, comment_id].
	q = 'SELECT comments, username, time, comment_id FROM comments, user_info \
	WHERE comments.post_id = ?, user_info.post_id = ?'
	info = c.execute(q, (post_id, post_id)).fetchall()
	conn.commit()
	return info

# returns the post_ids from the database, or []
def get_user_posts(username):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the posts table doesn't exist, return an empty list.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return []
	# Get the user_id associated with username.
	q = 'SELECT user_id FROM user_info WHERE username = ?'
	user_id = c.execute(q, (username,)).fetchone()[0]
	# Return the list of lists [post, heading, time, post_id]
	q = 'SELECT post_id FROM posts WHERE user_id = ?'
	info = [row[0] for row in c.execute(q, (user_id,)).fetchall()]
	conn.commit()
	return info

# returns the posts, headings,and times, and post_ids from the database, or []
def get_recent_posts():
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the posts table doesn't exist, return an empty list.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return []
	# Get the last post_id in posts.
	q = 'SELECT COUNT(*) FROM posts'
	num_rows = c.execute(q).fetchone()[0]
	# Return the list of lists [post, heading, time, post_id]
	q = 'SELECT post, heading, time, post_id FROM posts WHERE post_id > ? \
	ORDER BY post_id DESC'
	info = c.execute(q, (num_rows - 11,)).fetchall()
	conn.commit()
	return info

# modifies the post in the database, returns None
def modify_post(post_id, new_post):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the posts table doesn't exist, return None.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return None
	# Change the old post to the new one and return None.
	q = 'UPDATE posts SET post = ?, time = ? WHERE post_id = ?'
	c.execute(
		q,
		(
			new_post,
			strftime("%a, %d %b %Y %H:%M:%S", gmtime()),
			post_id
			)
		)
	conn.commit()
	return None

# modifies the comment in the database, returns None
def modify_comment(comment_id, new_comment):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the comments table doesn't exist, return None.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "comments"'
	c.execute(q)
	if not c.fetchone():
		return None
	# Change the old comment to the new one and return None.
	q = 'UPDATE comments SET comment = ?, time = ? WHERE comment_id = ?'
	c.execute(
		q,
		(
			new_comment,
			strftime("%a, %d %b %Y %H:%M:%S", gmtime()),
			comment_id
			)
		)
	conn.commit()
	return None

# removes the post from the database, returns None
def remove_post(post_id):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the posts table doesn't exist, return None.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "posts"'
	c.execute(q)
	if not c.fetchone():
		return None
	q = 'DELETE FROM posts WHERE post_id = ?'
	c.execute(q, (post_id,))
	conn.commit()
	return None

# removes the comment from the database, returns None
def remove_comment(comment_id):
	# Create the connection and cursor for the SQLite database.
	conn = sqlite3.connect("data.db")
	c = conn.cursor()
	# If the comments table doesn't exist, return None.
	q = 'SELECT name FROM sqlite_master WHERE \
	TYPE = "table" AND NAME = "comments"'
	c.execute(q)
	if not c.fetchone():
		return None
	q = 'DELETE FROM comments WHERE comment_id = ?'
	c.execute(q, (comment_id,))
	conn.commit()
	return None

