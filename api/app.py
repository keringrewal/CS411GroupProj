import os
import flask

from eventregistry import *

app = flask.Flask(__name__, template_folder='api/templates')


@app.route('/mainPage', methods=['GET'])
def main_page():
    return flask.render_template('mainPage.html')


@app.route('/results', methods=['POST'])
def search_youtube():
    er = EventRegistry(apiKey="KEY GOES HERE")

    # search by title
    search_term = flask.request.form['text']
    # input string from search bar output into George Clooney
    q = QueryArticlesIter(conceptUri=er.getConceptUri(search_term))
    results = []
    for art in q.execQuery(er, sortBy="date"):
        results.append(art)
        if len(results) == 10:
            break

    return flask.render_template('results.html', videos = results)

if __name__ == '__main__':
    app.run('localhost', debug=True)