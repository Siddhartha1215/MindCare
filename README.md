# MindCare

Mind Care is an innovative web application designed to relieve stress and improve mental well-being. It provides users with a platform to engage in anonymous conversations, join chat rooms dedicated to specific health topics, interact with an AI support assistant, and access licensed therapist consultations. This project addresses the growing need for accessible mental health resources, making it easier for individuals to seek help and find community support.

In addition, Mind Care enables users to analyze symptoms through its Symptom Analyzer, which identifies potential conditions based on user input. The app also recommends YouTube videos that match the user's emotional state, using sentiment analysis on the user's text to provide tailored content for relaxation and well-being.

## Features

- **User Authentication**: Register and login system for users and admins.
- **Chat System**: Real-time chat between users and admins/therapists.
- **Symptom Checker**: Users can select symptoms and get results based on a trained model.
- **Video Chat**: Secure video chat functionality for remote therapy sessions.
- **Voice Bot**: Voice-based interaction for accessibility.
- **Admin Dashboards**: Separate dashboards for managing users and sessions.
- **Modular Structure**: Each feature is encapsulated in its own Flask blueprint/app.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Siddhartha1215/MindCare.git
cd MindCare
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install Dependencies
<<<<<<< HEAD

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file (if needed) for sensitive settings like secret keys and database URIs.

Example:
```
GENAI_API_KEY=API_KEY
YOUTUBE_API_KEY=API_KEY
MONGO_URL=your_mongodb_uri
```

### 5. Run the Application

```bash
python main_app.py
```

The app will be available at `http://localhost:5000/` by default.

## Directory Details

- **ch_app/**, **chat_app/**: Chat functionality, with templates and static files.
- **login_panel/**: Handles user registration and login.
- **symptom/**: Symptom selection and result prediction (uses `Training.csv`).
- **video_maker/**: Tools for creating video content.
- **videochat/**: Video chat rooms and admin management.
- **voicebot/**: Voice-based interaction.
- **static/**: All CSS, JS, and image assets.
- **templates/**: Shared HTML templates.
- **mongo.py**: MongoDB connection logic.
- **shared.py**: Shared functions/utilities.
- **socket_instance.py**: Socket.IO setup for real-time features.

## Technologies Used

- Python 3
- Flask
- Flask-SocketIO
- MongoDB (via PyMongo)
- HTML, CSS, JavaScript
- [Other dependencies in requirements.txt]

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.
=======

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file (if needed) for sensitive settings like secret keys and database URIs.

Example:
```
GENAI_API_KEY=API_KEY
YOUTUBE_API_KEY=API_KEY
MONGO_URL=your_mongodb_uri
```

### 5. Run the Application

```bash
python main_app.py
```

The app will be available at `http://localhost:5000/` by default.

## Directory Details

- **ch_app/**, **chat_app/**: Chat functionality, with templates and static files.
- **login_panel/**: Handles user registration and login.
- **symptom/**: Symptom selection and result prediction (uses `Training.csv`).
- **video_maker/**: Tools for creating video content.
- **videochat/**: Video chat rooms and admin management.
- **voicebot/**: Voice-based interaction.
- **static/**: All CSS, JS, and image assets.
- **templates/**: Shared HTML templates.
- **mongo.py**: MongoDB connection logic.
- **shared.py**: Shared functions/utilities.
- **socket_instance.py**: Socket.IO setup for real-time features.

## Technologies Used

- Python 3
- Flask
- Flask-SocketIO
- MongoDB (via PyMongo)
- HTML, CSS, JavaScript
- [Other dependencies in requirements.txt]

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

>>>>>>> bd14b9b73d7719b0650377cb05c84529ffac4bd5
