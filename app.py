import requests
import random
import logging
import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__, 
            static_folder='static', 
            template_folder='templates')

# More comprehensive CORS configuration
CORS(app)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
def fetch_memes(subreddit='memes', limit=50):
    """
    Fetch memes from a specific subreddit with improved headers
    """
    memes = []
    try:
        # More comprehensive headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': f'https://www.reddit.com/r/{subreddit}/',
            'Origin': 'https://www.reddit.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }

        # Alternative meme sources if Reddit fails
        alternative_sources = [
            'https://api.imgflip.com/get_memes',
            'https://meme-api.com/gimme/50'
        ]

        # Try Reddit first
        response = requests.get(
            f'https://www.reddit.com/r/{subreddit}/top.json', 
            params={'limit': limit, 't': 'day'},
            headers=headers
        )
        
        # Check if request was successful
        if response.status_code == 200:
            reddit_data = response.json()
            
            for post in reddit_data['data']['children']:
                # Filter for image posts
                if (post['data'].get('url_overridden_by_dest') and 
                    any(post['data']['url_overridden_by_dest'].lower().endswith(ext) 
                        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp'])):
                    meme = {
                        'url': post['data']['url_overridden_by_dest'],
                        'subreddit': post['data']['subreddit'],
                        'title': post['data']['title']
                    }
                    memes.append(meme)
        
        # If Reddit fails, try alternative sources
        if not memes:
            for source_url in alternative_sources:
                try:
                    alt_response = requests.get(source_url)
                    if alt_response.status_code == 200:
                        alt_data = alt_response.json()
                        
                        # Handle different API response structures
                        if 'data' in alt_data and 'memes' in alt_data['data']:
                            # Imgflip API
                            memes = [
                                {
                                    'url': meme['url'],
                                    'title': meme.get('name', 'Meme'),
                                    'subreddit': 'Imgflip'
                                } 
                                for meme in alt_data['data']['memes']
                            ]
                        elif 'memes' in alt_data:
                            # Meme API
                            memes = [
                                {
                                    'url': meme['url'],
                                    'title': meme.get('title', 'Meme'),
                                    'subreddit': meme.get('subreddit', 'Unknown')
                                } 
                                for meme in alt_data['memes']
                            ]
                        
                        if memes:
                            break
                except Exception as e:
                    logging.error(f"Error fetching from alternative source {source_url}: {e}")
        
        # Shuffle memes
        random.shuffle(memes)
        return memes[:limit]
    
    except Exception as e:
        logging.error(f"Error fetching memes: {e}")
        return []

@app.route('/')
def index():
    """
    Render the main page
    """
    return render_template('index.html')

@app.route('/api/memes')
def get_memes():
    """
    API endpoint to get memes
    """
    try:
        memes = fetch_memes()
        
        # Ensure we have memes
        if not memes:
            # Hardcoded fallback memes
            memes = [
                {
                    'url': 'https://i.imgflip.com/1bij.jpg',
                    'title': 'Fallback Meme 1',
                    'subreddit': 'Fallback'
                },
                {
                    'url': 'https://i.imgflip.com/1bim.jpg',
                    'title': 'Fallback Meme 2',
                    'subreddit': 'Fallback'
                }
            ]
        
        return jsonify(memes)
    except Exception as e:
        logging.error(f"API memes error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    """
    Custom 404 error handler
    """
    return jsonify(error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    """
    Custom 500 error handler
    """
    return jsonify(error="Internal server error"), 500

# Debugging route
@app.route('/debug')
def debug():
    return jsonify({
        "status": "ok",
        "message": "Debug endpoint is working"
    })


