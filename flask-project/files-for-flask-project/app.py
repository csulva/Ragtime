from flask import Flask
from flask import render_template

app = Flask(__name__)

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