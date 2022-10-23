#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from cProfile import run
import json
import sys
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from datetime import datetime
from wtforms import ValidationError
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    genres = db.Column(db.String(), nullable=False)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())

    shows = db.relationship('Show', backref='venue')

    # Implementation Done


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())

    shows = db.relationship('Show', backref='artist')

    # Implementation Done


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime())


db.create_all()
# Implementation Done

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    places = Venue.query.distinct(Venue.city, Venue.state).all()
    areas = []
    for place in places:
        venues_in_the_city = Venue.query.filter_by(
            state=place.state, city=place.city).all()
        areas.append(
            {"city": place.city, "state": place.state, "venues": venues_in_the_city})

    return render_template('pages/venues.html', areas=areas)

    # Implementation Done


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    try:
        search_term = request.form.get('search_term')
        search_result = Venue.query.filter(
            Venue.name.ilike('%{}%'.format(search_term))).all()
        results = {"count": len(search_result), "data": search_result}
    except:
        flash("Something went wrong with search venue")
    finally:
        return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))

    # Implementation Done


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    venue.genres = venue.genres.split(' ')
    ans = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0
    }

    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()
    past_shows = []
    for show in past_shows_query:
        past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.venue_id == venue_id).filter(Show. start_time > datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    ans["past_shows"] = past_shows
    ans["upcoming_shows"] = upcoming_shows
    ans["past_shows_count"] = len(past_shows)
    ans["upcoming_shows_count"] = len(upcoming_shows)
    print(ans)
    return render_template('pages/show_venue.html', venue=ans)

    # Implementation Done

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    try:
        form = VenueForm(request.form)
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        image_link = form.image_link.data
        facebook_link = form.facebook_link.data
        website = form.website_link.data
        tmp_genres = request.form.getlist('genres')
        seeking_description = form.seeking_description.data
        new_venue = Venue(name=name,
                          city=city,
                          state=state,
                          address=address,
                          phone=phone,
                          genres=','.join(tmp_genres),
                          image_link=image_link,
                          facebook_link=facebook_link,
                          website=website,
                          seeking_talent=True if request.form.get(
                              'seeking_talent') != None else False,
                          seeking_description=seeking_description)
        db.session.add(new_venue)
        db.session.commit()

        # Implementation Done

    # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except ValidationError:
        db.session.rollback()
        flash("Enter valid data")
    except:
        db.session.rollback()
        flash("An error occurred when creating venue.")
        print(sys.exc_info())

        # Implementation Done

    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue_to_delete = Venue.query.filter(venue_id == Venue.id)
        venue_to_delete.delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return redirect(url_for("venues"))

    # Implementation Done
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    artists = db.session.query(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=artists)

    # Implementation Done


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    try:
        search_term = request.form.get('search_term')
        search_result = Artist.query.filter(
            Artist.name.ilike('%{}%'.format(search_term))).all()
        results = {"count": len(search_result), "data": search_result}
    except:
        flash("Something went wrong with Artist search")
    finally:
        return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))

    # Implementation Done


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)
    artist.genres = artist.genres.split(' ')
    ans = {"id": artist.id,
           "name": artist.name,
           "genres": artist.genres,
           "city": artist.city,
           "state": artist.state,
           "phone": artist.phone,
           "seeking_venue": artist.seeking_venue,
           "seeking_description": artist.seeking_description,
           "image_link": artist.image_link,
           "facebook_link": artist.facebook_link,
           "website": artist.website,
           "past_shows": [],
           "upcoming_shows": [],
           "past_shows_count": 0,
           "upcoming_shows_count": 0}
    past_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
    past_shows = []
    for show in past_shows_query:
        past_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(
        Show.artist_id == artist_id).filter(Show. start_time > datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    ans["upcoming_shows"] = upcoming_shows
    ans["past_shows"] = past_shows
    ans["past_shows_count"] = len(past_shows)
    ans["upcoming_shows_count"] = len(upcoming_shows)
    return render_template('pages/show_artist.html', artist=ans)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # TODO: populate form with fields from artist with ID <artist_id>

    data = Artist.query.get(artist_id)
    artist = {
        "id": data.id,
        "name": data.name,
        "genres": data.genres.split(", "),
        "city": data.city,
        "state": data.state,
        "phone": data.phone,
        "website_link": data.website,
        "facebook_link": data.facebook_link,
        "seeking_venue": data.seeking_venue,
        "seeking_description": data.seeking_description,
        "image_link": data.image_link,
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)

    # Implementation Done


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    try:
        data = Artist.query.get(artist_id)

        # using request.form.get is safer than accessing the value directly to handel null cases
        data.name = request.form.get('name')
        data.genres = ', '.join(request.form.getlist('genres'))
        data.city = request.form.get('city')
        data.state = request.form.get('state')
        data.phone = request.form.get('phone')
        data.facebook_link = request.form.get('facebook_link')
        data.image_link = request.form.get('image_link')
        data.website = request.form.get('website_link')
        data.seeking_venue = True if request.form.get(
            'seeking_venue') != None else False
        data.seeking_description = request.form.get('seeking_description')
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Something went wrong")
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    data = Venue.query.get(venue_id)
    venue = {
        "id": data.id,
        "name": data.name,
        "genres": data.genres.split(", "),
        "address": data.address,
        "city": data.city,
        "state": data.state,
        "phone": data.phone,
        "website": data.website,
        "facebook_link": data.facebook_link,
        "seeking_talent": data.seeking_talent,
        "seeking_description": data.seeking_description,
        "image_link": data.image_link,
    }

    # Implementation Done

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        data = Venue.query.get(venue_id)

        data.name = request.form.get('name')
        data.genres = ', '.join(request.form.getlist('genres'))
        data.address = request.form.get('address')
        data.city = request.form.get('city')
        data.state = request.form.get('state')
        data.phone = request.form.get('phone')
        data.facebook_link = request.form.get('facebook_link')
        data.image_link = request.form.get('image_link')
        data.website = request.form.get('website_link')
        data.seeking_talent = True if request.form.get(
            'seeking_talent') != None else False
        data.seeking_description = request.form.get('seeking_description')
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
        flash("Something went wrong")
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        form = ArtistForm(request.form)
        tmp_genres = request.form.getlist('genres')
        name = form.name.data
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        facebook_link = form.facebook_link.data
        image_link = form.image_link.data
        website = form.website_link.data
        seeking_description = form.seeking_description.data
        new_artist = Artist(name=name,
                            genres=', '.join(tmp_genres),
                            city=city,
                            state=state,
                            phone=phone,
                            facebook_link=facebook_link,
                            image_link=image_link,
                            website=website,
                            seeking_venue=True if request.form.get(
                                'seeking_venue') != None else False,
                            seeking_description=seeking_description)
        db.session.add(new_artist)
        db.session.commit()
    # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except ValidationError:
        flash("Enter valid data")
    except:
        db.session.rollback()
        flash("An error occurred when creating artist.")
        print(sys.exc_info())
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    shows_plain = Show.query.all()
    shows = []
    for s in shows_plain:
        show = {}
        show["venue_id"] = s.venue.id
        show["venue_name"] = s.venue.name
        show["artist_id"] = s.artist.id
        show["artist_name"] = s.artist.name
        show["artist_image_link"] = s.artist.image_link
        show["start_time"] = s.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        shows.append(show)
    print(shows[:])
    return render_template('pages/shows.html', shows=shows)

    # ?Implementation Done


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    try:
        new_show = Show(
            start_time=request.form.get('start_time'),
            venue_id=request.form.get('venue_id'),
            artist_id=request.form.get('artist_id')
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        flash("Something went wrong")
    finally:
        db.session.close()

    return render_template('pages/home.html')

    # Implementation Done


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
