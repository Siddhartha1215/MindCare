from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cum'
app.config['MONGO_URI'] = 'mongodb+srv://erza:qaz000@cluster0.kbmk3bq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'

client = MongoClient(app.config['MONGO_URI'])
db = client.mydatabase

login_manager = LoginManager(app)
login_manager.login_view = 'login'
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
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.users.find_one({"username": username}):
            flash('That username is taken. Please choose a different one.', 'danger')
            return redirect(url_for('register'))        
        hashed_password = generate_password_hash(password)
        db.users.insert_one({"username": username, "password_hash": hashed_password})
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_user_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def home():
    return render_template('home.html', logged_in=current_user.is_authenticated)

if __name__ == '__main__':
    app.run(debug=True)
