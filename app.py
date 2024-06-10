from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

app = Flask(__name__)
CORS(app)

summarizer = pipeline("summarization")

def get_video_id(url):
    from urllib.parse import urlparse, parse_qs
    query = urlparse(url).query
    params = parse_qs(query)
    return params["v"][0] if "v" in params else None

@app.route('/api/youtube-summary', methods=['POST'])
def summarize_youtube():
    data = request.json
    youtube_url = data.get('youtube_url')
    video_id = get_video_id(youtube_url)

    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
        
        # Summarize the transcript
        summary = summarizer(full_text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']

        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
