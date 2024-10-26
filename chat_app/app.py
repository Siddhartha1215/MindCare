from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import current_user
from flask_socketio import join_room, leave_room, send, emit
from socket_instance import socketio

app = Blueprint('chat_app', __name__, template_folder='templates')

# Static token for admin login
ADMIN_TOKEN = 'meow'

# List to store banned users
banned_users = set()

@app.route('/chat')
def chat():
    if not current_user.is_authenticated:
        flash('You need to log in to access the chat.', 'warning')
        return redirect(url_for('login_panel.login'))
    username = current_user.username
    return render_template('chat.html', username=username)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        token = request.form.get('token')
        if token == ADMIN_TOKEN:
            session['admin'] = True
            return redirect(url_for('chat_app.admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid token")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('chat_app.admin'))
    return render_template('admin_dashboard.html')

@app.route('/check_ban/<username>', methods=['GET'])
def check_ban(username):
    if username in banned_users:
        return jsonify({'banned': True, 'message': 'You are permanently banned from the chat due to misbehavior.'})
    else:
        return jsonify({'banned': False})

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    if username in banned_users:
        emit('banned', {'message': 'You are permanently banned from the chat due to misbehavior.'})
    else:
        join_room(room)
        send(f'{username} has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f'{username} has left the room.', to=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    room = data['room']

    if username in banned_users:
        emit('banned', {'message': 'You are permanently banned from the chat due to misbehavior.'}, room=request.sid)
    else:
        send(f"{username}: {data['msg']}", to=room)

@socketio.on('remove_user')
def remove_user(data):
    username = data['username']
    room = 'main_room'
    banned_users.add(username)
    send(f"{username} has been removed and banned by the admin.", to=room)
    emit('banned', {'message': 'You are permanently banned from the chat due to misbehavior.'}, room=request.sid)
    emit('user_removed', {'username': username}, to=room)
