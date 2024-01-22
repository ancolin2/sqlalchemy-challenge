# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Starter_Code/Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def index():
    return("Welcome to the Homepage<br>"
           "Here are your routes:<br>"
           "/api/v1.0/precipitation<br>"
           "/api/v1.0/stations<br>"
           "/api/v1.0/tobs<br>"
           "/api/v1.0/<start><br>"
           "/api/v1.0/<start>/<end>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    #get the last date
    recent_data = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #get the date 1year before the last date to get the past 12 months
    x = dt.datetime.strptime(recent_data[0], '%Y-%m-%d')
    querydate = dt.date(x.year-1,x.month,x.day)
    #get the dates and precipitation that are within the 12 month period
    precip = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date <= recent_data[0]).\
        filter(Measurement.date >= querydate).all()
    #Close session
    session.close()
    return jsonify(dict(precip))

@app.route("/api/v1.0/stations")
def stations():
    #Get the stations, count them, sort by the highest count to the lowest count
    stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    #Turn them into a list
    station_list = list(np.ravel(stations))
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #Get the stations, count them, sort from highest count to the lowest count
    active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    #Get the date that is most recent
    recent_data = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #Calculate 1 year before most recent date
    x = dt.datetime.strptime(recent_data[0], '%Y-%m-%d')
    querydate = dt.date(x.year-1,x.month,x.day)
    #Get the temperature observations of that year
    date_temp = session.query(Measurement.tobs).\
        filter(Measurement.station ==active_station[0][0]).\
            filter(Measurement.date <= recent_data[0]).\
                filter(Measurement.date >= querydate).all()
    #Sort them into a list
    tobs_station = list(np.ravel(date_temp))
    session.close()
    return jsonify(tobs_station)  
      
@app.route("/api/v1.0/<start>")
#Make start a variable that needs to be entered
def starting_date(start):
    #Get the most recent date in the table as the end date
    x = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    end = dt.datetime.strptime(x[0], '%Y-%m-%d')
    #Calculate the minimum, average, and maximum withing the specified start and with the end date being the most recent date
    TMIN = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    TAVG = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    TMAX = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()
    #Add to a list
    temperatures = [TMIN, TAVG, TMAX]
    session.close()
    return jsonify(list(np.ravel(temperatures)))

@app.route("/api/v1.0/<starting>/<ending>")
#Make a starting and ending variable
def start_and_end(starting, ending):
    minimum = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= starting).filter(Measurement.date <= ending).first()
    average = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= starting).filter(Measurement.date <= ending).first()
    maximum = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= starting).filter(Measurement.date <= ending).first()
    start_end_temperatures = [minimum, average, maximum]
    session.close()
    return jsonify(list(np.ravel(start_end_temperatures)))


if __name__=="__main__":
    app.run(debug = True)