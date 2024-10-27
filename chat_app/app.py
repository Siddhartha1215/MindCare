from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import current_user
from flask_socketio import join_room, leave_room, send, emit
from socket_instance import socketio

app = Blueprint('chat_app', __name__, template_folder='templates')

# Static token for admin login
ADMIN_TOKEN = 'meow'

# List to store banned users
banned_users = set()

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


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('chat_message', {'username': 'System', 'msg': f'{username} has left the room.'}, to=room)

@socketio.on('chat_message')
def chat_handle_message(data):
    username = data['username']
    room = data['room']
    if username in banned_users:
        emit('banned', {'message': 'You are permanently banned from the chat due to misbehavior.'}, room=request.sid)
    else:
        emit('chat_message', {'username': username, 'msg': data['msg']}, room=room)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    if username in banned_users:
        emit('banned', {'message': 'You are permanently banned from the chat.'}, room=request.sid)
    else:
        join_room(room)
        emit('chat_message', {'username': 'System', 'msg': f'{username} has entered the room.'}, room=room)


@socketio.on('remove_user')
def remove_user(data):
    username = data['username']
    room = 'main_room'
    banned_users.add(username)
    send(f"{username} has been removed and banned by the admin.", to=room)
    emit('banned', {'message': 'You are permanently banned from the chat due to misbehavior.'}, room=request.sid)
    emit('user_removed', {'username': username}, to=room)


# List to store available rooms
available_rooms = []


@app.route('/chat')
def chat():
    # Redirect to user dashboard
    return redirect(url_for('chat_app.user_dashboard'))

@app.route('/dashboard')
def user_dashboard():
    if not current_user.is_authenticated:
        flash('You need to log in to access the dashboard.', 'warning')
        return redirect(url_for('login_panel.login'))
    return render_template('user_dashboard.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    data = request.get_json()
    room_name = data.get('room_name')
    if room_name and room_name not in available_rooms:
        available_rooms.append(room_name)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Room already exists or invalid name.'})

@app.route('/rooms', methods=['GET'])
def get_rooms():
    return jsonify({'rooms': available_rooms})

@app.route('/chat/<room_name>')
def join_chat_room(room_name): 
    if not current_user.is_authenticated:
        flash('You need to log in to access chat rooms.', 'warning')
        return redirect(url_for('login_panel.login'))
    return render_template('chat.html', username=current_user.username, room=room_name)
