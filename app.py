from flask import Flask, render_template, session, request, redirect, url_for
import utils

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		if 'username' not in session:
			return redirect(url_for('login'))
		utils.new_post(
			session['username'],
			request.form['post'],
			request.form['heading']
			)
		return render_template(
			'index.html',
			posts=utils.get_recent_posts(),
			user_posts=utils.get_user_posts(session['username'])
			)
	if 'username' in session:
		return render_template(
			'index.html',
			posts=utils.get_recent_posts(),
			user_posts=utils.get_user_posts(session['username'])
			)
	return redirect(url_for('login'))

@app.route('/logout')
def logout():
	if 'username' in session:
			del session['username']
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form['username']
		if utils.check_login_info(username, request.form['password']):
			session['username'] = username
			return redirect(url_for('index'))
		else:
			return render_template('login.html',
				error='Invalid username or password.', posts=utils.get_recent_posts())
	return render_template('login.html', posts=utils.get_recent_posts())

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		error = utils.register_new_user(
			username,
			request.form['password'],
			request.form['confirm_password'],
			request.form['email']
			)
		if error:
			return render_template('register.html', error=error)
		else:
			session['username'] = username
			return redirect(url_for('index'))
	return render_template('register.html')

@app.route('/account', methods=['GET','POST'])
def account():
	return render_template('account.html')

@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
	if request.method == 'POST':
		if 'modify' in request.form:
			utils.modify_post(post_id, request.form['new_post'])
		else:
			utils.remove_post(post_id)
		return redirect(url_for('index'))
	if 'username' not in session:
		return redirect(url_for('login'))
	if post_id not in utils.get_user_posts(session['username']):
		return 'Error: Invalid post id.'
	return render_template('edit.html', post=utils.get_post(post_id))

if __name__ == "__main__":
	utils.register_new_user('Dennis Yatunin',
		'password0',
		'password0',
		'dyatun@gmail.com'
		)
	utils.register_new_user('Mike Zamansky',
		'abcdefg123',
		'abcdefg123',
		'sample@aol.com'
		)
	utils.register_new_user('Kerfuffle',
		'99 bottles of beer',
		'99 bottles of beer',
		'wowzers@verizon.net'
		)
	print utils.register_new_user(
            'Leon',
            'plsplspls1',
            'plsplspls1',
            'pls@pls.com'
            )
	app.debug = True
	app.secret_key = utils.secret_key
	app.run(host="0.0.0.0", port=8000)
