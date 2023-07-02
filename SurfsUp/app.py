# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


#################################################
# Database Setup.
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflects an existing database into a new model.
Base = automap_base()
# Reflect the tables.
Base.prepare(autoload_with=engine)

# Saves references to each table.
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creates session (link) from Python to the DB.
session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Homepage route. 
@app.route("/")
def homepage():
    """List all available api routes"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

# Precipitation route. #
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Finds the most recent date in the data set.
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # Converts latest_date string to a date format.
    latest_date = datetime.strptime(latest_date, "%Y-%m-%d")

    # Extracts the year, month, and day from latest_date.
    latest_year = latest_date.year
    latest_month = latest_date.month
    latest_day = latest_date.day

    # The most recent data point in the database (in ISO format). 
    latest_date = dt.date(latest_year, latest_month, latest_day)

    # Calculates the date one year from the last date in data set.
    one_year_prior = latest_date - dt.timedelta(days=365)

    # The below query retrieves the last 12 months of precipitation data.
    sel = [Measurement.date,
           Measurement.prcp]

    latest_year_prcp = session.query(*sel).\
                       filter(Measurement.date >= one_year_prior).\
                       filter(Measurement.date <= latest_date).\
                       order_by(Measurement.date).all()
    
    # Creates a dictionary from the row data and appends to a list of annual_precipitation.
    annual_precipitation = []
    for date, prcp in latest_year_prcp:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        annual_precipitation.append(precipitation_dict)

    return jsonify(annual_precipitation)
    
    session.close()

# Station route.
@app.route("/api/v1.0/stations")
def stations():
    #Creates a session (link) from Python to DB. 
    session = Session(engine)

    # Returns a list of all stations. 
    stations = session.query(Station.station).all()

    session.close()

    #Convert list of tuples into normal list.
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)


if __name__ == '__main__':
    app.run(debug=True)
