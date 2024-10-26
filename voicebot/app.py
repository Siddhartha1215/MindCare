from flask import Flask, request, jsonify, render_template, send_file
import speech_recognition as sr
import google.generativeai as genai
from gtts import gTTS
from pydub import AudioSegment
import io

app = Flask(__name__)

recognizer = sr.Recognizer()
genai.configure(api_key="AIzaSyDHLQe1XH7ZtwwvLrTc3x4Kk5dosQUUmio")
model = genai.GenerativeModel('gemini-1.5-flash', generation_config=genai.GenerationConfig(temperature=0.9))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-response', methods=['POST'])
def generate_response():
    data = request.json
    text = data['text']
    
    sys_message = ''' 
    You are an AI Medical Assistant trained on a vast dataset of health and mental health information. Please be thorough and
    provide an informative answer. If you don't know the answer to a specific medical inquiry, advise seeking professional help 
    and don't mention that 'I'm an AI and can't provide medical advice'. Do not be much creative.
    '''
    
    response = model.generate_content(f"{sys_message}, query: {text}")
    cleaned_text = response.text.replace('*', '')

    # Convert cleaned text to audio
    # tts = gTTS(text=cleaned_text, lang='en')
    # audio_file = io.BytesIO()
    # tts.write_to_fp(audio_file)
    # audio_file.seek(0)
    
    # # Save audio to a file
    # audio_segment = AudioSegment.from_mp3(audio_file)
    # audio_segment.export("static/response_audio.mp3", format="mp3")
    
    return jsonify({'response': cleaned_text})

if __name__ == '__main__':
    app.run(debug=True)
