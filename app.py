from flask import Flask, render_template, jsonify
import requests
import random
from flask_cors import CORS

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": [
            "Content-Type", 
            "Authorization", 
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Origin"
        ],
        "supports_credentials": True
    }
})

# Add additional headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

def fetch_memes(subreddit='memes', limit=50):
    """
    Fetch memes from a specific subreddit
    """
    memes = []
    try:
        headers = {
            'User-Agent': 'MemeNavigator/1.0'
        }
        response = requests.get(
            f'https://www.reddit.com/r/{subreddit}/top.json', 
            params={'limit': limit, 't': 'day'},
            headers=headers
        )
        
        # Check if request was successful
        if response.status_code != 200:
            print(f"Failed to fetch memes. Status code: {response.status_code}")
            return []

        reddit_data = response.json()
        
        for post in reddit_data['data']['children']:
            # Filter for image posts
            if (post['data'].get('url_overridden_by_dest') and 
                any(post['data']['url_overridden_by_dest'].lower().endswith(ext) 
                    for ext in ['.jpg', '.jpeg', '.png', '.gif'])):
                meme = {
                    'url': post['data']['url_overridden_by_dest'],
                    'subreddit': post['data']['subreddit'],
                    'title': post['data']['title']
                }
                memes.append(meme)
        
        return memes
    
    except Exception as e:
        print(f"Error fetching memes: {e}")
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
    # You can make this more dynamic by allowing subreddit selection
    memes = fetch_memes()
    
    # Shuffle memes to provide variety
    random.shuffle(memes)
    
    return jsonify(memes)

@app.errorhandler(404)
def page_not_found(e):
    """
    Custom 404 error handler
    """
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """
    Custom 500 error handler
    """
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",  # Listen on all available network interfaces
        port=5000,       # Default Flask port
        debug=True       # Enable debug mode during development
    )
