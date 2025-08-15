# backend/app.py
from sqlite3 import DataError
from flask import Flask, json, request, jsonify, send_file
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from urllib.parse import urlparse, parse_qs
from flask_cors import CORS
import re
from collections import defaultdict
from googleapiclient.discovery import build
import os

from gtts import gTTS
import io

app = Flask(__name__)
CORS(app)  # allow frontend to call

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise ValueError("❌ YOUTUBE_API_KEY is missing. Set it in your .env file.")

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@app.route('/trending-videos', methods=['GET'])
def get_trending_videos():
    try:
        # Get trending videos from YouTube API
        search_response = youtube.videos().list(
            part='snippet',
            chart='mostPopular',
            maxResults=12,
            regionCode='US'  # Change to your preferred region
        ).execute()
        
        videos = []
        for item in search_response.get('items', []):
            video_id = item['id']
            videos.append({
                'id': video_id,
                'title': item['snippet']['title'],
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'channel': item['snippet']['channelTitle']
            })
            
        return jsonify({
            'videos': videos,
            'status': 'success'
        })
    except Exception as e:
        print("Error in /trending-videos:", str(e))
        return jsonify({
            'error': 'Failed to fetch trending videos',
            'details': str(e)
        }), 500
    
    
# ---
    
# --- utility: accept either a full YouTube URL or a raw video id ---
# def extract_video_id(url_or_id: str):
#     if not url_or_id:
#         return None
#     # if already a video id (11 chars)
#     if re.fullmatch(r'[0-9A-Za-z_-]{11}', url_or_id):
#         return url_or_id
#     try:
#         from urllib.parse import urlparse, parse_qs
#         parsed = urlparse(url_or_id)
#         hostname = (parsed.hostname or "").lower()
#         if 'youtu.be' in hostname:
#             return parsed.path.lstrip('/').split('?')[0]
#         if 'youtube' in hostname:
#             if parsed.path == '/watch':
#                 return parse_qs(parsed.query).get('v', [None])[0]
#             parts = parsed.path.split('/')
#             # /embed/<id> or /v/<id>
#             if 'embed' in parts or 'v' in parts:
#                 return parts[-1]
#     except Exception:
#         pass
#     return None


# ---


# def summarize_text(text, num_sentences=3):
#     if not text.strip():
#         return "No summary available"
    
#     # Improved sentence splitting
#     sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text.strip())
#     if len(sentences) <= num_sentences:
#         return text
        
#     # More comprehensive stopwords
#     stopwords = {
#         "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
#         "the", "a", "an", "and", "but", "if", "or", "because", "as", "until", "while",
#         "at", "by", "for", "with", "about", "against", "between", "into", "through",
#         "during", "before", "after", "above", "below", "to", "from", "up", "down", "in",
#         "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
#         "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
#         "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
#         "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
#     }
    
#     # Score sentences by word frequency
#     word_freq = {}
#     words = re.findall(r'\b\w+\b', text.lower())
#     for word in words:
#         if word not in stopwords:
#             word_freq[word] = word_freq.get(word, 0) + 1
    
#     # Score sentences
#     scored = []
#     for i, sentence in enumerate(sentences):
#         score = sum(word_freq.get(word.lower(), 0) for word in re.findall(r'\b\w+\b', sentence))
#         scored.append((score, i, sentence))
    
#     # Get top sentences while preserving order
#     top = sorted(scored, key=lambda x: (-x[0], x[1]))[:num_sentences]
#     top_sorted = sorted(top, key=lambda x: x[1])
    
#     return ' '.join(s for _, _, s in top_sorted)


# ---


# @app.route('/get-transcript', methods=['POST'])
# def get_transcript():
#     body = request.get_json() or {}
#     # accept either videoId OR videoUrl to be flexible
#     raw = body.get('videoId') or body.get('videoUrl') or ''
#     video_id = extract_video_id(raw)
#     if not video_id:
#         return jsonify({'error': 'Missing or invalid videoId/videoUrl'}), 400

