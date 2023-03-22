from flask import Flask, jsonify

import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


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
        f"Welcome to the climate app<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"

    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    print("Query Date: ", query_date)

    # Perform a query to retrieve the data and precipitation scores
    precip_score = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= query_date).all()
    

    all_prcp = []
    for date, prcp in precip_score:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        
        all_prcp.append(prcp_dict)
    session.close()
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)

   


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    most_active = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    most_active_station = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == most_active[0].station).\
    filter(measurement.date >= query_date).all()

    
    all_tobs = []
    for date, prcp in most_active_station:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["temp"] = prcp
        
        all_tobs.append(prcp_dict)
    session.close()
    return jsonify(all_tobs)

    all_tobs = list(np.ravel(most_active_station))

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%d-%m-%Y")


    most_active_stat = session.query(func.min(measurement.tobs),\
            func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start_date).all()

    session.close()
    all_start = list(np.ravel(most_active_stat))

    return jsonify(all_start)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%d-%m-%Y")
    end_date = dt.datetime.strptime(end, "%d-%m-%Y")


    most_active_stat = session.query(func.min(measurement.tobs),\
            func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()
    all_start = list(np.ravel(most_active_stat))

    return jsonify(all_start)


    
if __name__ == "__main__":
    app.run(debug=True)
