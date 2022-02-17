from flask import Flask, request,Response, flash, url_for, redirect, render_template
from flask_restful import Api, Resource, abort, reqparse, marshal_with, fields
import flask
from flask_sqlalchemy import SQLAlchemy
import re
from sqlalchemy import text

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.sqlite3'
app.config['SECRET_KEY'] = "random string"
db = SQLAlchemy(app)

class movies(db.Model):
    id = db.Column('movie_id', db.Integer, primary_key = True)
    tittle = db.Column(db.String(100), )
    duration = db.Column(db.Integer)
    director = db.Column(db.String(200))
    genre = db.Column(db.String(10))
    rating = db.Column(db.Float)

    def __init__(self, tittle,duration, director, genre, rating):
       self.tittle = tittle
       self.duration = duration
       self.director=director
       self.genre = genre
       self.rating = rating

db.create_all()

movies_model_field = {
    'id': fields.Integer,
    'tittle': fields.String,
    'duration': fields.Integer,
    'director': fields.String,
    'genre': fields.String,
    'rating': fields.Float
}

movie_req = reqparse.RequestParser()
movie_req.add_argument('tittle', type=str, required=True)
movie_req.add_argument('duration', type=int, required=True)
movie_req.add_argument('director', type=str, required=True)
movie_req.add_argument('genre', type=str, required=True)
movie_req.add_argument('rating', type=float, required=True)

class MovieList(Resource):
    @marshal_with(movies_model_field)
    def get(self):

        result = movies.query.all()
        return result
        
    @marshal_with(movies_model_field)

    def post(self):
        new_movie_data = movie_req.parse_args()

        new_movie = movies(
            tittle = new_movie_data['tittle'],
            duration = new_movie_data['duration'],
            director = new_movie_data['director'],
            genre = new_movie_data['genre'],
            rating = new_movie_data['rating'])

        db.session.add(new_movie)
        db.session.commit()

        return new_movie, 201

api.add_resource(MovieList, '/movielist/')   

class Movies(Resource):
   @marshal_with(movies_model_field)
   def get(self, id):
        movie = movies.query.get(id)
        return movie

   @marshal_with(movies_model_field)
   def put(self, id):
        data = movie_req.parse_args()
        movie = movies.query.get(id)

        movie.tittle = data['tittle']
        movie.duration = data['duration']
        movie.director = data['director']
        movie.genre=data['genre']
        movie.rating=data['rating']
        db.session.commit()
        return movie
api.add_resource(Movies,'/movielist/<int:id>')


@app.route('/health', methods=['Get'])  
def health():
    status_code = flask.Response(status=200)
    return status_code
   

@app.route('/movies')
def show_all():
    return render_template('movie_template.html', movies = movies.query.all() ) 

@app.route('/movies/new', methods = ['GET', 'POST'])
def new():

 try:
    if request.method == 'POST':
        if not request.form['tittle'] or not request.form['duration'] or not request.form['director'] or not request.form['genre'] or not request.form['rating'] :
            flash('Please enter all the fields', 'error')
        elif int(request.form['duration'])<=0 :  
                flash('Please insert a positive value ', 'error')
        elif re.search("^[a-zA-Z0-9]",str(request.form['tittle'])) is None:
            flash('Tittle should begin with a letter or a number ', 'error')

        else:
            movie = movies(request.form['tittle'], request.form['duration'],request.form['director'],
                request.form['genre'] , request.form['rating'] 
                )
            db.session.add(movie)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all'))

    return render_template('new_movies.html')

 except: 

    return render_template('ErrorPage.html')

@app.route('/movies/update/<id>',methods = ['GET','POST'])
def update(id):
    movie = movies.query.get(id)
    if request.method == 'POST':
        if movie:
            db.session.delete(movie)
            db.session.commit() 
            movie = movies(request.form['tittle'], request.form['duration'],request.form['director'],
                request.form['genre'] , request.form['rating'])
            db.session.add(movie)
            db.session.commit()
            return redirect('/movies')
        return f"Movie with id = {id} Does not exist"

    return render_template('update.html', movie = movies.query.get(id) )
 
 
@app.route('/movies/delete/<id>', methods=['GET','POST'])
def delete(id):
    movie = movies.query.get(id)
    if request.method == 'POST':
        if movie:
            db.session.delete(movie)
            db.session.commit()
            return redirect('/movies')
        abort(404)
 
    return render_template('delete.html')


@app.route('/movies/details/<id>')
def details(id):
    return render_template('moviedetails.html', movie = movies.query.get(id) )

@app.route('/showMovies',methods = ['POST', 'GET'])
def showMovies():


 movies = db.engine.execute(text("SELECT * FROM movies where movie_id>= :val1 LIMIT :val2 "), {'val2':int(request.args.get('count')), 'val1':int(request.args.get('start'))})#.execution_options(autocommit=True)
 return render_template("movieList.html",movies = movies)

@app.route('/filterMovies',methods = ['POST', 'GET'])
def filterMovies():

 try:    
    if re.search("^[a-zA-Z]",str(request.form['tittle'])) is None:
        flash('Movie tittle should contain only letters', 'error')
        return render_template("movie_template.html", movies= movies.query.all() )

    else:    
        movies_10 =db.session.query(movies).filter(movies.tittle == request.form['tittle'])
   
    return render_template("movieList.html",movies = movies_10)

 except: 

    return render_template('ErrorPage.html')

@app.route('/')
def redirect_link():
    return redirect(url_for('show_all'))   

if __name__ == '__main__':
   app.run(host='127.0.0.1', port=8080,debug = True)