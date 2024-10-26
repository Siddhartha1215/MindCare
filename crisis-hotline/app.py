from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

admin_token = "meow"
waiting_users = []
room_occupants = {}  # Dictionary to track if admin has joined a user room

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        token = request.form.get('token')
        if token == admin_token:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid Token"
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/start_chat')
def start_chat():
    user_id = "user_" + str(len(waiting_users) + 1)
    session['user'] = user_id
    if user_id not in waiting_users:
        waiting_users.append(user_id)
    room_occupants[user_id] = {"admin_joined": False}  # Track if admin has joined
    return {"status": "waiting", "message": "Waiting for admin to join...", "user_id": user_id}

@app.route('/get_waiting_users')
def get_waiting_users():
    return jsonify({"users": waiting_users})


@app.route('/start_chat_with_user/<username>')
def start_chat_with_user(username):
    session['admin_in_room'] = True
    # Redirect admin to the admin-specific chat room for the chosen user
    return redirect(url_for('chat_as_admin', username=username))


@app.route('/chat/<username>')
def chat(username):
    # User joins the chat room
    session['user'] = username  # Store the user ID in the session
    return render_template('chat.html', username=username, role="user")

@app.route('/chat/admin/<username>')
def chat_as_admin(username):
    # Mark that admin has joined the room
    room_occupants[username]["admin_joined"] = True  
    return render_template('chat.html', username=username, role="admin")

# WebSocket for real-time messaging
@socketio.on('join')
def handle_join(data):
    room = data['room']
    role = data['role']

    join_room(room)
    
    # Notify room occupants about the joining
    if role == "admin":
        room_occupants[room]["admin_joined"] = True
        send("Admin has joined the chat.", room=room)
    else:
        if not room_occupants[room]["admin_joined"]:
            emit('waiting_for_admin', {'message': "Waiting for admin to join..."})
    
    send(f"{role.capitalize()} has entered the chat.", room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    role = data['role']
    send(f"{role.capitalize()}: {data['message']}", room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