#     try:
#         # try default English transcript first
        
#         # transcript_list = YouTubeTranscriptApi.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
#         # full_text = ' '.join([t.get('text', '') for t in transcript_list]).strip()
#         transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['en', 'en-US', 'en-GB'])
#         full_text = ' '.join([t.text for t in transcript_list]).strip()

#         if not full_text:
#             raise Exception("Transcript fetched but empty")
#         summary = summarize_text(full_text, num_sentences=4)
#         return jsonify({'transcript': full_text, 'summary': summary, 'status': 'success'})
#     except NoTranscriptFound:
#         return jsonify({'error': 'No transcript available for this video'}, 400)
#     except TranscriptsDisabled:
#         return jsonify({'error': 'Transcripts are disabled by uploader'}, 400)
#     except Exception as e:
#         # log server-side for debugging
#         print("Error in /get-transcript:", str(e))
#         return jsonify({'error': f'Failed to fetch transcript: {str(e)}'}), 400

# ---

# def extract_video_id(url_or_id):
#     # Handles both raw IDs and full YouTube URLs
#     if len(url_or_id) == 11 and " " not in url_or_id:
#         return url_or_id
#     try:
#         parsed_url = urlparse(url_or_id)
#         if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
#             return parse_qs(parsed_url.query).get('v', [None])[0]
#         elif parsed_url.hostname == 'youtu.be':
#             return parsed_url.path.lstrip('/')
#     except:
#         pass
#     return None

# def summarize_text(text, num_sentences=4):
#     # Simple summarizer (can be replaced with an AI model)
#     sentences = text.split('. ')
#     return '. '.join(sentences[:num_sentences])

# @app.route('/get-transcript', methods=['POST'])
# def get_transcript():
#     body = request.get_json() or {}
#     video_id = extract_video_id(body.get('videoId') or body.get('videoUrl') or '')
#     if not video_id:
#         return jsonify({'error': 'Missing or invalid video ID'}), 400

#     try:
#         # Use the current fetch method
#         api = YouTubeTranscriptApi()
#         fetched = api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
#         # Convert to simple list of dicts
#         transcript_list = [
#             {'text': t.text, 'start': t.start, 'duration': t.duration}
#             for t in fetched
#         ]

#         full_text = " ".join([t['text'] for t in transcript_list]).strip()
#         summary = summarize_text(full_text, num_sentences=4)

#         return jsonify({
#             'transcript': transcript_list,
#             'summary': summary,
#             'status': 'success'
#         })

#     except NoTranscriptFound:
#         return jsonify({'error': 'No transcript available for this video'}), 400
#     except TranscriptsDisabled:
#         return jsonify({'error': 'Transcripts are disabled by uploader'}), 400
#     except Exception as e:
#         print("Error in /get-transcript:", e)
#         return jsonify({'error': f'Failed to fetch transcript: {e}'}), 400


# ---


def extract_video_id(url_or_id):
    # Handles both raw IDs and full YouTube URLs
    if len(url_or_id) == 11 and " " not in url_or_id:
        return url_or_id
    try:
        parsed_url = urlparse(url_or_id)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.hostname == 'youtu.be':
            return parsed_url.path.lstrip('/')
    except:
        pass
    return None

# def summarize_text(text, num_sentences=4):
#     # Simple summarizer (can be replaced with an AI model)
#     sentences = text.split('. ')
#     return '. '.join(sentences[:num_sentences])


