# Imports dependencies.
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
base = automap_base()
# Reflect the tables.
base.prepare(autoload_with=engine)

# Saves references to each table.
measurement = base.classes.measurement
station = base.classes.station

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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd <br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# Precipitation route. 
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Finds the most recent date in the data set.
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

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
    sel = [measurement.date,
           measurement.prcp]

    latest_year_prcp = session.query(*sel).\
                       filter(measurement.date >= one_year_prior).\
                       filter(measurement.date <= latest_date).\
                       order_by(measurement.date).all()
    
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
    stations = session.query(station.station).all()

    session.close()

    #Convert list of tuples into normal list.
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)


# Tobs route. 
@app.route("/api/v1.0/tobs")
def tobs():
    #Creates a session (link) from Python to DB. 
    session = Session(engine)

    # Query which finds the most active stations (i.e. which stations have the most rows).
    # Stations and their counts are listed in descending order.
    station_activity = session.query(measurement.station, func.count(measurement.station)).\
                    group_by(measurement.station).\
                    order_by(func.count(measurement.station).desc()).all()
    
    most_active_station = station_activity[0][0]

    # Finds the most recent date in the data set when filtered only to the most active station.
    active_latest_date = session.query(measurement.date).\
                                filter(measurement.station == most_active_station).\
                                order_by(measurement.date.desc()).first()[0]
    
    # Converts active_latest_date string to a date format.
    active_latest_date = datetime.strptime(active_latest_date, "%Y-%m-%d")

    # Extracts the year, month, and day from active_latest_date.
    active_latest_year = active_latest_date.year
    active_latest__month = active_latest_date.month
    active_latest_day = active_latest_date.day

    # The most recent data point in the database when filtered to the most active station (in ISO format). 
    active_latest_date = dt.date(active_latest_year, active_latest__month ,active_latest_day)

    # Calculates the date one year from active_latest_date.
    active_one_year_prior = active_latest_date - dt.timedelta(days=365)

    # Queries the last 12 months of temperature observation data for the most active station.

    active_latest_year_tobs = session.query(measurement.tobs).\
                   filter(measurement.station == most_active_station).\
                   filter(measurement.date >= active_one_year_prior).\
                   filter(measurement.date <= active_latest_date).\
                   order_by(measurement.date).all()

    
        
    session.close()

    #Convert list of tuples into normal list.
    active_annual_tobs = list(np.ravel(active_latest_year_tobs))

    return jsonify(active_annual_tobs)

# Start Route. 
@app.route("/api/v1.0/<start>")
def start_date(start):
    
    canonicalized = start.replace(" ", "")
    canonicalized = start.replace(".", "-")
    
    #Creates a session (link) from Python to DB. 
    session = Session(engine)

    earliest_date = session.query(measurement.date).order_by(measurement.date).first()[0]
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

    if start >= earliest_date and start <= latest_date:

        # The below queries will returns the minimum, average, and maximum tobs of all dates after the start date specified. 
    
        sel = [func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)]
        

        tobs_after_start = session.query(*sel).\
                        filter(measurement.date >= start).\
                        order_by(measurement.date).all()
    
    
        # Creates a dictionary from the row data and appends to a list of after_start_tobs_summary.
        after_start_tobs_summary = []
        for min, avg, max in tobs_after_start:
            tobs_after_start_dict = {}
            tobs_after_start_dict["TMIN"] = min
            tobs_after_start_dict["TAVG"] = avg
            tobs_after_start_dict["TMAX"] = max
            after_start_tobs_summary.append(tobs_after_start_dict)

        return jsonify(after_start_tobs_summary)

    else:
        return "Error: The input date was not within the data range, please try another date."
    
    session.close()


# Start-End Route. 
@app.route("/api/v1.0/<start>/<end>")
def start_end_dates(start, end):
    
    canonicalized = start.replace(" ", "")
    canonicalized = start.replace(".", "-")
    canonicalized = end.replace(" ", "")
    canonicalized = end.replace(".", "-")
    
    #Creates a session (link) from Python to DB. 
    session = Session(engine)

    earliest_date = session.query(measurement.date).order_by(measurement.date).first()[0]
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]

    if start >= earliest_date and start <= latest_date and end >= earliest_date and end <= latest_date:

        # The below queries will returns the minimum, average, and maximum tobs of all dates on the start and end dates specified. 
    
        sel = [func.min(measurement.tobs),
            func.avg(measurement.tobs),
            func.max(measurement.tobs)]
        

        between_date_tobs = session.query(*sel).\
                        filter(measurement.date >= start).\
                        filter(measurement.date <= end).\
                        order_by(measurement.date).all()
    
    
        # Creates a dictionary from the row data and appends to a list of between_dates_tobs_summmary.
        between_dates_tobs_summmary = []
        for min, avg, max in between_date_tobs:
            tobs_between_dates_dict = {}
            tobs_between_dates_dict["TMIN"] = min
            tobs_between_dates_dict["TAVG"] = avg
            tobs_between_dates_dict["TMAX"] = max
            between_dates_tobs_summmary.append(tobs_between_dates_dict)

        return jsonify(between_dates_tobs_summmary)

    else:
        return "Error: Either both, or one of the start date and end dates input were not within the data range, please try again with a revised date."
    
    session.close()



if __name__ == '__main__':
    app.run(debug=True)