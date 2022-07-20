from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'tbl_venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(500), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))
    venue_shows = db.relationship('Show',backref='tbl_venues', lazy=True)

    # INSERT into tbl_venues(name,city,state,address,phone,genres) Values('Abuja Stadium','FCT','Abuja','No. 1 Abuja Staduim','+2348059246152','jazz,classic')



    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'tbl_artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_venues = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500))
    artist_shows = db.relationship('Show',backref='tbl_artists', lazy=True)

    # INSERT into tbl_artists(name,city,state,phone,genres) Values('Jeremiah','FCT','Abuja','+2348059246152','jazz,classic')



    # TODO: implement any missing fields, as a database migration using Flask-Migrate
# db.create_all()
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__= 'tbl_shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('tbl_artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('tbl_venues.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    # INSERT into tbl_shows(artist_id,venue_id,start_time) Values(1,2,'2022-06-04')