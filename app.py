#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from optparse import Values
from time import time
from tkinter import INSERT
from xmlrpc.client import Boolean
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
from models import db,Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate=Migrate(app,db)

# create database tables if the database exist
with app.app_context():
  db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# homepage route
@app.route('/')
def index():
  return render_template('pages/home.html')


# list of all venues route
@app.route('/venues')
def venues():
  # select distinct venues from cities/state
  city_state = db.session.query(Venue.city, Venue.state).distinct()
  data = []
  for venue in city_state:
    venue = dict(zip(('city', 'state'), venue))
    venue['venues'] = []
    for venue_data in Venue.query.filter_by(city=venue['city'], state=venue['state']).all():
        # get upcoming shows in the venue
        upcomming_shows = Show.query.filter_by(venue_id=venue_data.id).filter(Show.start_time>datetime.now()).all()
        num_upcoming = len(upcomming_shows) #number of upcoming shows
        venues_data = {
            'id': venue_data.id,
            'name': venue_data.name,
            'num_upcoming_shows': num_upcoming
        }
        venue['venues'].append(venues_data)
    data.append(venue)
  print(data)
  return render_template('pages/venues.html', areas=data);

# search for a specific venue route
@app.route('/venues/search', methods=['POST'])
def search_venues():
  looking_for = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(looking_for))).all()
  
  num_of_venues = len(venues)

  response={}
  response['count'] = num_of_venues
  response['data'] = [venue for venue in venues]
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

# view a particular venue route
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  data = {}
  data['id']= venue.id
  data['name']= venue.name
  data['city']= venue.city
  data['state']= venue.state
  data['genres']= venue.genres.split('|')
  data['phone']= venue.phone
  data['address']= venue.address
  data['image_link']= venue.image_link
  data['facebook_link']= venue.facebook_link
  data['seeking_talent']= venue.looking_for_talent
  data['seeking_description']= venue.seeking_description
  data['website']= venue.website_link
  # get upcoming shows in a venue
  query_upcoming = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time>datetime.now()).all()
  data['upcoming_shows'] = []
  for upcoming in query_upcoming:
    obj = {}
    obj['artist_id'] = upcoming.artist_id
    obj['venue_id'] = upcoming.venue_id
    obj['start_time'] = upcoming.start_time.isoformat()
    obj['artist_name'] = Artist.query.filter_by(id=upcoming.artist_id).first().name
    obj['artist_image_link'] = Artist.query.filter_by(id=upcoming.artist_id).first().image_link
    data['upcoming_shows'].append(obj)
  data['upcoming_shows_count'] = len(data['upcoming_shows'])

  # get past shows in a venue
  query_pastshows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue_id).filter(Show.start_time<datetime.now()).all()
  data['past_shows'] = []
  for pastshow in query_pastshows:
    obj = {}
    obj['artist_id'] = pastshow.artist_id
    obj['venue_id'] = pastshow.venue_id
    obj['start_time'] = pastshow.start_time.isoformat()
    obj['artist_name'] = Artist.query.filter_by(id=pastshow.artist_id).first().name
    obj['artist_image_link'] = Artist.query.filter_by(id=pastshow.artist_id).first().image_link
    data['past_shows'].append(obj)
  data['past_shows_count'] = len(data['past_shows'])
  return render_template('pages/show_venue.html', venue=data)


#  Create a Venue route
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

# create a venue endpoint
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  venue_fields=dict(request.form)
  
  is_looking_for_talent = False
  
  if request.form.get('looking_for_talent') == 'y':
    is_looking_for_talent =  True

  venue_fields['looking_for_talent'] = is_looking_for_talent
  venue_fields['genres'] = '|'.join(request.form.getlist('genres'))
  
  new_venue = Venue(**venue_fields)

  try:
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except():
    db.session.rollback()
    flash('An error occurred. Venue ' + venue_fields.name + ' could not be listed.')
  finally:
    db.session.close()
  print(venue_fields)
  return render_template('pages/home.html')

# delete a venue endpoint
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue deleted successfully'.format(venue_id))
  except():
    db.session.rollback()
    print(sys.exc_info())
    flash('Deletion Failed')
  finally:
    db.session.close()
  return jsonify({
    'success': True
  })
  return None

#  list of all artists route
@app.route('/artists')
def artists():
  data=[]
  artists = Artist.query.order_by('id').all()
  for artist in artists:
      data.append({'id': artist.id, 'name':artist.name})
  return render_template('pages/artists.html', artists=data)

# search for artist endpoint
@app.route('/artists/search', methods=['POST'])
def search_artists():
  looking_for = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%{}%'.format(looking_for))).all()
  
  num_of_artists = len(artists)

  response={}
  response['count'] = num_of_artists
  response['data'] = [artist for artist in artists]
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

