from flask import Flask, render_template, request
from scraper import get_response

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search_term = request.form.get("term")
        language_code = request.form.get("language")
    return render_template('index.html')

if __name__ == "__main__":
    app.run()