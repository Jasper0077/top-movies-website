from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# API Endpoint and API Key
API_KEY = "f111d14b434f5470d65b22f3d47611dd"
SEARCH_ENDPOINT = "https://api.themoviedb.org/3/search/movie"


Bootstrap(app)
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(400), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(400), nullable=False)
    img_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'


class UpdateForm(FlaskForm):
    rating = FloatField(label='Rating out of 10.0, e.g 7.8', validators=[DataRequired()])
    review = StringField(label='Your review', validators=[DataRequired()])
    submit = SubmitField(label="Update")


class AddForm(FlaskForm):
    title = StringField(label='Movie title', validators=[DataRequired()])
    submit = SubmitField(label="Search")


# db.create_all()

# After adding the new_movie the code needs to be commented out/deleted.
# So you are not trying to add the same movie twice.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating.desc()).all()
    i = 1
    for movie in movies:
        movie.ranking = i
        i += 1
    return render_template("index.html", movies=movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    id = request.args.get("id")
    form = UpdateForm()
    movie_id = id
    movie_to_update = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form)


@app.route("/delete/<id>")
def delete(id):
    movie_id = id
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        return redirect(url_for('select', title=form.title.data))
    return render_template("add.html", form=form)


@app.route("/select/<title>")
def select(title):
    parameters = {
        "api_key": API_KEY,
        "query": title
    }
    response = requests.get(SEARCH_ENDPOINT, params=parameters)
    print(response)
    movies_list = response.json()
    print(movies_list)
    return render_template("select.html", movies=movies_list["results"])


@app.route("/find")
def add_movie():
    id = request.args.get("id")
    get_movie_endpoint = f"https://api.themoviedb.org/3/movie/{id}"
    parameters = {
        "api_key": API_KEY
    }
    response = requests.get(get_movie_endpoint, params=parameters)
    movie_details = response.json()
    new_movie = Movie(
        title=movie_details["original_title"],
        year=movie_details["release_date"].split("-")[0],
        description=movie_details["overview"],
        rating=0,
        ranking=0,
        review="-",
        img_url=f"https://image.tmdb.org/t/p/w500/{movie_details['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
