import flask

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from eventregistry import *
import argparse
import shlex

import search_NYT
import search_twitter
import search_youtube
from private import key_store

import string
from nltk.corpus import stopwords
import datetime as dt
from flaskext.mysql import MySQL

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "private/info.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = flask.Flask(__name__, template_folder='templates')
app.secret_key = 'appsecretkey'
# mysql set up
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
# NOTE MUST INSERT YOUR OWN PASSWORD
app.config['MYSQL_DATABASE_PASSWORD'] = key_store.get_mysql_pass()
app.config['MYSQL_DATABASE_DB'] = 'NovelNews'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'

mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load the credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    client = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    if flask.request.method == 'POST':
        return flask.redirect(flask.url_for('search'))

    else:
        info = get_today_info()

        article = info['article']
        tweets = info['tweets']
        yt = info['youtube']
        disp_date = info['date']

        videos = "https://www.youtube.com/embed/VIDEO_ID?playlist="
        for title, id in yt:
            videos = videos + ',' + id

        return flask.render_template('mainPage.html', article = article, tweets = tweets, videos = videos, date = disp_date)


@app.route('/authorize')
def authorize():
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow
    # steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    authorization_url, state = flow.authorization_url(
        # This parameter enables offline access which gives your application
        # both an access and refresh token.
        access_type='offline',
        # This parameter enables incremental auth.
        include_granted_scopes='true')

    # Store the state in the session so that the callback can verify that
    # the authorization server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verify the authorization server response.
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session.
    # ACTION ITEM for developers:
    #     Store user's access and refresh tokens in your data store if
    #     incorporating this code into your real app.
    credentials = flow.credentials
    flask.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

    return flask.redirect(flask.url_for('index'), code = 302)


@app.route('/search', methods=['GET', 'POST'])
def search():

    search_date = flask.request.form.get('search')
    today = dt.date.today()
    today = str(today)
    if search_date == today:
        info = get_today_info()
    else:
        print(search_date)
        info = search_results(search_date)

    article = info['article']
    tweets = info['tweets']
    yt = info['youtube']
    date = info['date']

    print(article)

    videos = "https://www.youtube.com/embed/VIDEO_ID?playlist="
    for title, id in yt:
        videos = videos + ',' + id

    return flask.render_template('mainPage.html', article = article, tweets = tweets, videos = videos, date = date)

#
# @app.errorhandler(405)
# def not_found(error):
#     info = get_today_info()
#
#     article = info['article']
#     tweets = info['tweets']
#     yt = info['youtube']
#     disp_date = info['date']
#
#     videos = "https://www.youtube.com/embed/VIDEO_ID?playlist="
#     for title, id in yt:
#         videos = videos + ',' + id
#
#     return flask.render_template('mainPage.html', article = article, tweets = tweets,
#                                  videos = videos, date = disp_date), 405
#


def search_results(date):
    query = "SELECT 1 FROM Dates WHERE Date = ('{0}')".format(date)
    cursor.execute(query)
    in_db = cursor.fetchall()
    print(in_db)

    if in_db:
        query = "SELECT a.title, a.url FROM Articles a WHERE a.date = '{0}'".format(date)
        cursor.execute(query)
        article = cursor.fetchall()
        print(article)

        query = "SELECT v.title, v.id FROM Videos v WHERE v.date = '{0}'".format(date)
        cursor.execute(query)
        videos = cursor.fetchall()

        query2 = "SELECT t.tweet_url, t.tweet, t.twit_user FROM Tweets t WHERE t.date = '{0}'".format(date)
        cursor.execute(query2)
        tweets = cursor.fetchall()

        article = list(article[0])
        top_videos = list(videos)
        top_tweets = list(tweets)

        return {'article': article, 'tweets': top_tweets, 'youtube': top_videos, 'date': date}

    else:
        return get_today_info()


def get_today_info():

    today = dt.date.today()
    query = "SELECT 1 FROM Dates WHERE Date = ('{0}')".format(today)
    cursor.execute(query)
    in_db = cursor.fetchall()

    if not in_db:
        top_stories = search_NYT.search_NYT()

        top_story = top_stories['results'][0]

        search_string = ("--q='{0}' --max-results=5").format(top_story['title'])

        parser = argparse.ArgumentParser()
        parser.add_argument('--q', help='Search term', default='Google')
        parser.add_argument('--max-results', help='Max results', default=25)

        args = parser.parse_args(shlex.split(search_string))

        stops = set(stopwords.words('english'))
        keywords = top_story['title']
        exclude = set(string.punctuation)
        keywords = ''.join(ch for ch in keywords if ch not in exclude)
        keywords = keywords.split(' ')
        keywords = [w for w in keywords if not w in stops]

        top_tweets = search_twitter.search_twitter(keywords)
        top_videos = search_youtube.youtube_search(args)

        article = [top_story['title'], top_story['url']]

        query = "INSERT INTO DATES (Date) VALUES ('{0}')".format(today)
        cursor.execute(query)
        conn.commit()

        for tweet in top_tweets:
            query = "INSERT INTO Tweets (date, tweet, tweet_url, twit_user) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (today, tweet[1], tweet[0], tweet[2]))
            conn.commit()


        query = "INSERT INTO Articles (date, title, url) VALUES (%s, %s, %s)"
        cursor.execute(query, (today, article[0], article[1]))
        conn.commit()

        for video in top_videos:
            query = "INSERT INTO Videos (date, title, id) VALUES (%s, %s, %s)"
            cursor.execute(query, (today, video[0], video[1]))
            conn.commit()


    else:
        query = "SELECT a.title, a.url FROM Articles a WHERE a.date = '{0}'".format(today)
        cursor.execute(query)
        article = cursor.fetchall()

        query = "SELECT v.title, v.id FROM Videos v WHERE v.date = '{0}'".format(today)
        cursor.execute(query)
        videos = cursor.fetchall()

        query2 = "SELECT t.tweet_url, t.tweet, t.twit_user FROM Tweets t WHERE t.date = '{0}'".format(today)
        cursor.execute(query2)
        tweets = cursor.fetchall()

        article = list(article[0])
        top_videos = list(videos)
        top_tweets = list(tweets)


    return {'article': article, 'tweets': top_tweets, 'youtube': top_videos, 'date': today}

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8090, debug=True)


