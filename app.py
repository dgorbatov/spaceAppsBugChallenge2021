import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import shortuuid
import firebase_admin
from firebase_admin import credentials, firestore, storage
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath
from geopy.geocoders import Nominatim
import geocoder

# configure firebase DB

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Configure application
app = Flask(__name__)

# Configure geolocation

geolocator = Nominatim(user_agent="geoapiExercises")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config.threaded=True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/",  methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]

            image.save(secure_filename(image.filename))

            url = image.filename

            # pass the image to the ML model and get result
            # assuming model will return bug name:

            bug_name = "test-bug"

            # get user location

            user_ip = request.remote_addr

            g = geocoder.ipinfo(user_ip)
            location = g.latlng

            location = str(geolocator.reverse(g.latlng))

            # add bug info to DB

            db.collection('bugs').add({"name":f"{bug_name}", "location":location})

            return redirect(f"/bug/{bug_name}")

    else:
        return render_template("index.html")

@app.route("/bug/<name>",  methods=["GET", "POST"])
def bug(name):
    # get data from API based on bug name

    description = "sample description"
    image_url = "https://earthbox.com/media/wysiwyg/images/insect/large/Eastern-boxelder-bug.jpg"
    harmful_or_not = "harmful"
    further_steps = "take these steps"

    return render_template("bug.html", name=name, description=description, image_url=image_url, harmful_or_not=harmful_or_not, further_steps=further_steps)
