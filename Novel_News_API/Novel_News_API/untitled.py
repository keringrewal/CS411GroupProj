from flask import Flask
from flask import render_template
from flask import request
from eventregistry import *
import key_store

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    return render_template('mainPage.html')


@app.route("/search/", methods=["POST"])
def search():
    if request.method == 'POST':
        key = key_store.get_yt_key()
        er = EventRegistry(key)

        print("hello")

        # search by title
        search_term = request.form.get('search')

        # input string from search bar output into George Clooney
        results = []

        q = QueryArticlesIter(conceptUri=er.getConceptUri(search_term))
        for art in q.execQuery(er, sortBy="date"):
            results.append(art)
            if len(results) == 10:
                break

        print(results)
        return render_template('mainResults.html', videos=results)



if __name__ == '__main__':
    app.run()
