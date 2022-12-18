import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def density(a,b,c):
    list=[a,b,c]
    sum=0
    for item in list:
        for i in item :
            if i == "/":
                sum = 50
                x= "very dense"
                return sum , x



    sum = int(b) + int(c)


    if sum >= 50:
        x = "Very Dense"
    elif sum <50 and sum >= 30:
        x = " Dense"
    elif sum <30 and sum >= 10:
        x = "Medium Dense"
    elif sum <10 and sum >= 4:
        x = " Loose"
    else:
        x = " Very Loose"
    return sum ,x


def descriptopn(desc):
    list_new =[]
    li=[]
    text=""
    for item in desc:
        if item != "None":
            list_new.append(item)
    for i in list_new:
        if i != " ":
            li.append(i)

    for i in li:
        text += i +", "
    return(text)





