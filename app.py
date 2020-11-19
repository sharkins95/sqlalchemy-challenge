# Import flask and dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

import datetime as dt

# Set up database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Setup Flask
app = Flask(__name__)

# Flask routes
@app.route("/")
def home():
    return (
        f"All Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from python to DB
    session = Session(engine)

    # Query for date and prcp
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Convert query results to dictionary using date as the key and prcp as the value
    measurements = []
    for date, prcp in results:
        dict = {date : prcp}
        measurements.append(dict)
    
    # Close session
    session.close()

    # Return JSON representation of dictionary
    return jsonify(measurements)

@app.route("/api/v1.0/stations")
def stations():
    # Create session from python to DB
    session = Session(engine)

    stations = session.query(Station.station).all()

    # Close session
    session.close()

    # Return JSON list of stations from dataset
    stations_list = list(np.ravel(stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from python to DB
    session = Session(engine)

    # Query the date and temp observations of the most active station for the last year of data
    station_id = 'USC00519281'

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_date = dt.datetime.strptime(last_date,'%Y-%m-%d')-dt.timedelta(days=366)

    # Return a JSON list of tobs for the previous year
    temps = []
    most_active = session.query(Measure.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_date).filter(Measurement.station == station_id).all()

    for station, date, tobs in most_active:
        tobs={ }
        tobs['Date'] = date
        tobs['Station ID'] = station
        tobs['tobs'] = tobs
        temps.append(tobs)

    # Close session
    session.close()

    # Return JSON list
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
# When given the start only, calculate TMIN, TAVG, and TMAX for
#  all dates greater than and equal to the start date
def start():
    # Create session from python to DB
    session = Session(engine)

    # Query for min, max, and avg
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Close session
    session.close()

    # Return a JSON list
    temp_results = []
    for min, max, avg in results:
        result_qry={ }
        result_qry['Tmin'] = min
        result_qry['Tmax'] = max
        result_qry['Tavg'] = avg
        temp_results.append(result_qry)

    return jsonify(temp_results)

@app.route("/api/v1.0/<start>/<end>")
# When given the start and the end date, calculate the TMIN, TAVG, and 
# TMAX for dates between the start and end date inclusive
def start_end():
    # Create session from python to DB
    session = Session(engine)

    # Query for min, max, and avg
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Close session
    session.close()

    # Return a JSON list
    temp_results = []
    for min, max, avg in results:
        result_qry={ }
        result_qry['Tmin'] = min
        result_qry['Tmax'] = max
        result_qry['Tavg'] = avg
        temp_results.append(result_qry)

    return jsonify(temp_results)

if __name__ == "__main__":
    app.run(debug=True)