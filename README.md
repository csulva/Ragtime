# Ragtime

[Ragtime](https://flask-webdev-cs.herokuapp.com/) is a social media app created with Flask for users to post new "music" as a composition. Register an account and start sharing your compositions on the blog or follow other users to see their work!

[Join Ragtime](https://flask-webdev-cs.herokuapp.com/) by creating an account and be part of the community by sharing your compositions!

## Installation

It is  recommended to install requirements in a virtual environment (venv).
```bash
python3 -m venv venv
. venv/bin/activate
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Ragtime requirements.

```bash
pip install -r requirements.txt
```

## Us
To start using the app, open a ```flask shell``` session:
```python
export FLASK_APP=ragtime
flask shell
```
```python
>>> db.create_all()
>>> Role.insert_roles()
>>> User.add_self_follows()
>>> exit()
```

Add yourself to the database in a flask shell session:
```python
>>> u = User(username='yourusername', email='youremail', password='yourpassword', confirmed=True)
>>> db.session.add(u)
>>> db.session.commit()
>>> exit()
```
Note: you can also register in your own app!
First, run the program:

```python
flask run
```
Then, navigate to your *register* template: __localhost:5000/auth/register__ and register your email address. Confirm yourself as a user by opening the link sent to you in an email (see [Send Emails](#send-emails)).

Now you can create your own compositions!

## Fake Data
Fake data with your app in development to see new users and their compositions on your website and in your database.

To do so, ```pip install requirements/dev.txt``` in your virtual environment.

Next, open a Flask shell session:
```python
flask shell
```
```python
# use however many users or compositions you want to generate
>>> from app import fake
>>> fake.users(count=20)
>>> fake.compositions(count=200)
```

The data will automatially be committed to your database in development. Be sure not transfer this data to production so that the information you show to the world on your app is real 🙂

## Migrations
Whenever a database migration needs to be made. Run the following commands
```bash
flask db migrate
```
This will generate a new migration script. Then run:
```bash
flask db upgrade
```
To apply the migration.

For a full migration command reference, run ```flask db --help```.

## Send Emails

For email sending to work properly with this app, including confirmation emails, you must have an email that accepts SMTP authentication. Then, you must then set the environment variables MAIL_USERNAME, MAIL_PASSWORD, and RAGTIME_ADMIN that are found in ```config.py```

You can configure those variables in a bash script:

```python
export MAIL_USERNAME=<your_username>
export MAIL_PASSWORD=<your_password>
export RAGTIME_ADMIN=<yourusername@example.com>
```

## Environment Variables

It might be useful to save your environment variables in your project, so you do not need to set them up each time you run the app. To do so, run the following:

```python
touch .env
```
Be sure to create it in your root directory and not to push it to GitHub or any public space where it can be viewed. Then you can add your environment variables to the file. For example:
```python
# .env
FLASK_APP=ragtime.py
```

For deployment to Heroku, you must add the environment variables to your app. [You can do this in your Heroku dashboard](https://devcenter.heroku.com/articles/config-vars) when the app is created. Or apply them in your terminal:
```python
heroku config:set FLASK_APP=ragtime.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## References
[CodingNomads Python Web Development](https://codingnomads.co/career-track/professional-python-web-development-course)
