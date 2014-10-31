from flask import Flask, render_template, redirect, request, session as websession
from sqlalchemy import func
import model

app = Flask(__name__)
app.secret_key = 'MovieRatings4Eva'

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/userlist") 
def show_user_list():

    user_list = model.session.query(model.Rating.user_id, func.count(model.Rating.rating), model.User.age).join(model.User).group_by(model.Rating.user_id).all()

    return render_template('user_list.html', user_list=user_list)

@app.route("/login") 
def login():
    return render_template('login.html')



@app.route("/signup") 
def sign_up():
    return render_template('sign_up.html')



@app.route("/adduser",methods = ["POST"]) 
def add_user():
    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")    

    query_result = model.session.query(model.User).filter_by(email = email).first()

    if query_result:
        return redirect("/login")
    else:
        user = model.User(email = email, password = password, age = age, zipcode = zipcode)
        model.session.add(user)
        model.session.commit()
        websession['user_id'] = user.user_id
        return redirect ("/welcome")
        

@app.route("/loguser", methods = ["POST"])     
def log_user_in():
    email = request.form.get("email")
    password = request.form.get("password")


    user = model.session.query(model.User).filter_by(email = email, password=password).first()


    if user:
        websession['user_id'] = user.user_id
        return redirect("/welcome")
    else:
        return redirect("/signup")


@app.route("/user") 
def display_a_users_list_of_ratings():
    user_id = request.args.get('id')
    rated_movies = model.session.query(model.Movie, model.Rating).join(model.Movie.ratings).filter_by(user_id=user_id).all()
    return render_template('welcome.html', rated_movies = rated_movies, name = user_id)


@app.route("/welcome") 
def welcome():
 
    user_id = websession['user_id']   

    rated_movies = model.session.query(model.Movie, model.Rating).join(model.Movie.ratings).filter_by(user_id=user_id).all()

    return render_template('welcome.html', rated_movies = rated_movies, name = user_id)



@app.route("/movie")
def movie_page():
    movie_id = int(request.args.get('movie_id'))
    movie = model.session.query(model.Movie).filter_by(movie_id = movie_id).first()
    
    #call prediction method for you, for this movie
    your_rating = None
    prediction = None
    effective_rating = None

    if 'user_id' in websession:
        user_id = websession['user_id']
        user = model.session.query(model.User).get(user_id)
        for rating in user.ratings:
            if rating.movie_id == movie_id:
                your_rating = rating.rating
                effective_rating = your_rating
            else:
                prediction = user.predict_rating(movie)
                effective_rating = prediction

    the_eye = model.session.query(model.User).filter_by(email="theeye@ofjudgment.com").one()
    eye_rating = model.session.query(model.Rating).filter_by(user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if not eye_rating:
        eye_rating = the_eye.predict_rating(movie)
    else:
        eye_rating = eye_rating.rating

    difference = abs(eye_rating - effective_rating)

    messages = [ "I suppose you don't have such bad taste after all.",
             "I regret every decision that I've ever made that has brought me to listen to your opinion.",
             "Words fail me, as your taste in movies has clearly failed you.",
             "That movie is great. For a clown to watch. Idiot."]

    beratement = messages[int(difference)]
                
    return render_template('moviepage.html', movie = movie, prediction = prediction, your_rating = your_rating, beratement = beratement)

@app.route("/rate")
def rate_movie():
    if 'user_id' in websession:
        movie_id = request.args.get('movie_id')
        movie = model.session.query(model.Movie).filter_by(movie_id = movie_id).first()

        return render_template('rateform.html', movie=movie)
    else:
        return redirect("/signup")

@app.route("/submitrating", methods = ["POST"])
def submit_rating():
    rating = request.form.get("rating")
    user_id = websession['user_id']
    movie_id = request.form.get("movie_id")
    
    query_results = model.session.query(model.Rating).filter_by(movie_id = movie_id).filter_by(user_id = user_id).all()

    if query_results == []:
        new_rating = model.Rating(rating = rating, user_id = user_id, movie_id = movie_id)
        model.session.add(new_rating)
    else: 
        query_results[0].rating = rating
        model.session.add(query_results[0])

    
    model.session.commit()

    return redirect('/movie?movie_id='+movie_id)

if __name__ == "__main__":
    app.run(debug = True)