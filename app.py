# coding:utf-8
import io
import os
from os import path
import numpy as np
import logging
import tweepy
from flask import Flask, session, redirect, render_template, request, send_file
from igo.Tagger import Tagger
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import random
import string
import codecs

from PIL import Image


# Consumer Key
CONSUMER_KEY = os.environ['CONSUMER_KEY']

# Consumer Secret
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']

# CALLBACK_URL (Will be redirected after authentication)
CALLBACK_URL = 'https://twitter-word-cloud-toshi.herokuapp.com'
#CALLBACK_URL = 'http://localhost:5000' # local environment

logging.warn('app start!')

# Start Flask
app = Flask(__name__)

# Set key to use session of flask
app.secret_key = os.environ['SECRET_KEY']

timeline = False

# Set root page
@app.route('/')
def index():
    # get user-timeline after authentication
    #global timeline
    timeline = user_timeline()
    #if timeline == True:
    #    session['user_timeline'] = timeline
     
    timeline_list = []
        
    text_list = []
    wakati_list = []
    text_all = ""
    wakati_all = "友達"
    user_image = ""

   
    if timeline == False:
        pass
    else:
        user_image = timeline[0].user.profile_image_url
        for status in timeline:
            text = status.text
            if 'RT' in text:
                pass
            else:
                text_list.append(text)
    text_all = "".join(text_list)

    tagger = Tagger()
    wakati_text = tagger.parse(text_all)

    for word in wakati_text:
        if '名詞'.decode('utf-8') in word.feature:
            wakati_list.append(word.surface)

    wakati_all = " ".join(wakati_list)
    print(wakati_all)
    session['wakati_all'] = wakati_all
    #print(user_id)
    #print(timeline_list) 
    return render_template('index.html', timeline=timeline, user_image=user_image)

@app.route('/word_cloud/<user_id>', methods=['GET', 'POST'])
def word_cloud(user_id):
    fpath = "Fonts/NotoSansCJKjp-Medium.otf"
    
    d = path.dirname(__file__)

    alice_mask = np.array(Image.open(path.join(d, "alice_mask.png")))

    wakati_all = session.get('wakati_all').decode('utf-8')
    print(wakati_all)

    wordcloud = WordCloud(
        background_color = 'white',
        max_font_size = 40,
        relative_scaling = .5,
        # width = 900,
        # height = 500,
        font_path = fpath,
        #stopwords = set(stop_words)
        mask = alice_mask,
        ).generate(wakati_all)
           
    fig = plt.figure()
    plt.imshow(wordcloud)
    plt.axis("off")
        
        #fig, ax = plt.subplots(1)
        #ppl.bar(ax, np.arange(10), np.abs(np.random.randn(10)))
        #canvas = FigureCanvas(fig)

        #f = tempfile.TemporaryFile()
    img = io.BytesIO()
        #strio = StringIO()
        #fig.savefig(strio, format="svg")
    fig.savefig(img)
        #plt.close(fig)
    img.seek(0)
    response = send_file(img, mimetype='image/png')
    return response

        #f.close()

        #strio.seek(0)
        #svgstr = strio.buf[strio.buf.find("<svg"):]
        #return send_file(strio, attachment_filename='graph2.png', as_attachment=True)
    #return render_template("sin.html", svgstr=svgstr.decode("utf-8"), timeline=timeline)


@app.route('/images')
def images():
    return render_template("test.html")



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
        logging.error(str(e).decode('utf-8'))
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
    except (tweepy.TweepError):
        #logging.error(str(e))
        return {}

	# Access to Twitter API using tweepy
    api = tweepy.API(auth)
	
	# Get tweets (max: 100 tweets) list
    return api.user_timeline(count=100)

