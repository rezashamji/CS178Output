from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Agency(db.Model):
    __tablename__ = 'agency'
    agency_id = db.Column(db.String, primary_key=True)
    agency_name = db.Column(db.String)
    agency_url = db.Column(db.String)
    agency_timezone = db.Column(db.String)
    agency_lang = db.Column(db.String, nullable=True)
    agency_phone = db.Column(db.String, nullable=True)
    agency_fare_url = db.Column(db.String, nullable=True)

class Stops(db.Model):
    __tablename__ = 'stops'
    stop_id = db.Column(db.String, primary_key=True)
    stop_code = db.Column(db.String, nullable=True)
    stop_name = db.Column(db.String)
    stop_desc = db.Column(db.String, nullable=True)
    stop_lat = db.Column(db.Float)
    stop_lon = db.Column(db.Float)
    stop_url = db.Column(db.String, nullable=True)
    location_type = db.Column(db.Integer, nullable=True)
    stop_timezone = db.Column(db.String, nullable=True)
    wheelchair_boarding = db.Column(db.Integer, nullable=True)
    platform_code = db.Column(db.String, nullable=True)