# view a particular artist route
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  artist_data = {}
  artist_data['id'] = artist.id
  artist_data['name'] = artist.name
  artist_data['city'] = artist.city
  artist_data['state'] = artist.state
  artist_data['phone'] = artist.phone
  artist_data['genres'] = artist.genres.split('|')
  artist_data['image_link'] = artist.image_link
  artist_data['facebook_link'] = artist.facebook_link
  artist_data['seeking_venue'] = artist.looking_for_venues
  artist_data['seeking_description'] = artist.seeking_description
  artist_data['website'] = artist.website_link
  # get upcoming shows
  query_upcoming = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time>datetime.now()).all()
  artist_data['upcoming_shows'] = []
  for upcoming in query_upcoming:
    obj = {}
    obj['artist_id'] = upcoming.artist_id
    obj['venue_id'] = upcoming.venue_id
    obj['venue_image_link'] = Venue.query.filter_by(id=upcoming.venue_id).first().image_link
    obj['start_time'] = upcoming.start_time.isoformat()
    obj['venue_name'] = Venue.query.filter_by(id=upcoming.venue_id).first().name
    obj['artist_image_link'] = Artist.query.filter_by(id=upcoming.artist_id).first().image_link
    artist_data['upcoming_shows'].append(obj)
  artist_data['upcoming_shows_count'] = len(artist_data['upcoming_shows'])
  print(artist_data)
  # get past shows
  query_pastshows = db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).filter(Show.start_time<datetime.now()).all()
  artist_data['past_shows'] = []
  for pastshow in query_pastshows:
    obj = {}
    obj['artist_id'] = pastshow.artist_id
    obj['venue_id'] = pastshow.venue_id
    obj['venue_image_link'] = Venue.query.filter_by(id=pastshow.venue_id).first().image_link
    obj['start_time'] = pastshow.start_time.isoformat()
    obj['venue_name'] = Venue.query.filter_by(id=pastshow.venue_id).first().name
    obj['artist_image_link'] = Artist.query.filter_by(id=pastshow.artist_id).first().image_link
    artist_data['past_shows'].append(obj)
  artist_data['past_shows_count'] = len(artist_data['past_shows'])
  return render_template('pages/show_artist.html', artist=artist_data)


#  Update an artist route
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_data = {}
  artist_data["id"] = artist.id
  artist_data["name"] = artist.name
  artist_data["genres"] = artist.genres.split('|')
  artist_data["city"] = artist.city
  artist_data["state"] = artist.state
  artist_data["phone"] = artist.phone
  artist_data["website_link"] = artist.website_link
  artist_data["facebook_link"] = artist.website_link
  artist_data["seeking_venue"] = artist.looking_for_venues
  artist_data["seeking_description"] = artist.seeking_description
  artist_data["image_link"] = artist.image_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

#  Update an artist endpoint
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  try:
    is_looking_for_venues = False
    
    if request.form.get('looking_for_venues') == 'y':
      is_looking_for_venues =  True
    
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = '|'.join(request.form.getlist('genres'))
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website_link = request.form.get('website_link')
    artist.looking_for_venues = is_looking_for_venues
    artist.seeking_description =  request.form.get('seeking_description')

    flash('Artist ' + request.form.get('name') + ' was successfully updated!')
    db.session.commit()
  except():
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be updated.')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

# edit an venue route
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_data = {}
  venue_data['id'] = venue.id
  venue_data['name'] = venue.name
  venue_data['genres'] = venue.genres.split('|')
  venue_data['address'] = venue.address
  venue_data['city'] = venue.city
  venue_data['state'] = venue.state
  venue_data['phone'] = venue.phone
  venue_data['website_link'] = venue.website_link
  venue_data['facebook_link'] = venue.facebook_link
  venue_data['seeking_talent'] = venue.looking_for_talent
  venue_data['seeking_description'] = venue.seeking_description
  venue_data['image_link'] = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

# edit a venue endpoint
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  try:
    is_looking_for_talent = False
    
    if request.form.get('looking_for_talent') == 'y':
      is_looking_for_talent =  True
    
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = '|'.join(request.form.getlist('genres'))
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website_link = request.form.get('website_link')
    venue.looking_for_talent = is_looking_for_talent
    venue.seeking_description =  request.form.get('seeking_description')

    flash('Venue ' + request.form.get('name') + ' was successfully updated!')
    db.session.commit()
  except():
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

# create an artist route
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# create an artist endpoint
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  artist_fields=dict(request.form)
  
  is_looking_for_venues = False
  
  if request.form.get('looking_for_venues') == 'y':
    is_looking_for_venues =  True

  artist_fields['looking_for_venues'] = is_looking_for_venues
  artist_fields['genres'] = '|'.join(request.form.getlist('genres'))
  
  new_artist = Artist(**artist_fields)

  try:
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except():
    db.session.rollback()
    flash('An error occurred. Artist ' + artist_fields.name + ' could not be listed.')
  finally:
    db.session.close()
  print(artist_fields)
  return render_template('pages/home.html')  


#  list of all Shows route
@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
    show_data = {}
    show_data["venue_id"] = show.venue_id
    show_data["artist_id"] = show.artist_id
    show_data["venue_name"] = db.session.query(Venue.name).filter(Venue.id==show.venue_id).first()[0]
    show_data["artist_name"] = db.session.query(Artist.name).filter(Artist.id==show.artist_id).first()[0]
    show_data["artist_image_link"] = db.session.query(Artist.image_link).filter(Artist.id==show.artist_id).first()[0]
    show_data["start_time"] = str(show.start_time)
    data.append(show_data)
  return render_template('pages/shows.html', shows=data)

# create a new show route
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# create a new show endpoint
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    new_show = Show(**request.form)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except():
    db.session.rollback()
    flash('An error occurred. Show could not be listed.\n{}'.format(e))
  finally:
    db.session.close()
  return render_template('pages/home.html')

# app 404 error handler route
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

# app 500 error handler route
@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
