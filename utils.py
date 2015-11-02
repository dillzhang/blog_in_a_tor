from os import urandom
from hashlib import sha512
from uuid import uuid4
from re import search
from time import gmtime, strftime
from pymongo import MongoClient
import sqlite3
# a 32-byte key that should be used to secure the Flask session
secret_key = urandom(32);

# checks whether the database contains a user with the given information
def check_login_info(username, password):
	#Creates Connection to MongoClient and Connects to the database
	connection = MongoClient()
	c = connection['data']
	# If the user_info table doesn't exist, return false.
	if not "user_info" in c.collection_names():
			return False
	# If the table does exist, check the given username and password.
	salt_n_hash = c.user_info.find_one({'username':username})
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
	# Check if the username or email is taken.
	print(c.user_info.find_one({'username':username}))
	if c.user_info.find_one({'username':username}) != None :
		return 'Username already taken'
	if c.user_info.find_one({'email':email}) != None:
		return 'Email already taken'
	# Create a random salt to add to the hash.
	salt = uuid4().hex
	# Create a hash, and use string concatenation to make the hash function slow
	# for added security.
	hash_value = sha512((password + salt) * 10000).hexdigest()
	# Enter the new information and return None.
	num_rows = c.user_info.count()
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
	salt_n_hash = c.user_info.find_one({'username':username})
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
	c.user_info.update({'username':username}, {"$set":{'salt':salt,'hash_value':hash_value}})
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
	if not "user_info" in c.collection_names():
		return 'Incorrect username or password.'
	# If the table does exist, check the username and password.
	salt_n_hash = c.user_info.find_one({'username':username})
	if not (
		bool(salt_n_hash) and
		sha512((password + salt_n_hash['salt']) * 10000).hexdigest() == salt_n_hash['hash_value']
		):
		return 'Incorrect username or password.'
	# Change the old email to the new one and return None.
	c.user_info.update({'username':username}, {"$set":{'email':new_email}})
	return None

# enters a new post into the database, returns post_id or possible errors
def new_post(username, post, heading=''):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# Get the user_id associated with username.
	user_id = c.user_info.find_one({'username':username})['user_id']
	if not user_id:
		return 'Incorrect username.'
	# If no heading was provided, set a default heading.
	if heading == '':
		heading = post[:10]+'...'
	# Enter the new information and return the new post's id.
	num_rows = c.posts.count()
	q = {'post_id':num_rows + 1,
		'user_id':user_id,
		'time':strftime("%a, %d %b %Y %H:%M:%S", gmtime()),
		'heading':heading,
		'post':post}
	c.posts.insert(q)
	return num_rows + 1

# enters a new comment into the database, returns comment_id or possible errors
def new_comment(username, post_id, comment):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	user_id = c.user_info.find_one({'username':username})['user_id']
	if not user_id:
		'Incorrect username.'
	# Enter the new information and return the new comment's id.
	num_rows = c.comments.count()
	q=
		{'comment_id':num_rows + 1,
			'post_id':post_id,
			'user_id':user_id,
			'time':strftime("%a, %d %b %Y %H:%M:%S", gmtime()),
			'comment':comment
			}
	c.comments.insert(q)
	return num_rows + 1

# returns the post, heading,and timestamp from the database, or None
def get_post(post_id):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	if not "posts" in c.collection_names():
		return None
	# Return the list [post, heading, time]
	q = 'SELECT post, heading, time FROM posts WHERE post_id = ?'
	info = c.posts.find_one({'post_id':post_id})
	return info

# returns the comments, usernames, times, and comment_ids from the database, or []
def get_comments(post_id):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# If the comments table doesn't exist, return an empty list.
	if not "comments" in c.collection_name():
		return []
	# Return the list of lists [comment, username, time, comment_id].
	for x in c.comments.find({"post_id":post_id}):
		info.append(x)
	return info

# returns the post_ids from the database, or []
def get_user_posts(username):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# If the posts table doesn't exist, return an empty list.
	if not "posts" in c.collection_names():
		return []
	# Get the user_id associated with username.
	user_id = c.user_info.find_one({'username':username})['user_id']
	# Return the list of lists [post, heading, time, post_id]
	for x in c.posts.find({"user_id":user_id}):
		info.append(x)
	return info

# returns the posts, headings,and times, and post_ids from the database, or []
def get_recent_posts():
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c=connection['data']
	# If the posts table doesn't exist, return an empty list.
	if not "posts" in c.collection_names():
		return []
	# Get the last post_id in posts.
	num_rows = c.posts.count()
	# Return the list of lists [post, heading, time, post_id]
	for x in c.posts.find({"post_id":{'$gte': num_rows-11}}):
		info.append(x)
	return info

# modifies the post in the database, returns None
def modify_post(post_id, new_post):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# If the posts table doesn't exist, return None.
	if not "posts" in c.collection_names():
		return None
	# Change the old post to the new one and return None.
	c.posts.update({'post_id':post_id}, {"$set":{'post':new_post,'time':strftime("%a, %d %b %Y %H:%M:%S", gmtime())}})
	return None

# modifies the comment in the database, returns None
def modify_comment(comment_id, new_comment):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# If the comments table doesn't exist, return None.
	if not "comments" in c.collection_names():
		return None
	# Change the old comment to the new one and return None.
	c.comments.update({'comment_id':comment_id}, {"$set":{'comment':new_comment, 'time':strftime("%a, %d %b %Y %H:%M:%S",gmtime())}})
	return None

# removes the post from the database, returns None
def remove_post(post_id):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# If the posts table doesn't exist, return None.
	if not "posts" in c.collection_names():
		return None
	c.posts.remove({'post_id':post_id})
	return None

# removes the comment from the database, returns None
def remove_comment(comment_id):
	# Create the connection and cursor for the SQLite database.
	connection = MongoClient()
	c = connection['data']
	# If the comments table doesn't exist, return None.
	if not "comments" in c.collection_names():
		return None
	c.comments.remove({'comment_id':comment_id})
	return None

