from flask import Flask, jsonify
from flask_cors import CORS
import tweepy
import os

app = Flask(__name__)
CORS(app)

# CONFIGURATION - Remplacez par vos credentials Twitter
# Créez une app gratuite sur: https://developer.twitter.com/en/portal/dashboard
BEARER_TOKEN = "VOTRE_BEARER_TOKEN_ICI"

client = tweepy.Client(bearer_token=BEARER_TOKEN)

@app.route('/tweets/<username>')
def get_tweets(username):
    try:
        # Récupérer l'utilisateur
        user = client.get_user(username=username, user_fields=['profile_image_url'])
        user_id = user.data.id
        
        # Récupérer les tweets
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=10,
            tweet_fields=['created_at', 'attachments'],
            media_fields=['url', 'preview_image_url'],
            expansions=['attachments.media_keys']
        )
        
        result = []
        media_dict = {}
        
        # Mapper les médias
        if tweets.includes and 'media' in tweets.includes:
            for media in tweets.includes['media']:
                media_dict[media.media_key] = media.url if hasattr(media, 'url') else None
        
        # Formatter les tweets
        for tweet in tweets.data:
            images = []
            if tweet.attachments:
                for key in tweet.attachments.get('media_keys', []):
                    if key in media_dict and media_dict[key]:
                        images.append(media_dict[key])
            
            result.append({
                'username': username,
                'text': tweet.text,
                'date': tweet.created_at.isoformat(),
                'images': images
            })
        
        return jsonify({'tweets': result})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
