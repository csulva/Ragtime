from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return """<h2>Hello Web World!</h2>
    <p><a href="http://127.0.0.1:5000/songs">Song List</a></p>
    <p><a href="http://127.0.0.1:5000/about">About Me</a></p>
    """

@app.route('/about')
def about():
    return '<strong>Hello, my name is Chris, and I enjoy web development and music.</strong>'

@app.route('/songs')
def songs():
    return """<h2>A list of my favorite songs</h2>
    <li><em>You're the Voice</em> by <strong>John Farnham</strong></li>
    <li><em>Tubular Bells</em> by <strong>Mike Oldfield</strong></li>
    <li><em>Black Market</em> by <strong>Weather Report</strong></li>
    <li><em>A Whiter Shade of Pale</em> by <strong>Procol Harum</strong></li>
    """