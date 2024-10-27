from flask import Flask, render_template, request, Blueprint, redirect, url_for, session, jsonify
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from socket_instance import socketio

app = Blueprint('videochat', __name__, template_folder='templates')

ADMIN_TOKEN = "meow"
waiting_users = []
room_occupants = {}  # Dictionary to track if admin has joined a user room

# Track connected users
connected_users = set()

@app.route('/vc')
def vc():
    return render_template('vc.html')

@app.route('/videochat_admin_dashboard')
def videochat_admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('videochat.videochat_admin'))
    return render_template('videochat_admin_dashboard.html')

@app.route('/videochat_admin', methods=['GET', 'POST'])
def videochat_admin():
    if request.method == 'POST':
        token = request.form.get('token')
        if token == ADMIN_TOKEN:
            session['admin'] = True
            return redirect(url_for('videochat.videochat_admin_dashboard'))
        else:
            return render_template('videochat_admin_login.html', error="Invalid token")
    return render_template('videochat_admin_login.html')

@app.route('/videochat_start')
def videochat_start():
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "user_" + str(len(waiting_users) + 1)  # Generate a username if not logged in

    session['user'] = username
    if username not in waiting_users:
        waiting_users.append(username)
    room_occupants[username] = {"admin_joined": False}  # Track if admin has joined
    return jsonify({"status": "waiting", "message": "Waiting for admin to join...", "username": username})

@app.route('/videochat_get_waiting_users')
def videochat_get_waiting_users():
    return jsonify({"users": waiting_users})

@app.route('/videochat_start_with_user/<username>')
def videochat_start_with_user(username):
    if not session.get('admin'):
        return redirect(url_for('videochat.videochat_admin'))

    if username not in waiting_users:
        return "User not available", 404

    session['admin_in_room'] = True
    # Redirect admin to the admin-specific chat room for the chosen user
    return redirect(url_for('videochat.videochat_as_admin', username=username))

@app.route('/videochat/<username>')
def videochat(username):
    if session.get('user') == username and username in room_occupants:
        if room_occupants[username]["admin_joined"]:
            return render_template('videochat.html', username=username, role="user")
        else:
            return render_template('waiting.html', message="Waiting for admin to join...")
    
    session['user'] = username  # Store the user ID in the session
    return render_template('videochat.html', username=username, role="user")


@app.route('/videochat/videochat_admin/<username>')
def videochat_as_admin(username):
    if not session.get('admin'):
        return redirect(url_for('videochat.videochat_admin'))
    
    if username not in room_occupants:
        return "User not found", 404

    # Mark that admin has joined the room
    room_occupants[username]["admin_joined"] = True
    socketio.emit('admin_joined', {"message": "Admin has joined"}, to=username)  # Notify user that admin has joined
    return render_template('videochat.html', username=username, role="admin")


@socketio.on('connect')
def handle_connect():
    connected_users.add(request.sid)
    emit_user_status()

@socketio.on('disconnect')
def handle_disconnect():
    connected_users.discard(request.sid)
    emit_user_status()

@socketio.on('join')
def handle_join(data):
    username = data.get('username')
    room = data.get('room')
    join_room(room)

    # Update room_occupants if admin joins
    if session.get('admin'):
        room_occupants[username]["admin_joined"] = True
        socketio.emit('admin_joined', {"message": "Admin has joined"}, to=room)
    else:
        if room_occupants[username]["admin_joined"]:
            socketio.emit('user_in_call', {"message": "You are in a call with the admin"}, to=room)
        else:
            socketio.emit('waiting_for_admin', {"message": "Waiting for admin to join"}, to=room)

@socketio.on('signal')
def handle_signal(data):
    emit('signal', data, broadcast=True, include_self=False)

def emit_user_status():
    # Broadcast to all clients whether there is more than one user connected
    peer_available = len(connected_users) > 1
    socketio.emit('user_status', {'peerAvailable': peer_available})
