import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Configure application
app = Flask(__name__)

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
    # add file to database and take reroute user to route for their specific bug ID.
    return render_template("index.html")

@app.route("/bug/<identifier>",  methods=["GET", "POST"])
def bug(identifier):
    # based on identifier - return prediction and type of bug for the bug image user has input.
    # return bug image as well