def summarize_text(text, num_sentences=3):
    """
    Generates more concise summaries by:
    1. Better sentence selection
    2. Removing redundant phrases
    3. Forcing conclusion-like endings
    """
    if not text.strip():
        return "No summary available"

    # Improved sentence splitting with abbreviation handling
    sentences = [s.strip() for s in re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text) if s.strip()]
    
    if len(sentences) <= num_sentences:
        return text

    # Enhanced stopwords with YouTube-specific phrases
    stopwords = {
        "i", "me", "my", "we", "our", "you", "your", "the", "a", "an", "and", 
        "but", "if", "or", "because", "as", "at", "by", "for", "with", "about",
        "this", "that", "these", "those", "have", "has", "had", "do", "does", "did",
        "like", "subscribe", "watch", "video", "click", "channel", "turn", "notification",
        "hey", "hello", "welcome", "thanks", "thank", "please", "everyone", "everybody"
    }

    # Calculate meaningful word frequencies
    word_freq = defaultdict(int)
    for sentence in sentences:
        for word in re.findall(r'\b[a-z]{3,}\b', sentence.lower()):  # Only words >2 chars
            if word not in stopwords:
                word_freq[word] += 1

    # Score sentences with position weighting
    scored = []
    for i, sentence in enumerate(sentences):
        # Base score from important words
        words = re.findall(r'\b[a-z]{3,}\b', sentence.lower())
        score = sum(word_freq.get(word, 0) for word in words if word not in stopwords)
        
        # Boost opening/closing sentences (often contain conclusions)
        if i == 0 or i >= len(sentences)-2:
            score *= 1.5
            
        scored.append((score, i, sentence))
    
    # Select top sentences with diversity
    top_sentences = []
    selected_indices = set()
    
    # Always include the last sentence if it's a conclusion
    if len(sentences) > 1:
        last_sentence = sentences[-1]
        if any(keyword in last_sentence.lower() for keyword in ["conclusion", "summary", "finally"]):
            top_sentences.append((0, len(sentences)-1, last_sentence))
            selected_indices.add(len(sentences)-1)

    # Add remaining top sentences
    for score, i, sentence in sorted(scored, key=lambda x: (-x[0], x[1])):
        if i not in selected_indices and len(top_sentences) < num_sentences:
            top_sentences.append((score, i, sentence))
            selected_indices.add(i)

    # Re-sort to maintain original order
    top_sentences.sort(key=lambda x: x[1])
    
    # Join and clean the summary
    summary = ' '.join(s for _, _, s in top_sentences)
    
    # Remove repetitive openings
    summary = re.sub(r'^(hey|welcome|so)\W+', '', summary, flags=re.I)
    
    # Ensure proper ending
    if not re.search(r'[.!?]$', summary):
        summary = summary.rstrip() + '.'
    
    return summary

def transcribe_with_whisper(video_url):
    # Requires Whisper AI setup (OpenAI's Whisper or faster-whisper)
    import whisper
    model = whisper.load_model("base")
    result = model.transcribe(video_url)
    return [{'text': seg['text'], 'start': seg['start'], 'duration': seg['end']-seg['start']} 
            for seg in result['segments']]

def generate_from_metadata(video_id):
    # Use YouTube API to get video description and auto-captions
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    
    description = response['items'][0]['snippet']['description']
    # Basic processing to create "fake" transcript segments
    sentences = [s.strip() for s in description.split('.') if s.strip()]
    return [{'text': s, 'start': i*5, 'duration': 5} for i, s in enumerate(sentences)]

@app.route('/get-transcript', methods=['POST'])
def get_transcript():
    body = request.get_json() or {}
    video_id = extract_video_id(body.get('videoId') or body.get('videoUrl') or '')
    if not video_id:
        return jsonify({'error': 'Missing or invalid video ID'}), 400

    try:
        # First try: YouTube's official transcript
        try:
            api = YouTubeTranscriptApi()
            fetched = api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
            transcript_list = [
                {'text': t.text, 'start': t.start, 'duration': t.duration}
                for t in fetched
            ]
            full_text = " ".join([t['text'] for t in transcript_list]).strip()
            summary = summarize_text(full_text, num_sentences=4)

            return jsonify({
                'transcript': transcript_list,
                'summary': summary,
                'source': 'youtube',
                'status': 'success'
            })

        except (NoTranscriptFound, TranscriptsDisabled) as yt_error:
            # Fallback 1: Use Whisper AI for audio transcription
            try:
                audio_url = f"https://www.youtube.com/watch?v={video_id}"
                transcript_list = transcribe_with_whisper(audio_url)
                full_text = " ".join([t['text'] for t in transcript_list]).strip()
                summary = summarize_text(full_text, num_sentences=4)

                return jsonify({
                    'transcript': transcript_list,
                    'summary': summary,
                    'source': 'whisper',
                    'status': 'success'
                })
            except Exception as whisper_error:
                # Fallback 2: Generate from video description/automatic captions
                transcript_list = generate_from_metadata(video_id)
                full_text = " ".join([t['text'] for t in transcript_list]).strip()
                summary = summarize_text(full_text, num_sentences=4)

                return jsonify({
                    'transcript': transcript_list,
                    'summary': summary,
                    'source': 'generated',
                    'status': 'success'
                })

    except Exception as e:
        print("Error in /get-transcript:", e)
        return jsonify({'error': f'Failed to fetch transcript: {e}'}), 400
    
    
