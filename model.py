from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

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

class Movie(Base):
    __tablename__ = 'movies'

    movie_id =      Column(Integer, primary_key = True)
    title =         Column(String(64), nullable = True)
    release_date =  Column(Date, nullable = True)
    imdb =          Column(String(15), nullable = True)

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
   #  global Base
   #  global ENGINE

   #  ENGINE = create_engine("sqlite:///ratings.db", echo=False)
   # # Session = sessionmaker(bind = ENGINE)

   #  Base.metadata.create_all(ENGINE)


if __name__ == "__main__":
    main()
