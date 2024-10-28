# Mind Care

## Technologies Used
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask, Python
- **Database:** MongoDB
- **APIs:** [Gemini API](https://aistudio.google.com/apikey), [YouTube Search](https://console.cloud.google.com/apis/dashboard)
- **Others:** Git, GitHub

## Project Description
Mind Care is an innovative web application designed to relieve stress and improve mental well-being. It provides users with a platform to engage in anonymous conversations, join chat rooms dedicated to specific health topics, interact with an AI support assistant, and access licensed therapist consultations. This project addresses the growing need for accessible mental health resources, making it easier for individuals to seek help and find community support.

In addition, Mind Care enables users to analyze symptoms through its Symptom Analyzer, which identifies potential conditions based on user input. The app also recommends YouTube videos that match the user's emotional state, using sentiment analysis on the user's text to provide tailored content for relaxation and well-being.

## API References
- **Gemini API:** [API Documentation](https://aistudio.google.com/apikey)  
  - To obtain an API key, sign up at Google Studio and follow the instructions on their platform.

- **YouTube Search API:** [API Documentation](https://console.cloud.google.com/apis/dashboard)  
  - To obtain an API key, create a Google Cloud Console account, navigate to the APIs & Services dashboard, and generate credentials.

## Demo Video
Watch the demo of the Mind Care app on YouTube: [Mind Care Demo](https://youtu.be/tG4C4Ns6sE4)

## Installation and Setup
To set up the Mind Care project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Siddhartha1215/MindCare.git
   cd MindCare
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main_app.py
   ```

4. **Access the app:**
   Open your browser and go to `http://localhost:5000` to start using Mind Care.

## Future Scope
- Integration with IoT or wearable devices to monitor and assess stress levels in real time.
- Potential collaboration with psychiatric hospitals or mental health organizations to offer Mind Care as part of their digital care toolkit.
- Expansion of AI-driven features, such as personalized wellness recommendations and progress tracking based on user interactions and well-being data.
