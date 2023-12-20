from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = '2306'  # Přidejte tuto řádku s tajným klíčem
db = SQLAlchemy(app)

class UFORecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    video_url = db.Column(db.String(100), nullable=False)

class VideoForm(FlaskForm):
    title = StringField('Title')
    description = StringField('Description')
    category = StringField('Category')
    video = FileField('Video')
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = VideoForm()

    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        category = form.category.data
        video = form.video.data

        video_filename = f'random_ufo_video-{os.getpid()}-let_the_truth_be_known.mp4'
        video.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))

        video_url = f'/static/uploads/{video_filename}'

        new_record = UFORecord(title=title, description=description, category=category, video_url=video_url)

        db.session.add(new_record)
        db.session.commit()

        return redirect(url_for('index'))

    # Získání unikátních kategorií pro filtrování
    categories = set(record.category for record in UFORecord.query.all())

    # Filtrování podle kategorie
    category_filter = request.args.get('category', '')
    if category_filter:
        records = UFORecord.query.filter_by(category=category_filter).all()
    else:
        records = UFORecord.query.all()

    return render_template('index.html', records=records, form=form, categories=categories)

@app.route('/uploads/<filename>')
def download_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Zajištění, že adresář pro nahrávky existuje
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    app.run(debug=True)
