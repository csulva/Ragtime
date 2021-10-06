from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route('/')
def index():
    return f""" {render_template('index.html')}
    <p><a href="http://127.0.0.1:5000/songs">Song List</a></p>
    <p><a href="http://127.0.0.1:5000/about">About Me</a></p>
    """

@app.route('/about')
def about():
    return '<strong>Hello, my name is Chris, and I enjoy web development and music.</strong>'

@app.route('/songs')
def songs():
    songs = {"You're the Voice": "John Farnham", "Tubular Bells": "Mike Oldfield", "Black Market": "Weather Report", "A Whiter Shade of Pale": "Procol Harum"}
    return render_template('songs.html', favorite_songs=songs)

@app.route('/user/<username>')
def user(username):
    return render_template('user.html', username=username)

@app.route('/number/<number>')
def square(number):
    return f'Your number squared is: {int(number) * int(number)}'

@app.route('/derived')
def derived():
    return render_template('derived.html')

@app.errorhandler(403)
def forbidden(e):
    error_title = 'Forbidden'
    error_msg = 'You shouldn\t be here.'
    return render_template('error.html', error_title=error_title, error_msg=error_msg), 403

@app.errorhandler(404)
def page_not_found(e):
    error_title = 'Not Found'
    error_msg = 'That page doesn\'t exist.'
    return render_template('error.html', error_title=error_title, error_msg=error_msg), 404

@app.errorhandler(500)
def internal_server_error(e):
    error_title = "Internal Server Error"
    error_msg = "Sorry, we seem to be experiencing some technical difficulties"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 500