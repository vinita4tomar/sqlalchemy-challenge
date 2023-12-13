# Import the dependencies.
import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"
    )

# Precipition route
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    session.close()

    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)


# Stations route
@app.route("/api/v1.0/stations")
def stations():
    
    station_names = session.query(Station.station).all()
    session.close()

    names = list(np.ravel(station_names))

    return jsonify(StationNames = names)


# Tempeerature route
@app.route("/api/v1.0/tobs")
def temp():
    
    station_data = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').all()

    session.close()

    data = list(np.ravel(station_data))

    return jsonify(Temperatures = data)


# start and end date route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def tempbydate(start = None, end = None):
    
    try:
        start = dt.datetime.strptime(start, "%m%d%Y")
    
    except:
        return jsonify({"Error: Incorrect data format, should be MMDDYYYY"}), 404

    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    # When only start date is given
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temp_data = list(np.ravel(results))
        return jsonify(temp_data)

    # When start and end dates are given
    try:
        end = dt.datetime.strptime(end, "%m%d%Y")
    
    except:
        return jsonify({"Error: Incorrect data format, should be MMDDYYYY"}), 404

    results = session.query(*sel).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temp_data = list(np.ravel(results))
    return jsonify(temp_data)
    
    
if __name__ == "__main__":
    app.run(debug=True)