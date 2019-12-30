import os
# API Key= pk_367ebd64ed244414b161ecea3c984499
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask,url_for
import psycopg2

# from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("postgres://rooozmfwvvqrkw:eeffde2be78c3203ef421748bb17511f7dae337a45e9c57ab25e28cf9ddb2a0a@ec2-54-235-250-38.compute-1.amazonaws.com:5432/df0ic2g1r6uo40")
DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

cur.execute("SELECT username FROM users")
usernametest = cur.fetchone()[0]

print("\n\n\n\n\n\n")
print(usernametest)

# db = SQL("sqlite:///data.db")
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


# From helpers.py:
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
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# def usd(value):
    # """Format value as USD."""
    # return f"${value:,.2f}"

# End from helpers.py





@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    #collects data neccessary from users and players
    total_overalls = 0
    counter = 0
    points = cur.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    username = cur.execute("SELECT username FROM users WHERE id=:user_id", user_id=session["user_id"])
    overalls = cur.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
    #iterates through all players owned in collection and adds their overall into a single variable
    for x in overalls:
        total_overalls += x["overall"]
        counter += 1
    total_value= ((total_overalls-(counter*78))*400) + (counter)*5000

    #sets networth
    total_overalls = 0
    counter = 0
    overalls = cur.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
    for x in overalls:
        total_overalls += x["overall"]
        counter += 1
    total_value= ((total_overalls-(counter*78))*400) + (counter)*5000
    print(points)
    networth = total_value + points[0]["cash"]
    cur.execute('UPDATE users SET networth=:networth WHERE id=:user_id', networth=networth, user_id=session["user_id"])
    conn.commit()
    #gets place
    y = 0
    x = 1
    username=username[0]["username"]
    users = cur.execute("SELECT * FROM users ORDER BY networth desc")
    for user in users:
        user["place"] = x
        x += 1
        if user["username"]==username:
            y = user["place"]
    x = x-1

    #stores all player data into collection_images
    collection_images = cur.execute('SELECT * FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id ORDER BY overall desc', user_id=session["user_id"])
    networth = total_value + points[0]["cash"]

    #Sets "instructions" so javascript whether or not to display them
    instructions = int(session['instructions'])
    if instructions == 1:
        session['instructions'] = 0
        return render_template("home.html", username=username, collection_images=collection_images, points=points, total_value=total_value, networth=(networth), instructions=instructions, x=x, y=y)
    if request.method == "POST":
        return render_template("home.html", username=username, collection_images=collection_images, points=points, total_value=total_value, networth=(networth), instructions=instructions, x=x, y=y)
    else:
        return render_template("home.html", username=username, collection_images=collection_images, points=points, total_value=usd(total_value), networth=(networth), instructions=instructions, x=x, y=y)

@app.route("/openpacks", methods=["GET", "POST"])
@login_required
def openpacks():
    points = cur.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    #sets networth
    total_overalls = 0
    counter = 0
    overalls = cur.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
    for x in overalls:
        total_overalls += x["overall"]
        counter += 1
    total_value= ((total_overalls-(counter*78))*400) + (counter)*5000
    networth = total_value + points[0]["cash"]
    cur.execute('UPDATE users SET networth=:networth WHERE id=:user_id', networth=networth, user_id=session["user_id"])
    conn.commit()

    #gets place
    y = 0
    x = 1
    username = cur.execute("SELECT username FROM users WHERE id=:user_id", user_id=session["user_id"])
    username=username[0]["username"]
    users = cur.execute("SELECT * FROM users ORDER BY networth desc")
    for user in users:
        user["place"] = x
        x += 1
        if user["username"]==username:
            y = user["place"]
    x = x-1
    #redirects to the openpacks htmls
    return render_template("openpacks.html", points=points, x=x, y=y)

