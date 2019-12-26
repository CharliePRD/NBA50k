import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask,url_for

from helpers import apology, login_required, usd

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_env.filters["usd"] = usd

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///data.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    #collects data neccessary from users and players
    total_overalls = 0
    counter = 0
    points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    username = db.execute("SELECT username FROM users WHERE id=:user_id", user_id=session["user_id"])
    overalls = db.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
    #iterates through all players owned in collection and adds their overall into a single variable
    for x in overalls:
        total_overalls += x["overall"]
        counter += 1
    total_value= ((total_overalls-(counter*78))*400) + (counter)*5000
    #stores all player data into collection_images
    collection_images = db.execute('SELECT * FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id ORDER BY overall desc', user_id=session["user_id"])
    networth = total_value + points[0]["cash"]
    #updates the networth of the user based on the total overalls of the owned players * 65
    db.execute('UPDATE users SET networth = ? WHERE id = ?', networth, session['user_id'])
    #Sets "instructions" so javascript whether or not to display them
    instructions = int(session['instructions'])
    if instructions == 1:
        session['instructions'] = 0
        return render_template("home.html", username=username, collection_images=collection_images, points=points, total_value=total_value, networth=usd(networth), instructions=instructions)
    if request.method == "POST":
        return render_template("home.html", username=username, collection_images=collection_images, points=points, total_value=total_value, networth=usd(networth), instructions=instructions)
    else:
        return render_template("home.html", username=username, collection_images=collection_images, points=points, total_value=usd(total_value), networth=usd(networth), instructions=instructions)

@app.route("/openpacks", methods=["GET", "POST"])
@login_required
def openpacks():
    #redirects to the openpacks htmls
    points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    return render_template("openpacks.html", points=points)

@app.route("/info", methods=["GET", "POST"])
@login_required
def info():
    points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    if request.method == "POST":
        #Selects all the information of a player based on the image link of the form submitted when the player was clicked on from Home
        player = db.execute("SELECT * FROM players WHERE image=:img", img=request.form["img"])
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
        return render_template("info.html", points=points, name=name, overall=overall, team=team, image=image, value=usd(value), selling_value=selling_value)
    else:
        return render_template("info.html", points=points, name=name, overall=overall, team=team, image=image, value=usd(value), selling_value=selling_value)

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
        #inserts the new user into the users database
        session["user_id"] = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=h_password)
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

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
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

#@app.route("/refund")
#def refund():
    #THIS IS COMMENTED OUT AND NOT INCLUDED IN MY WEBSITE, BUT KEPT HERE SO THAT I COULD REIMPLIMENT LATER IF NEEDED. ALLOWS A PLAYER TO BE REFUNDED THEIR CASH SPENT ON A PACK.
    #points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    #user_id = session['user_id']
    #points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=user_id)
    #points[0]["cash"] = points[0]["cash"] + 5000
    #db.execute('UPDATE users SET cash = ? WHERE id = ?', points[0]["cash"], session['user_id'])
    #return render_template("openpacks.html", points=points)

@app.route("/leaderboard", methods=["GET", "POST"])
@login_required
def leaderboard():
    points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    if request.method == "GET":
        total_overalls = 0
        counter = 0
        overalls = db.execute('SELECT overall FROM players JOIN collection ON collection.player_id = players.id WHERE user_id=:user_id', user_id=session["user_id"])
        for x in overalls:
            total_overalls += x["overall"]
            counter += 1
        total_value= ((total_overalls-(counter*78))*400) + (counter)*5000
        networth = total_value + points[0]["cash"]
        db.execute('UPDATE users SET networth=:networth WHERE id=:user_id', networth=networth, user_id=session["user_id"])

        #Stores all information of users in a list of dicts called users by descending networth
        users = db.execute("SELECT * FROM users ORDER BY networth desc")
        #creates places
        x = 1
        for user in users:
            user["place"] = x
            x += 1
        return render_template("leaderboard.html", points=points, users=users)
    else:
        return render_template("leaderboard.html", points=points, users=users)

@app.route("/packs", methods=["GET", "POST"])
#@login_required
def packs():
    points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    if request.method == 'GET':
        user_id=session["user_id"]
        #confirms user has enough money
        if not points[0]["cash"] >= 5000:
            return apology("Not Enough Points", 400)
        else:
            #subtracts cost of pack from the user and updates the users table
            points[0]["cash"] = points[0]["cash"] - 5000
            db.execute('UPDATE users SET cash = ? WHERE id = ?', points[0]["cash"], session['user_id'])
            #selects a random player and stores this player's information in random_player
            random_player = db.execute('SELECT * FROM players ORDER BY RANDOM() LIMIT 1')

            overall = random_player[0]['overall']
            value = ((overall-78)*400) + 5000
            random_player[0]["value"] = usd(value)
            image = random_player[0]['image']
            if overall >= 95:
                selling_value= round(value*0.95)
            elif overall >= 90:
                selling_value = round(value*0.97)
            elif overall >= 73:
                selling_value = round(value*0.99)
            else:
                selling_value = round(value)

            #THIS IS COMMENTED OUT AND NOT INCLUDED. WAS USED BEFORE TO NOT ALLOW DUPLICATE PLAYERS, BUT AS DESIGN.md SAYS I DECIDED AGAINST IT:
            #player_ids = db.execute('SELECT player_id FROM collection WHERE id=:user_id', user_id=session['user_id'])
            #player_found = 0
            #for i in range(len(player_ids)):
                #if random_player[0]["id"]==player_ids[i]["player_id"]:
                    #player_found = 1
            #if player_found == 0:

            #adds the newly drafted player into the user's collection
            db.execute('INSERT into collection(user_id, player_id) VALUES (:id, :random_player)', id=user_id, random_player=random_player[0]["id"])
            return render_template("packs.html", random_player=random_player, points=points, selling_value=selling_value, image=image)

            #else:
                #points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
                #return render_template("packs.html", random_player=0, points=points)
    else:
        return render_template("openpacks.html", points=points)

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == 'GET':
        return redirect("/")
    if request.method == 'POST':
        points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
        #selects all the player's data using the image submitted from the form on home.
        player = db.execute("SELECT * FROM players WHERE image=:img", img=request.form["img"])
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
        db.execute('DELETE FROM collection WHERE player_id=:player_id AND user_id=:user_id ORDER BY RANDOM() LIMIT 1', player_id=player_id, user_id=session['user_id'])
        db.execute('UPDATE users SET cash = ? WHERE id = ?', points, session['user_id'])
        return redirect("/")



@app.route("/sellfrompacks", methods=["GET", "POST"])
@login_required
def sellfrompacks():
    if request.method == 'GET':
        return redirect("/openpacks")
    if request.method == 'POST':
        points = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
        #selects all the player's data using the image submitted from the form on home.
        player = db.execute("SELECT * FROM players WHERE image=:img", img=request.form["img"])
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
        db.execute('DELETE FROM collection WHERE player_id=:player_id AND user_id=:user_id ORDER BY RANDOM() LIMIT 1', player_id=player_id, user_id=session['user_id'])
        db.execute('UPDATE users SET cash = ? WHERE id = ?', points, session['user_id'])
        return redirect("/openpacks")