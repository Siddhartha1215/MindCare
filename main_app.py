from flask import render_template
from flask_login import LoginManager, current_user, UserMixin
from login_panel.app import app as login_panel
from video_maker.app import app as video_maker
from voicebot.app import app as voicebot
from chat_app.app import app as chat_app
from ch_app.app import app as ch_app
from socket_instance import socketio
from symptom.app import app as symptom
from shared import app
from mongo import db
from bson.objectid import ObjectId

socketio.init_app(app)

# Register the blueprint
app.register_blueprint(login_panel, url_prefix='/login_panel')
app.register_blueprint(voicebot, url_prefix='/voicebot')
app.register_blueprint(chat_app, url_prefix='/chat_app')
app.register_blueprint(ch_app, url_prefix='/ch_app')
app.register_blueprint(symptom, url_prefix='/symptom')
app.register_blueprint(video_maker, url_prefix='/video_maker')

# Initialize Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login_panel.login'



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

@app.route('/')
def index():
    return render_template('index.html', logged_in=current_user.is_authenticated)

@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    # socketio.run(app)
    app.run(host='0.0.0.0', port=5000)
