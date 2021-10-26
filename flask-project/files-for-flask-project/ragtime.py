from app import create_app, db
from app.models import Role, User
import os
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User)


# @app.route('/zodiac', methods=["GET", "POST"])
# def zodiac():
#     form = DateForm()
#     zodiac_signs = ['Aquarius', 'Pisces', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn']
#     if form.validate_on_submit():
#         session['date'] = form.date.data
#         flash(f'Your zodiac sign is... ')
#         return redirect(url_for('zodiac'))
#     return render_template('zodiac.html', form=form, date=session.get('date'), zodiac_signs=zodiac_signs)


app.run()