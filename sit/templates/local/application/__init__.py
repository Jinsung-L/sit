from flask import Flask, render_template, url_for


app = application = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
