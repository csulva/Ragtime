from sqlalchemy.exc import IntegrityError
from fake import Faker
from app import db
from app.models import User, Composition

from random import randint
import string

def users(count=20):
    """Creates fake users to use and manipulate in development

    Args:
        count (int, optional): The count/number you want to create. Defaults to 20.
    """
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
            username=fake.user_name(),
            password='password',
            confirmed=True,
            name=fake.name(),
            location=fake.city(),
            bio=fake.text(),
            last_seen=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
                db.session.rollback()

def compositions(count=100):
    """Creates fake compositions to use and manipulate in development

    Args:
        count (int, optional): The count/number you want to create. Defaults to 100.
    """
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        c = Composition(release_type=randint(0,2),
                        title=string.capwords(fake.bs()),
                        description=fake.text(),
                        timestamp=fake.past_date(),
                        artist=u)
        db.session.add(c)
    db.session.commit()
    for c in Composition.query.all():
        c.generate_slug()