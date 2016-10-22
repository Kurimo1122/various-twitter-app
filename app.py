import os
import logging
import tweepy
from flask import Flask, session, redirect, render_template, request
from igo.Tagger import Tagger
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import codecs


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
    text_list = []
    wakati_list = []
    text_all = ""
    wakati_all = ""

    fpath = "./Fonts/ヒラギノ角ゴシック W4.ttc"
    
    if timeline == False:
        print("False!")
    else:
        print("True!")
        
        for status in timeline:
            text = status.text
            if 'RT' in text:
                pass
            elif '@' in text:
                pass
            else:
                text_list.append(text)
        text_all = "".join(text_list)

        tagger = Tagger()
        wakati_text = tagger.parse(text_all)

        for word in wakati_text:
            if '名詞' in word.feature:
                wakati_list.append(word.surface)

        wakati_all = " ".join(wakati_list)

        wordcloud = WordCloud(
                background_color = 'white',
                max_font_size = 40,
                relative_scaling = .5,
                # width = 900,
                # height = 500,
                font_path = fpath,
                #stopwords = set(stop_words)
                ).generate(wakati_all)
        #TODO Something wrong with following three lines
        output = plt.figure()
        #plt.imshow(wordcloud)
        #plt.savefig('/static/images/output.png')
        
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

