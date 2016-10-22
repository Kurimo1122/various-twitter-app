import os
import logging
import tweepy
from flask import Flask, session, redirect, render_template, request

# Consumer Key
CONSUMER_KEY = os.environ['CONSUMER_KEY']

# Consumer Secret
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

# CALLBACK_URL (Will be redirected after authentication)
# CALLBACK_URL = 'https://tweet-stream-toshi.herokuapp.com/'
CALLBACK_URL = 'http://localhost:5000' # local environment

logging.warn('app start!')

# Start Flask
app = Flask(__name__)

# Set key to use session of flask
app.secret_key = os.environ['SECRET_KEY']

# Set root page
@app.route('/')
def index():

    # get user-timeline after authentication
    timeline = user_timeline()
    if timeline == False:
        print("False!")
    else:
        print("True!")
        for status in timeline:
					text = status.text
					print(text)


    return render_template('index.html', timeline=timeline)

# Set auth page
@app.route('/twitter_auth', methods=['GET'])
def twitter_auth():
    # Authentication using OAuth by tweepy
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)

    try:
        # Get the redirect_url
        redirect_url = auth.get_authorization_url()

        # Save the request_token which will be used after authentication
        session['request_token'] = auth.request_token
    
    except (tweepy.TweepError, e):
        logging.error(str(e))
    
    return redirect(redirect_url)

# Function to get user_timeline
def user_timeline():
    # Check request_token and oauth_verifier
    token = session.pop('request_token', None)
    verifier = request.args.get('oauth_verifier')
    
    if token is None or verifier is None:
        return False # if the authentication has not yet been done.

    # OAuth authentication using tweepy
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)

    # Get access token, Access token secret
    auth.request_token = token
    try:
        auth.get_access_token(verifier)
    except (tweepy.TweepError, e):
        logging.error(str(e))
        return {}

    # Access to Twitter API using tweepy
    api = tweepy.API(auth)

    # Get tweets (max: 100 tweets) list
    return api.user_timeline(count=100)
