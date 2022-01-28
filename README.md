# Ragtime

Ragtime is a social app created with Flask for users to post new "music" as a composition. Register an account and start sharing your compositions on the blog or follow other users to see their work!
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Ragtime requirements.
For Production:
```bash
pip install requirements.txt
```
For Development (includes Faker):
```bash
pip install requirements/dev.txt
```

## Usage

```python
import foobar

# returns 'words'
foobar.pluralize('word')

# returns 'geese'
foobar.pluralize('goose')

# returns 'phenomenon'
foobar.singularize('phenomena')
```
## Usage in Development
```python
from fake import Faker
fake = Faker()

# Fake users
u = User(email=fake.email(),
            username=fake.user_name(),
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            bio=fake.text(),
            last_seen=fake.past_date())
        db.session.add(u)
        db.session.commit()
        
# Fake compositions
        c = Composition(release_type=randint(0,2),
                        title=string.capwords(fake.bs()),
                        description=fake.text(),
                        timestamp=fake.past_date(),
                        artist=u)
        db.session.add(c)
        db.session.commit()

# See app/fake.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Migrations
Whenever a database migration needs to be made. Run the following commands
```bash
flask db migrate
```
This will generate a new migration script. Then run
```bash
flask db upgrade
```
To apply the migration.

For a full migration command reference, run flask db --help.

## References
[CodingNomads Python Web Development](https://codingnomads.co/career-track/professional-python-web-development-course)
