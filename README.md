# Ragtime

[Ragtime](https://flask-webdev-cs.herokuapp.com/) is a social app created with Flask for users to post new "music" as a composition. Register an account and start sharing your compositions on the blog or follow other users to see their work!

[Join Ragtime](https://flask-webdev-cs.herokuapp.com/) by creating an account and be part of the community by sharing your compositions!

## Installation

It is  recommended to install requirements in a virtual environment (venv).
```bash
python3 -m venv venv
. venv/bin/activate
```
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Ragtime requirements.

For Production:
```bash
pip install -r requirements.txt
```
For Development (includes Faker):
See [Development Setup](https://github.com/csulva/Ragtime/blob/main/Dev-Setup-with-Faker.md)

## Usage

```python
flask run
```

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

For a full migration command reference, run flask db --help.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## References
[CodingNomads Python Web Development](https://codingnomads.co/career-track/professional-python-web-development-course)
