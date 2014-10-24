import model
import csv
from datetime import datetime

def load_users(session, filename): 
    # use u.user
    with open(filename, 'rb') as csvfile:
        
        lines = csv.reader(csvfile, delimiter = '|')
        
        for line in lines:
            user = model.User() 
            user.user_id = line[0].strip()
            user.age = line[1].strip()
            user.zipcode = line[4].strip()

            session.add(user)


    session.commit()



def load_movies(session, filename):
    # use u.item
    with open(filename, 'rb') as csvfile:
        
        lines = csv.reader(csvfile, delimiter = '|')
        
        for line in lines:
            movie = model.Movie()
            movie.movie_id = line[0].strip()
            movie.title = line[1].strip()
            movie.title = movie.title[:-6].strip()
            movie.title = movie.title.decode("latin-1")
            movie.release_date = datetime.strptime(line[2].strip(),"%d-%b-%Y")
            movie.imdb = line[4].strip()
            session.add(movie)


    session.commit()
    


def load_ratings(session, filename): 
    # use u.data
    # when running for real, remove echo = true
    with open(filename, 'rb') as temp_file:

        for line in temp_file:
            line = line.split()
            rating = model.Rating() 
            rating.movie_id = line[0].strip()
            rating.user_id = line[1].strip()
            rating.rating = line[2].strip()
            session.add(rating)

    session.commit()

def main(session):
    # when running for real, remove echo = true
    # You'll call each of the load_* functions with the session as an argument
    # load_movies(session, 'seed_data/u.item')
    # load_ratings(session, 'seed_data/u.data')
    # load_users(session,'seed_data/u.user')

if __name__ == "__main__":
    s= model.connect()
    main(s)