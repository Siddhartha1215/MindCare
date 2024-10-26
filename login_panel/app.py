from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from mongo import db
from bson.objectid import ObjectId

app = Blueprint('login_panel', __name__, template_folder='templates')

login_manager = LoginManager()
login_manager.login_view = 'login_panel.login'
login_manager.login_message_category = 'info'

class User(UserMixin):
    def __init__(self, username, password_hash, id=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get_user_by_id(user_id):
        user = db.users.find_one({"_id": ObjectId(user_id)})
        return User(username=user['username'], password_hash=user['password_hash'], id=str(user['_id'])) if user else None

    @staticmethod
    def get_user_by_username(username):
        user = db.users.find_one({"username": username})
        return User(username=user['username'], password_hash=user['password_hash'], id=str(user['_id'])) if user else None

@login_manager.user_loader
def load_user(user_id):
    return User.get_user_by_id(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.users.find_one({"username": username}):
            flash('That username is taken. Please choose a different one.', 'danger')
            return redirect(url_for('login_panel.register'))        
        hashed_password = generate_password_hash(password)
        db.users.insert_one({"username": username, "password_hash": hashed_password})
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login_panel.login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_panel.login'))