@app.route("/info", methods=["GET", "POST"])
@login_required
def info():
    points = cur.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    if request.method == "POST":
        user_id = session["user_id"]
        #Selects all the information of a player based on the image link of the form submitted when the player was clicked on from Home
        player = cur.execute("SELECT * FROM players WHERE image=:img", img=request.form["img"])
        name= player[0]['name']
        overall= player[0]['overall']
        team= player[0]['team']
        image= player[0]['image']
        value= ((overall-78)*400) + 5000
        if overall >= 95:
            selling_value= round(value*0.95)
        elif overall >= 90:
            selling_value = round(value*0.97)
        elif overall >= 73:
            selling_value = round(value*0.99)
        else:
            selling_value = round(value)

        #sets networth
        total_overalls = 0
        counter = 0
        overalls = cur.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
        for x in overalls:
            total_overalls += x["overall"]
            counter += 1
        total_value= ((total_overalls-(counter*78))*400) + (counter)*5000
        networth = total_value + points[0]["cash"]
        cur.execute('UPDATE users SET networth=:networth WHERE id=:user_id', networth=networth, user_id=session["user_id"])
        conn.commit()

        #gets place
        y = 0
        x = 1
        username = cur.execute("SELECT username FROM users WHERE id=:user_id", user_id=session["user_id"])
        username=username[0]["username"]
        users = cur.execute("SELECT * FROM users ORDER BY networth desc")
        for user in users:
            user["place"] = x
            x += 1
            if user["username"]==username:
                y = user["place"]
        x = x-1

        return render_template("info.html", points=points, name=name, overall=overall, team=team, image=image, value=(value), selling_value=selling_value, x=x, y=y)
    else:
        return render_template("info.html", points=points, name=name, overall=overall, team=team, image=image, value=(value), selling_value=selling_value, x=x, y=y)

@app.route("/register", methods=["GET", "POST"])
def register():
    #checks requirements for creating an account
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        elif not request.form.get("cpassword"):
            return apology("must confirm password", 403)
        #receives the information through a form
        password=request.form.get("password")
        cpassword=request.form.get("cpassword")
        username=request.form.get("username")
        h_password = generate_password_hash(password)
        #checks that confirm password and password match
        if password != cpassword:
            return apology("password and confirm password must match", 403)
        usernames = cur.execute("SELECT username FROM users")
        #confirms username doesn't exist
        for y in usernames:
            if username == y["username"]:
                return apology("username already taken", 403)
        #inserts the new user into the users database
        session["user_id"] = cur.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=h_password)
        print("\n\n\n session ID:")
        print (session["user_id"])
        session['instructions'] = 1
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    #checks to see both username and password are submitted
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = cur.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        #confirms the username and password exists in users
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        session['instructions'] = 0
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    #clears the session and logs out
    session.clear()
    return redirect("/login")

@app.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    points = cur.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    username = cur.execute("SELECT username FROM users WHERE id=:user_id", user_id=session["user_id"])
    if request.method == "GET":
        #sets networth
        total_overalls = 0
        counter = 0
        overalls = cur.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
        for x in overalls:
            total_overalls += x["overall"]
            counter += 1
        total_value= ((total_overalls-(counter*78))*400) + (counter)*5000
        print("\n\n\n\n\n points without [0][cash]:")
        print(points)
        print("\n\n\n\n\n\n points with [0][cash]")
        print(points[0]["cash"])
        networth = total_value + points[0]["cash"]
        cur.execute('UPDATE users SET networth=:networth WHERE id=:user_id', networth=networth, user_id=session["user_id"])
        conn.commit()

        #Stores all information of users in a list of dicts called users by descending networth
        users = cur.execute("SELECT * FROM users ORDER BY networth desc")
        #creates places
        y = 0
        x = 1
        username = username[0]["username"]
        for user in users:
            user["place"] = x
            x += 1
            if user["username"]==username:
                y = user["place"]
        x = x-1
        return render_template("leaderboard.html", points=points, users=users, username=username, y=y, x=x)
    else:
        return render_template("leaderboard.html", points=points, users=users, username=username, y=y, x=x)

