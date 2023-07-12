# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
def home():
    return """ <h1> Climate API - Hawaii </h1> 
    <h3> Available API Routes: </h3>
    <ul>
        <li><a href = "/api/v1.0/precipitation"> Precipitation </a> </li>
        <li><a href = "/api/v1.0/stations"> Stations </a> </li>
        <li><a href = "/api/v1.0/tobs"> Temperature </a></li>
    </ul>
        """

@app.route("/api/v1.0/precipitation")
def precipitation():
    end_date = session.query(func.max(measurement.date)).first()[0]
    start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days = 365)
    yearly_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= str(start_date)).all()

    list_prcp = []
    for date, prcp in yearly_prcp:
        dict_prcp = {}
        dict_prcp["date"] = date
        dict_prcp["prcp"] = prcp
        list_prcp.append(dict_prcp)
    
    return jsonify(list_prcp)

@app.route("/api/v1.0/stations")
def stations():
    station_info = session.query(station.station).all()
    
    list_stations = list(np.ravel(station_info))

    return jsonify(list_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    end_date = session.query(func.max(measurement.date)).first()[0]
    start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days = 365)

    tobs_data = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= start_date).all()

    list_tobs = []
    for date, tobs in tobs_data:
        dict_tobs = {}
        dict_tobs["date"] = date
        dict_tobs["tobs"] = tobs
        list_tobs.append(dict_tobs)
    
    return jsonify(list_tobs)

@app.route("/api/v1.0/<start>")
def start_day(start):
    start_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).all()

    start_values = []
    for min, max, avg in start_results:
        start_dict = {}
        start_dict["min"] = min
        start_dict["max"] = max
        start_dict["avg"] = avg
        start_values.append(start_dict)

    return jsonify(start_values)

@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start, end):
    ste_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()

    ste_values = []
    for min, max, avg in ste_results:
        ste_dict = {}
        ste_dict["min"] = min
        ste_dict["max"] = max
        ste_dict["avg"] = avg
        ste_values.append(ste_dict)

    return jsonify(ste_values)

session.close()

if __name__ == "__main__":
    app.run(debug = True)