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
    dbsession = model.connect()
    # user_list = dbsession.query(model.User, model.Rating).join(model.User.ratings).all()
    # user_list = dbsession.query(model.Rating.user_id, func.count(model.Rating.rating)).join(model.User).group_by(model.Rating.user_id).all()
    
    user_list = dbsession.query(model.Rating.user_id, func.count(model.Rating.rating), model.User.age).join(model.User).group_by(model.Rating.user_id).all()


        # rated_movies = dbsession.query(model.Movie, model.Rating).join(model.Movie.ratings).filter_by(user_id=user_id).all()
    return render_template('user_list.html', user_list=user_list)

@app.route("/login")
def login():
    return render_template('login.html')



@app.route("/signup")
def sign_up():
    return render_template('sign_up.html')



@app.route("/adduser",methods = ["POST"])
def add_user():
    print "This is add user function"

    # email_in_db = dbsession.query(model.User).filter_by(email = email)
    # if email in database:
    #     #go to welcome page
    # else:
    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    # print email, password, age, zipcode

    user = model.User(email = email, password = password, age = age, zipcode = zipcode)
    dbsession = model.connect()
    dbsession.add(user)
    dbsession.commit()
    user_id = dbsession.query(model.User).filter_by(email = email).one()
    user_id = user_id.user_id
 #   print "this is user id 1", user_id
    websession['user'] = {'email': email, 'user_id': user_id}
    return redirect ("/welcome")

@app.route("/loguser", methods = ["POST"])
def log_user_in():
  #  print "this is the log in function"
    email = request.form.get("email")
    dbsession = model.connect()
    email_in_db = dbsession.query(model.User).filter_by(email = email).all()


    if email_in_db == []:
        return redirect("/signup")
    else:
        user_id = dbsession.query(model.User).filter_by(email = email).one()
        user_id = user_id.user_id
        websession['user'] = {'email': email, 'user_id': user_id}
        return redirect("/welcome")

@app.route("/user")
def display_a_users_list_of_ratings():
    dbsession = model.connect()
    user_id = request.args.get('id')
    rated_movies = dbsession.query(model.Movie, model.Rating).join(model.Movie.ratings).filter_by(user_id=user_id).all()
    return render_template('welcome.html', rated_movies = rated_movies, name = user_id)


@app.route("/welcome")
def welcome():
    dbsession = model.connect()
    user_id = websession['user']['user_id']   
    # rated_movies = dbsession.query(model.Rating).filter_by(user_id = websession['user']['user_id']).all()

    rated_movies = dbsession.query(model.Movie, model.Rating).join(model.Movie.ratings).filter_by(user_id=user_id).all()
    # print dir(rated_movies)
    # for rated_movie in rated_movies:
    #     print dir(rated_movie)
    
    return render_template('welcome.html', rated_movies = rated_movies, name = user_id)

@app.route("/movie")
def movie_page():
    dbsession = model.connect()
    movie_id = request.args.get('movie_id')
    movie = dbsession.query(model.Movie).filter_by(movie_id = movie_id).first()
    movie_title = movie.title
    ratings = dbsession.query(model.Rating).filter_by(movie_id = movie_id).all()
    return render_template('moviepage.html',movie_id = movie_id, movie_title = movie_title, ratings = ratings)

@app.route("/rate")
def rate_movie():
    if 'user' in websession:
        dbsession = model.connect()
        movie_id = request.args.get('movie_id')
        websession['movie_id'] = movie_id
        movie = dbsession.query(model.Movie).filter_by(movie_id = movie_id).first()
        movie_title = movie.title
        return render_template('rateform.html', movie_title = movie_title)
    else:
        return redirect("/signup")

@app.route("/submitrating", methods = ["POST"])
def submit_rating():
   # print "you got here"
    rating = request.form.get("rating")
    user_id = websession['user']['user_id']
    movie_id = websession['movie_id']
    

    dbsession = model.connect()
    results = dbsession.query(model.Rating).filter_by(movie_id = movie_id).filter_by(user_id = user_id).all()

    if  results == []:
        new_rating = model.Rating(rating = rating, user_id = user_id, movie_id = movie_id)
        dbsession.add(new_rating)
    else: 
        results[0].rating = rating
        dbsession.add(results[0])

    
    dbsession.commit()
 #    user_id = dbsession.query(model.User).filter_by(email = email).one()
 #    user_id = user_id.user_id
 # #   print "this is user id 1", user_id
 #    websession['user'] = {'email': email, 'user_id': user_id}
    return redirect('/movie?movie_id='+movie_id)

if __name__ == "__main__":
    app.run(debug = True)