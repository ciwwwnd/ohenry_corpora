from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from nlp import searching

app = Flask(__name__, static_folder='templates/templates/static')
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        search = searching(query)
        if search == []:
            return render_template("nothing.html", query=query)
        return render_template("results.html", search=search, query=query)


@app.route('/faq')
def faq():
    return render_template("faq.html")


@app.route('/tags')
def tags():
    return render_template("tags.html")


if __name__ == '__main__':
    app.run()