@app.route("/packs", methods=["GET", "POST"])
#@login_required
def packs():
        user_id=session["user_id"]
        points = cur.execute("SELECT cash FROM users WHERE id=:user_id", user_id=user_id)
        #confirms user has enough money
        if not points[0]["cash"] >= 5000:
            return apology("Not Enough Points", 400)
        else:
            #subtracts cost of pack from the user and updates the users table
            points[0]["cash"] = points[0]["cash"] - 5000
            cur.execute('UPDATE users SET cash = ? WHERE id = ?', points[0]["cash"], session['user_id'])
            conn.commit()
            #selects a random player and stores this player's information in random_player
            random_player = cur.execute('SELECT * FROM players ORDER BY RANDOM() LIMIT 1')

            overall = random_player[0]['overall']
            value = ((overall-78)*400) + 5000
            random_player[0]["value"] = (value)
            image = random_player[0]['image']
            if overall >= 95:
                selling_value= round(value*0.95)
            elif overall >= 90:
                selling_value = round(value*0.97)
            elif overall >= 73:
                selling_value = round(value*0.99)
            else:
                selling_value = round(value)

            #adds the newly drafted player into the user's collection
            cur.execute('INSERT into collection(user_id, player_id) VALUES (:id, :random_player)', id=user_id, random_player=random_player[0]["id"])
            conn.commit()

            #sets networth
            total_overalls = 0
            counter = 0
            overalls = cur.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
            for x in overalls:
                total_overalls += x["overall"]
                counter += 1
            total_value= ((total_overalls-(counter*78))*400) + (counter)*5000
            networth = total_value + points[0]["cash"]
            cur.execute('UPDATE users SET networth=:networth WHERE id=:user_id', networth=networth, user_id=session["user_id"])
            conn.commit()

            #gets place
            y = 0
            x = 1
            username = cur.execute("SELECT username FROM users WHERE id=:user_id", user_id=session["user_id"])
            username=username[0]["username"]
            users = cur.execute("SELECT * FROM users ORDER BY networth desc")
            for user in users:
                user["place"] = x
                x += 1
                if user["username"]==username:
                    y = user["place"]
            x = x-1

            if request.method == 'GET':
                user_id=session["user_id"]
                return render_template("packs.html", random_player=random_player, points=points, selling_value=selling_value, image=image, x=x, y=y)

            else:
                return render_template("openpacks.html", points=points, x=x, y=y)

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == 'GET':
        return redirect("/")
    if request.method == 'POST':
        points = cur.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
        #selects all the player's data using the image submitted from the form on home.
        player = cur.execute("SELECT * FROM players WHERE image=:img", img=request.form["img"])
        points = points[0]['cash']
        overall= player[0]['overall']
        player_id = player[0]['id']
        #Value is slightly higher than selling value (see "scoring" in Design.md)
        value= ((overall-78)*400) + 5000
        if overall >= 95:
            selling_value= round(value*0.95)
        elif overall >= 90:
            selling_value = round(value*0.97)
        elif overall >= 73:
            selling_value = round(value*0.99)
        else:
            selling_value = round(value)
        #the player's selling value is added to the user's points and updated
        points += selling_value
        cur.execute('DELETE FROM collection WHERE player_id=:player_id AND user_id=:user_id ORDER BY RANDOM() LIMIT 1', player_id=player_id, user_id=session['user_id'])
        cur.execute('UPDATE users SET cash = ? WHERE id = ?', points, session['user_id'])
        conn.commit()
        return redirect("/")



@app.route("/sellfrompacks", methods=["GET", "POST"])
@login_required
def sellfrompacks():
    if request.method == 'GET':
        return redirect("/openpacks")
    if request.method == 'POST':
        points = cur.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
        #selects all the player's data using the image submitted from the form on home.
        player = cur.execute("SELECT * FROM players WHERE image=:img", img=request.form["img"])
        points = points[0]['cash']
        overall= player[0]['overall']
        player_id = player[0]['id']
        #Value is slightly higher than selling value (see "scoring" in Design.md)
        value= ((overall-78)*400) + 5000
        if overall >= 95:
            selling_value= round(value*0.95)
        elif overall >= 90:
            selling_value = round(value*0.97)
        elif overall >= 73:
            selling_value = round(value*0.99)
        else:
            selling_value = round(value)
        #the player's selling value is added to the user's points and updated
        points += selling_value
        cur.execute('DELETE FROM collection WHERE player_id=:player_id AND user_id=:user_id ORDER BY RANDOM() LIMIT 1', player_id=player_id, user_id=session['user_id'])
        cur.execute('UPDATE users SET cash = ? WHERE id = ?', points, session['user_id'])
        conn.commit()
        return redirect("/openpacks")