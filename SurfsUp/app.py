# Import the dependencies.
import numpy as np
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"start and end date format: (yyyy-mm-dd)"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    # Results filtered to a year back
    results = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date >= "2016-08-24").all()

    session.close()

    # List builder to turn into json
    prcp_results = [{date:prcp} for prcp, date in results]
    
    return jsonify(prcp_results)

# Station Route
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

# Temperature Observations Route
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs, Measurement.prcp).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station =='USC00519281').all()

    session.close()

    # List builder to turn into json
    all_tobs = [{"prcp":prcp, "date":date, "tobs":tobs} for prcp, date, tobs in results]

    return jsonify(all_tobs)

#################################################
# Dynamic Flask Routes
#################################################

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    session = Session(engine) 

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close() 

    # List builder to turn into json
    start_date_tobs_values =[{"start_date":start, "min":min, "average":avg, "max":max} for min, avg, max in results]

    return jsonify(start_date_tobs_values)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    session = Session(engine)

    results = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date <= end).filter(Measurement.date >= start).all()

    session.close()

    # List builder to turn into json
    start_end_date_tobs = [{"start_date":start, "end_date":end, "min":min, "average":avg, "max":max} for min, avg, max in results]

    return jsonify(start_end_date_tobs)

if __name__ == '__main__':
    app.run(debug=True)

