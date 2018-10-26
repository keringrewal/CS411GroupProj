from flask import Flask
from flask import render_template
from flask import request
from eventregistry import *
import key_store

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        key = key_store.get_yt_key()
        er = EventRegistry(key)

        # search by title
        search_term = request.form['search']
        # input string from search bar output into George Clooney
        q = QueryArticlesIter(conceptUri=er.getConceptUri(search_term))
        results = []
        for art in q.execQuery(er, sortBy="date"):
            results.append(art)
            if len(results) == 10:
                break

        return render_template('mainResults.html', videos=results)
    else:
        return render_template('mainPage.html')


if __name__ == '__main__':
    app.run()
