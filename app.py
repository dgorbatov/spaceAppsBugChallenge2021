from flask import Flask, redirect, render_template, request
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.utils import secure_filename
from geopy.geocoders import Nominatim
import geocoder
import requests
import json
import csv;

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
    return render_template("index.html")

@app.route("/home",  methods=["GET", "POST"])
def home():
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
        return render_template("home.html")

@app.route("/map",  methods=["GET"])
def map():
    users_ref = db.collection("bugs")
    docs = users_ref.stream()
    cords = []

    for doc in docs:
        cords.append(doc.to_dict())

    cords = json.dumps(cords)
    return render_template("map.html", cords=cords);

@app.route("/bug/<name>",  methods=["GET", "POST"])
def bug(name):
    bug_name = "Bug Not Found"
    image_url = "https://earthbox.com/media/wysiwyg/images/insect/large/Eastern-boxelder-bug.jpg"
    harmful_or_not = "No Data"
    science_name = "No Data"
    pesticide = "No Data"
    crop = "No Data"

    filename = "bugdata.csv"
    rows = []
    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)

    data = []
    for rowdata in rows:
        if rowdata[0].lower() == name.lower():
            data = rowdata
            break

    if data != []:
        bug_name = data[0]
        image_url = data[5]
        science_name = data[3]
        pesticide = data[4]
        crop = data[2]

        if data[1] == '0':
            harmful_or_not = "harmful"
        else:
            harmful_or_not = "not harmful"

    return render_template("bug.html", name=bug_name,
                                       image_url=image_url,
                                       harmful_or_not=harmful_or_not,
                                       science_name=science_name,
                                       pesticide=pesticide,
                                       crop=crop)
