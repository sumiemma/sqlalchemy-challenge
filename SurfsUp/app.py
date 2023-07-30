# Import the dependencies.

import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

def get_tob(start_date, end_date):
    session = Session(engine)
    tobs_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    Session.close()

    tobs_list = []
    tobs_dict = {
        "TMIN" : tobs_result[0][0],
        "TAVG" : tobs_result[0][1], 
        "TMAX" : tobs_result[0][2]
    }
    tobs_list.append(tobs_dict) 

    return(tobs_list)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )




@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return percipitation of last year"""
    # Query
    results = session.query(Measurement.date, Measurement.prcp).filter((Measurement.date >= '2016-08-23')).order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of date and prcp
    last_year_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        last_year_prcp.append(prcp_dict)

    # Convert list of tuples into normal list
    last_year_prcp = list(np.ravel(results))


    session.close()


    return jsonify(last_year_prcp)




@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))


    return jsonify(all_stations)





@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the dates and temperature observations of the most action station for the previous year"""
    # Query all stations
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.date >= '2016-08-23')).filter((Measurement.station == 'USC00519281')).all()

    session.close()

    # Create a dictionary from the row data and append to a list of last_year_Temp_most_active
    last_year_Temp_most_active = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        last_year_Temp_most_active.append(temp_dict)


    return jsonify(last_year_Temp_most_active)





@app.route("/api/v1.0/<start>")
def start_tobs(start):

    """End date of query as today"""
    start_date = dt.datetime.strptime(start, '%m%d%Y')
    end_date = dt.datetime.today().strftime('%m%d%Y')
    return (jsonify(get_tob(start_date,end_date)))




@app.route("/api/v1.0/<start>/<end>")
def start_end_tobs(start,end):
    start_date = dt.datetime.strptime(start, '%m%d%Y')
    end_date = dt.datetime.strptime(end, '%m%d%Y')
    return (jsonify(get_tob(start_date,end_date)))


if __name__ == '__main__':
    app.run(debug=True)
