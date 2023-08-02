from flask import Flask , redirect
import string
import random
import datetime
import requests

def if_is_url(url_string) :
    try:
        response = requests.get(url_string)

        return True
    except :
        return False

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Please enter your URL onto the search tab!</p>"


@app.route("/{}".format("123"))
def hello_123():
    return redirect("https://pynative.com/python-generate-random-string/" , code = 302)

print(if_is_url("https://tiktok.cm/"))