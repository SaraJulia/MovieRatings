from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session
import correlation

# ENGINE = None
# Session = None

ENGINE = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind = ENGINE,
                                        autocommit = False,
                                        autoflush = False))


Base = declarative_base()
Base.query = session.query_property()

### Class declarations go here

class User(Base):
    __tablename__ = 'users'

    user_id =   Column(Integer, primary_key = True)
    email =     Column(String(64), nullable = True)
    password =  Column(String(64), nullable = True)
    age =       Column(Integer, nullable = True)
    zipcode =   Column(String(15), nullable = True)

    def similarity(self,user2):
        u_ratings = {}
        paired_ratings = []
        for r in self.ratings:
            u_ratings[r.movie_id] = r

        for r in user2.ratings:
            u_r = u_ratings.get(r.movie_id)
            if u_r:
                paired_ratings.append( (u_r.rating, r.rating) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0

    def predict_rating(self, movie):

        other_ratings = movie.ratings

        similarities = []
        # creates a list of tuples (similarity, rating object)
        for rating in other_ratings:
            #similarities.append((self.similarity(rating.user),rating)) # old code
            similarities.append((movie.similarity(rating.movie),rating)) ## bonus round

        similarities.sort(reverse = True)

        pos_similarities = []
        for similarity in similarities:
            if similarity[0] > 0:
                pos_similarities.append(similarity)

        if not pos_similarities:
            return "There were no positives"

        numerator = 0
        for similarity, r in pos_similarities:
            this_mean = similarity * r.rating
            numerator += this_mean

        denominator = 0
        for similarity in pos_similarities:
            denominator += similarity[0]

        return numerator/denominator

# THIS ALSO WORKS
        # other_ratings = movie.ratings
        # other_users = []

        # for r in other_ratings:
        #     other_users.append(r.user)

        # user_correlations = []
        # for other_user in other_users: 
        #     similarity = self.similarity(other_user)
        #     pair = (similarity, other_user.user_id)
        #     user_correlations.append(pair)

        # user_correlations.sort(reverse = True)

        # best_match = user_correlations[0]
        # best_match_rating = session.query(Rating).filter_by(user_id = best_match[1], movie_id = movie.movie_id).one()

        # prediction = best_match[0] * float(best_match_rating.rating)

        # return prediction

class Movie(Base):
    __tablename__ = 'movies'

    movie_id =      Column(Integer, primary_key = True)
    title =         Column(String(64), nullable = True)
    release_date =  Column(Date, nullable = True)
    imdb =          Column(String(15), nullable = True)

    def similarity(self,movie2):
        m_ratings = {}
        paired_ratings = []
        for r in self.ratings:
            m_ratings[r.user_id] = r #dictionary for this movie where the user id 
            #is the key and that user's rating of this movie is the value

        #for every rating in the other movie's list of ratings objects
        for r in movie2.ratings:
            #m_r is 
            m_r = m_ratings.get(r.user_id)
            if m_r:
                #print (m_r.rating, r.rating)
                paired_ratings.append( (m_r.rating, r.rating) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0


class Rating(Base):
    __tablename__ = 'ratings'

    rating_id =     Column(Integer, primary_key = True)
    movie_id =      Column(Integer, ForeignKey('movies.movie_id'), nullable = True)
    user_id =       Column(Integer, ForeignKey('users.user_id'), nullable = True)
    rating =        Column(Integer,nullable = True)

    user = relationship("User", backref = backref("ratings", order_by=rating_id)) 
    movie = relationship("Movie", backref = backref("ratings", order_by =rating_id))

### End class declarations

def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("sqlite:///ratings.db", echo=False)
    Session = sessionmaker(bind = ENGINE)

    return Session()

def main():
    """In case we need this for something"""

    # m = session.query(Movie).get(300)
    # u = session.query(User).get(1)
    # print u.predict_rating(m)
   # #  global Base
   #  global ENGINE

   #  ENGINE = create_engine("sqlite:///ratings.db", echo=False)
   # # Session = sessionmaker(bind = ENGINE)

   #  Base.metadata.create_all(ENGINE)


if __name__ == "__main__":
    main()
