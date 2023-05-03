from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
db =SQLAlchemy(app)


MOVIE_ENDPOIND = 'https://api.themoviedb.org/3/search/movie'
API_KEY = 'dae56c91508f072508941052d0890d06'

with app.app_context():
    class Movie(db.Model):            
        id = db.Column(db.Integer, primary_key = True)
        title = db.Column(db.String(250), unique = True, nullable = False)
        year = db.Column(db.Integer, nullable = False)
        description = db.Column(db.String(250), nullable = False)
        rating = db.Column(db.Float, nullable = True)
        ranking = db.Column(db.Float, nullable = True)
        review = db.Column(db.String(250), nullable = True)
        # img_url =db.Column(db.String(250), nullable = False)
    db.create_all()

class AddMovie(FlaskForm):
    movie = StringField(label = 'Movie Title', validators=[DataRequired()])    
    submit = SubmitField(label='Add Movie')


 
@app.route("/")
def home():
    all_movie = Movie.query.order_by(Movie.rating).all()
    for  i in range(len(all_movie)):
        all_movie[i].ranking = len(all_movie) - i
    db.session.commit()
    return render_template("index.html", movies = all_movie)

@app.route('/edit', methods = ["GET", "POST"])
def edit():
    if request.method == "POST":
        movie_id = request.form["id"]
        movie_update = Movie.query.get(movie_id)
        movie_update.rating = request.form["rating"]
        movie_update.review = request.form['review']
        db.session.commit()
        return redirect(url_for('home'))
    movie = request.args.get('id')  
    selected_movie = Movie.query.get(movie)  
    return render_template('edit.html', movie = selected_movie)

@app.route('/delete')
def delete():
    movie_delete = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_delete)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))
    
@app.route('/add', methods = ['POST', 'GET'])
def add():
    add_form = AddMovie()
    if add_form.validate_on_submit():
        list_of_movie = get_data_about_movie(add_form.movie.data)
        return render_template('select.html', list = list_of_movie)
    return render_template('add.html', form = add_form) 

def get_data_about_movie(movie):
    movie_params = {
        'api_key': API_KEY,
        'language' : "en-US",
        'query' : movie
    }
    response = requests.get(url=MOVIE_ENDPOIND, params=movie_params)
    list = []
    data = response.json()
    for page in range(len(data)):
        for result in data['results']:
            list.append((result['original_title'], result['release_date'], result['id']))
    return list

@app.route('/find')
def find_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_url = f'https://api.themoviedb.org/3/movie/{movie_api_id}'
        movie_params = {
            'api_key': API_KEY,
            'language' : "en-US", 
        }
        response = requests.get(url = movie_url, params= movie_params)
        data = response.json()
        new_movie = Movie(
            title = data['original_title'],
            year = data['release_date'].split('-')[0],
            description = data['overview'],
            ranking = data['vote_average']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id = new_movie.id))
    

if __name__ == '__main__':
    app.run(debug=True)
