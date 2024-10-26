import speech_recognition as sr
import google.generativeai as genai


API_KEY = "AIzaSyDHLQe1XH7ZtwwvLrTc3x4Kk5dosQUUmio"
recognizer = sr.Recognizer()
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash', generation_config=genai.GenerationConfig(temperature=0.9))


# todo- here you can use whatever frontend mechanism to get your audio input and save it inside "audio" variable
with sr.Microphone() as source:
    print("Please say something:")
    audio = recognizer.listen(source)

try:
    text = recognizer.recognize_google(audio)
except sr.UnknownValueError:
    text = None
except sr.RequestError as e:
    text = None


sys_message = ''' 
        You are an AI Medical Assistant trained on a vast dataset of health and mental health information. Please be thorough and
        provide an informative answer. If you don't know the answer to a specific medical inquiry, advise seeking professional help. Do not be much creative.
        '''
if text:
    response = model.generate_content(f"{sys_message}, query: {text}")
else:
    response = None

if response:
    print(response.text)
else:
    print("Sorry, I couldn't understand you.")