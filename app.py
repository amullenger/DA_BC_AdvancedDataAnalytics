import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from datetime import datetime

from flask import Flask, jsonify

#create connection to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#setup base and reflect tables
Base = automap_base()
Base.prepare(engine, reflect=True)

#create table references
Measurement = Base.classes.measurement
Station = Base.classes.station

#create session
session = Session(engine)

#flask setup
app = Flask(__name__)

#establish flask routes
@app.route("/")
def welcome():
    """List all available routes"""
    return(
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/  <--choose a start date<br/>"
        f"/api/v1.0/  <--choose a start and end date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    l_d_dt = datetime.strptime(latest_date[0], '%Y-%m-%d')
    months_ago_12 = l_d_dt - dt.timedelta(days = 365)
    m_a_12 = months_ago_12.date()

    # Perform a query to retrieve the data and precipitation scores
    res = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= m_a_12).all()
    
    prcp_dict = {}
    for i in range(len(res)):
        prcp_dict[res[i][0]] = res[i][1]
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    res = session.query(Station.station).all()

    #convert tuples to list
    all_stations = list(np.ravel(res))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    l_d_dt = datetime.strptime(latest_date[0], '%Y-%m-%d')
    months_ago_12 = l_d_dt - dt.timedelta(days = 365)
    m_a_12 = months_ago_12.date()

    temp_data_12_mo = session.query(Measurement.tobs).\
    filter(Measurement.date >= m_a_12).all()    
    
    temp_list = []
    for i in range(len(temp_data_12_mo)):
        temp_list.append(temp_data_12_mo[i][0])
    
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def stats_after_start(start):
    temps = session.query(Measurement.tobs).filter(Measurement.date >= start).all()
    temps_list = list(np.ravel(temps))

    max_temp = max(temps_list)
    min_temp  = min(temps_list)
    avg_temp = np.mean(temps_list)

    ret_dict = {"Max temp": max_temp, "Min Temp": min_temp, "Average Temp": avg_temp}

    return jsonify(ret_dict)

@app.route("/api/v1.0/<start>/<end>")
def stats_between_dates(start, end):
    temps = session.query(Measurement.tobs).filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps_list = list(np.ravel(temps))

    max_temp = max(temps_list)
    min_temp = min(temps_list)
    avg_temp = np.mean(temps_list)

    ret_dict = {"Max temp": max_temp, "Min Temp": min_temp, "Average Temp": avg_temp}

    return jsonify(ret_dict)

if __name__ == '__main__':
    app.run(debug = False)