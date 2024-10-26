from flask import request, jsonify, render_template, Blueprint, flash, redirect, url_for
import speech_recognition as sr
from flask_login import current_user
import google.generativeai as genai

app = Blueprint('voicebot', __name__, template_folder='templates')

recognizer = sr.Recognizer()
genai.configure(api_key="AIzaSyDHLQe1XH7ZtwwvLrTc3x4Kk5dosQUUmio")
model = genai.GenerativeModel('gemini-1.5-flash', generation_config=genai.GenerationConfig(temperature=0.9))


@app.route('/voice', methods=['GET'])
def voice():
    if current_user.is_authenticated:
        return render_template('voice.html')
    flash('You need to log in to access the voice.', 'warning')
    return redirect(url_for('login_panel.login'))

@app.route('/generate-response', methods=['POST'])
def generate_response():
    if not current_user.is_authenticated:
        flash('You need to log in to access the voice feature.', 'warning')
        return redirect(url_for('login_panel.login'))
    
    data = request.json
    text = data['text']
    
    sys_message = ''' 
    You are an AI Medical Assistant trained on a vast dataset of health and mental health information. Please be thorough and
    provide an informative answer. If you don't know the answer to a specific medical inquiry, advise seeking professional help 
    and don't mention that 'I'm an AI and can't provide medical advice'. Do not be much creative.
    '''
    
    response = model.generate_content(f"{sys_message}, query: {text}")
    cleaned_text = response.text.replace('*', '')

    return jsonify({'response': cleaned_text})