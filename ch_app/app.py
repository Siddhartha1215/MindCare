from flask import render_template, redirect, url_for, session, jsonify, Blueprint, request
from flask_socketio import join_room, send, emit
from flask_login import current_user
from socket_instance import socketio

app = Blueprint('ch_app', __name__, template_folder='templates')

ADMIN_TOKEN = "meow"
waiting_users = []
room_occupants = {}  # Dictionary to track if admin has joined a user room

@app.route('/ch')
def ch():
    return render_template('ch.html')

@app.route('/ch_admin_dashboard')
def ch_admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('ch_app.ch_admin'))
    return render_template('ch_admin_dashboard.html')

@app.route('/ch_admin', methods=['GET', 'POST'])
def ch_admin():
    if request.method == 'POST':
        token = request.form.get('token')
        if token == ADMIN_TOKEN:
            session['admin'] = True
            return redirect(url_for('ch_app.ch_admin_dashboard'))
        else:
            return render_template('ch_admin_login.html', error="Invalid token")
    return render_template('ch_admin_login.html')

@app.route('/ch_start_chat')
def ch_start_chat():
    if current_user.is_authenticated:
        username = current_user.username
    else:
        username = "user_" + str(len(waiting_users) + 1)  # Generate a username if not logged in

    session['user'] = username
    if username not in waiting_users:
        waiting_users.append(username)
    room_occupants[username] = {"admin_joined": False}  # Track if admin has joined
    return {"status": "waiting", "message": "Waiting for admin to join...", "username": username}


@app.route('/ch_get_waiting_users')
def ch_get_waiting_users():
    return jsonify({"users": waiting_users})

@app.route('/ch_start_chat_with_user/<username>')
def ch_start_chat_with_user(username):
    session['admin_in_room'] = True
    # Redirect admin to the admin-specific chat room for the chosen user
    return redirect(url_for('ch_app.ch_chat_as_admin', username=username))

@app.route('/ch_chat/<username>')
def ch_chat(username):
    # User joins the chat room
    session['user'] = username  # Store the user ID in the session
    return render_template('ch_chat.html', username=username, role="user")

@app.route('/ch_chat/ch_admin/<username>')
def ch_chat_as_admin(username):
    # Mark that admin has joined the room
    if username in room_occupants:
        room_occupants[username]["admin_joined"] = True
    return render_template('ch_chat.html', username=username, role="admin")

# WebSocket for real-time messaging
@socketio.on('ch_join')
def ch_handle_join(data):
    room = data.get('room')
    role = data.get('role')

    if not room:
        return
    join_room(room)
    if role == "admin":
        if room in room_occupants:
            room_occupants[room]["admin_joined"] = True
        send("Admin has joined the chat.", room=room)
        emit('admin_has_joined', {'message': "Admin has joined the chat"}, room=room)
    else:
        if room in room_occupants and not room_occupants[room].get("admin_joined", False):
            emit('waiting_for_admin', {'message': "Waiting for admin to join..."}, room=room)

    send(f"{role.capitalize()} has entered the chat.", room=room)


@socketio.on('ch_message')
def ch_handle_message(data):
    room = data.get('room')
    message = data.get('message')
    role = data.get('role')

    if not room or not message or not role:
        return
    
    emit('ch_message', f"{message}", room=room)