# ---
    
# @app.route('/search-videos', methods=['POST'])
# def search_videos():
#     body = request.get_json() or {}
#     query = body.get('query', '').strip()
#     if not query:
#         return jsonify({'error': 'Missing search query'}), 400
    
#     try:
#         # # Ensure your API key is properly configured
#         # if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == 'AIzaSyBNrlmMlakIZqE2x7dHLhyqMJQ8_34kXbA':
#         #     return jsonify({'error': 'YouTube API key not configured'}), 500
            
#         search_response = youtube.search().list(
#             q=query,
#             part='id,snippet',
#             maxResults=10,
#             type='video',
#             safeSearch="none"  # Add this to avoid restrictions
#         ).execute()
        
#         videos = []
#         for item in search_response.get('items', []):
#             video_id = item['id']['videoId']
#             videos.append({
#                 'videoId': video_id,
#                 'title': item['snippet']['title'],
#                 'thumbnail': item['snippet']['thumbnails']['default']['url'],
#                 'channel': item['snippet']['channelTitle']
#             })
            
#         return jsonify({'videos': videos, 'status': 'success'})
#     except Exception as e:
#         print("Error in /search-videos:", str(e))
#         return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/search-videos', methods=['POST'])
def search_videos():
    body = request.get_json() or {}
    query = body.get('query', '').strip()
    if not query:
        return jsonify({'error': 'Missing search query'}), 400
    
    try:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=10,
            type='video'
        ).execute()
        
        videos = []
        for item in search_response.get('items', []):
            if item['id']['kind'] == 'youtube#video':
                videos.append({
                    'videoId': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'thumbnail': item['snippet']['thumbnails']['default']['url'],
                    'channel': item['snippet']['channelTitle']
                })
                
        return jsonify({
            'videos': videos,
            'status': 'success',
            'query': query  # Return the original query for reference
        })
    except Exception as e:
        print("Error in /search-videos:", str(e))
        return jsonify({
            'error': 'Search failed. Please try again later.',
            'details': str(e)
        }), 500
        
@app.route('/video-details', methods=['POST'])
def get_video_details():
    body = request.get_json() or {}
    video_id = body.get('videoId')
    if not video_id:
        return jsonify({'error': 'Missing videoId'}), 400

    try:
        response = youtube.videos().list(
            part='snippet,contentDetails',
            id=video_id
        ).execute()
        
        if not response['items']:
            return jsonify({'error': 'Video not found'}), 404
            
        item = response['items'][0]
        return jsonify({
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'duration': item['contentDetails']['duration'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
            'channel': item['snippet']['channelTitle'],
            'publishedAt': item['snippet']['publishedAt'],
            'status': 'success'
        })
    except Exception as e:
        print("Error in /video-details:", str(e))
        return jsonify({'error': str(e)}), 500   
         
@app.route('/translate-voice', methods=['POST'])
def translate_voice():
    data = request.get_json()
    text = data.get('text', '')
    language = data.get('language', 'es')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Create speech from text
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save to bytes buffer
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        
        return send_file(
            audio_bytes,
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)