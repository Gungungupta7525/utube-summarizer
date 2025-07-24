from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import requests

app = Flask(__name__)
CORS(app)

# 👇 Summarize using Groq
def summarize_transcript(transcript_text):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": "Bearer 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",  # Replace with your real key
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Summarize the following YouTube transcript:"},
            {"role": "user", "content": transcript_text}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    print("Groq response:", result)

    return result['choices'][0]['message']['content']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    video_url = data.get("video_url")
    video_id = extract_video_id(video_url)

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t["text"] for t in transcript])

        # Limit to 3000 words to avoid token limit errors
        words = full_text.split()
        if len(words) > 3000:
            words = words[:3000]
        trimmed_text = ' '.join(words)

        summary = summarize_transcript(trimmed_text)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)})

def extract_video_id(url):
    import re
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

if __name__ == '__main__':
    app.run(debug=True)
