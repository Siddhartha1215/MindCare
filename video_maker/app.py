from flask import render_template, request, Blueprint
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai_api_key = os.getenv("GENAI_API_KEY")
youtube_api_key = os.getenv("YOUTUBE_API_KEY")

genai.configure(api_key=genai_api_key)
model = genai.GenerativeModel('gemini-1.5-flash', generation_config=genai.GenerationConfig(temperature=0.9))

app = Blueprint('video_maker', __name__, template_folder='templates')

from googleapiclient.discovery import build

api_key=youtube_api_key

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

def get_video_link(query):
    # Call the search.list method to retrieve results matching the query
    request = youtube.search().list(
        part='snippet',
        q=query,
        type='video',
        maxResults=1
    )
    response = request.execute()
    
    # Extract video ID and create the YouTube link
    if response['items']:
        video_id = response['items'][0]['id']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return video_url
    else:
        return None


def get_embedded_url(youtube_url):
    if "watch?v=" in youtube_url:
        video_id = youtube_url.split("watch?v=")[-1]
        return f'<iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
    elif "youtu.be/" in youtube_url:
        video_id = youtube_url.split("youtu.be/")[-1]
        return f'<iframe src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
    else:
        return None
    
@app.route('/video_maker')
def video_maker():
    return render_template('video_maker.html')

@app.route('/submit', methods=['POST'])
def video_maker_submit():
    user_input = request.form['user_input']
    sys_message = ''' 
    You are an AI Sentiment Analysis Assistant trained on a comprehensive dataset of emotional
    expressions and media resources. Your task is to analyze a given sentence for its sentiment—whether it is positive,
    negative, or neutral. Once the sentiment is determined, provide a list of three YouTube video names
    that can help neutralize the identified emotional state. and make sure no extra text is included and give in names
    '''
    # user_input = "hey i am feeling very bad today as i was failed in an exam"
    response = model.generate_content(f"{sys_message}, query: {user_input}")
    cleaned_text = response.text.replace('*', '')
    cleaned_text=cleaned_text.split("\n")
    embedded_urls = []
    for url in cleaned_text:
        text=url
        url=get_video_link(url)
        new_url = get_embedded_url(url)
        if new_url is not None:
            embedded_urls.append([new_url,text])
    print(embedded_urls)
    if len(embedded_urls) >3:
        embedded_urls=embedded_urls[:3]
    return render_template('results.html', embedded_urls=embedded_urls)