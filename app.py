import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import pdfkit


from helpers import apology, login_required, density , descriptopn

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///app.db")

# Make sure API key is set

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




@app.route("/")
def portal():

          return render_template("portal.html")

@app.route("/index")
@login_required
def index():
    """Show portfolio of stocks"""
    if session["user_id"]:


        return render_template("index.html")
    # return render_template("quoted.html")
    else:
        return redirect("/portal")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 404)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password",403 )

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 405)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("index")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/index")





@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    usernames = list(db.execute("SELECT email FROM users"))
    if request.method == "POST":



        for i in usernames:

            if request.form.get("email") == i["email"]:
                return apology("this email is already exist", 400)

        email = request.form.get("email")
        password = generate_password_hash(request.form.get("password"))
        first = request.form.get("firstname")
        last = request.form.get("lastname")
        department = request.form.get("department")
        title = request.form.get("title")
        db.execute("INSERT INTO users (email , hash, first_name, last_name, department, title) VALUES (?,?,?,?,?,?)", email, password, first, last, department, title)
        session["user_id"] = (db.execute("SELECT id FROM users   WHERE email= ?", email))[0]["id"]
       # fill the persinal data

        return redirect("/index")

    else:
        return render_template("register.html")

    # return apology("TODO")



# in case of changing the account data
@app.route("/change", methods=["GET","POST"])
@login_required
def change():
    if request.method == "POST":
        password =  generate_password_hash(request.form.get("password"))
        pass_old = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])[0]["hash"]
        new = request.form.get("new")
        conf = request.form.get("conf")
        updated =  generate_password_hash(new)
        check = check_password_hash(pass_old, request.form.get("password"))
        #return render_template("test.html" , a = password , x = x)
        if not (check):
            return apology("enter password", 403)
        if new != conf:
            return apology("enter same passwords" , 405)
        db.execute("UPDATE users SET hash =? WHERE id = ?", updated , session["user_id"])
        return redirect("/index")
    else:
        return render_template("change.html")
# the completed projects
@app.route("/finished" , methods=["POST" ,"GET"])
@login_required
def finished():
        if request.method =="POST":
            title= db.execute("SELECT title FROM users WHERE id = ?" , session["user_id"])[0]["title"]
            if title == "manager":
                projects=db.execute("SELECT name, location,bh FROM projects WHERE statue=?" , "finished")
                return render_template("finished.html", projects=projects)

            else:
                projects=db.execute("SELECT name FROM projects JOIN people ON projects.id = people.projects_id WHERE people.users_id =? AND statue=?", session["user_id"] ,"finished")

                return render_template("finished.html", projects=projects)
        else:
            return("/index")


# to add new project
@app.route("/new" , methods=["POST","GET"])
@login_required
def new():


     if request.method =="POST":
        list_names=list(db.execute("SELECT name FROM projects"))
        name = request.form.get("name")

        for i in list_names :
            if name == i["name"]:
                return apology("this name is already exist" , 403)

        location = request.form.get("location")
        bh = request.form.get("bh")
        statue = request.form.get("statue")

        db.execute("INSERT INTO projects (name, location, bh) VALUES (?,?,?) ", name, location, bh)
        id = (db.execute("SELECT id FROM projects WHERE name=?", name))[0]["id"]
        db.execute("INSERT INTO people (users_id, projects_id) VALUES (?,?)", session["user_id"], id)
        return redirect("/index")
     else:
          return render_template("new.html")
# the projects in progress
@app.route("/ongoing" , methods=["POST","GET"])
@login_required
def ongoing():



        title= db.execute("SELECT title FROM users WHERE id = ?" , session["user_id"])

        if title == "manager":
            list_names=(db.execute("SELECT name FROM projects"))
            list=[]
            for i in list_names:
                list.append(i['name'])
            return render_template("ongoing.html" ,list = list )

        else:
            list_names =db.execute("SELECT name,location,bh FROM projects JOIN people ON projects.id = people.projects_id WHERE (people.users_id = ?  AND statue = 'onprogress');", session["user_id"])
            list=[]
            count=1
            for i in list_names:
                list.append(i['name'])
            return render_template("ongoing.html" ,list = list_names ,count=count)


#  view and edit the selected  project
@app.route("/project" , methods=["GET" , "POST"])
@login_required
def project():
    if request.method == "POST":
        # SUMMRY
        # NEW BH
        # BH EDIT
        # FINISH
        # DELETE
        name = request.form.get("name")
        logs = db.execute("SELECT bh_no ,id FROM bh WHERE project_id = (SELECT id FROM projects WHERE name =?)" , name )
        finished = db.execute("SELECT COUNT(bh_no) FROM bh WHERE project_id = (SELECT id FROM projects WHERE name =?) AND statue=?" , name , "finished")[0]["COUNT(bh_no)"]
        scope = db.execute("SELECT bh FROM projects WHERE name =?", name )[0]["bh"]
        in_progress = scope - finished
        project_id = db.execute("SELECT id FROM projects WHERE name =? " , name)[0]["id"]
        return render_template("bhs.html" , name = name , logs =logs, in_progress = in_progress , finished = finished , scope = scope , project_id=project_id)
    else:
        return redirect("/ongoing")

# in order to mark a project as finished
@app.route("/finish" , methods=["GET" , "POST"])
@login_required
def finish():
    if request.method == "POST":

        name = request.form.get("name")
        db.execute("UPDATE projects SET statue = ? WHERE name = ?" , "finished" ,  name )

        return redirect("/finished")
    else:
        return redirect("/ongoing")
# edit the log
@app.route("/log" , methods=["POST" , "GET"])
@login_required
def log ():
    bh = request.form.get("name")
    project_id= request.form.get("id")
    return render_template("log.html" , bh =bh ,project_id=project_id)
# delete bh
@app.route("/delete" , methods=["POST" , "GET"])
@login_required
def delete ():
    bh_id = request.form.get("name")
    db.execute("DELETE FROM bh WHERE id =?",bh_id)
    return redirect("/ongoing")


# edit function to make new bh or edit the project info in a selected project
@app.route("/edit" , methods=["POST" , "GET"])
@login_required
def edit ():

    order = request.form.get("Add New Borehole")
    id = request.form.get("name")


    if order =="Add New Borehole":
        return render_template("new_log.html" , id =id)
    else :


        return render_template("edit_project.html" , id = id)
# edit the project info
@app.route("/edit_project" , methods=["POST" , "GET"])
@login_required
def edit_project ():

     if request.method =="POST":
        name = request.form.get("name")
        location = request.form.get("location")
        bh = request.form.get("bh")

        db.execute("UPDATE projects SET location=? , bh=? WHERE id = ? ", location, bh , name)
        return redirect("/index")
     else:
          return render_template("/")

@app.route("/new_log" , methods=["POST" , "GET"])
@login_required
def new_log():
    if request.method=="POST":
        bh_no = request.form.get("bh")
        engineer = request.form.get("engineer")
        notes = request.form.get("notes")
        machine = request.form.get("machine")
        project_id = request.form.get("name")
        db.execute("INSERT INTO bh (bh_no , project_id , machine, notes , engineer) VAlUES (?, ?, ?, ?, ?)", bh_no, project_id,machine, notes, engineer)

        return render_template("log.html" , bh_no=bh_no , project_id = project_id)

    else:
        return redirect("/")


@app.route("/add_soil" , methods=["POST" , "GET"])
@login_required
def add_soil():
    if request.method=="POST":
        bh = request.form.get("bh_no")
        project_id = request.form.get("project")
        sample_no = request.form.get("sample_no")
        sample_type = request.form.get("sample_type")
        depth_from = request.form.get("from")
        depth_to = request.form.get("to")
        n1 = request.form.get("N1")
        n2 = request.form.get("N2")
        n3 = request.form.get("N3")
        density_values = density(n1, n2, n3)
        N = density_values[0]
        density_text = density_values[1]
        recovery = request.form.get("recovery")
        color = request.form.get("color")
        soil_type = str(request.form.get("mainor")) +" "+ str(request.form.get("major"))

        adj = request.form.get("adj")
        additional=request.form.get("additional")
        another = request.form.get("another")
        notes= request.form.get("notes")
        if another == "Ditto" or another =="ditto":
            desc = "Ditto."
        else:
            desc_list=[density_text,str(color), soil_type,   str(adj) , str(additional), str(another)]
            # desc_before = density_text +', ' + str(color) + ', ' + str(mainor) +' ' + str(major) +', ' + str(adj) + ' '+ str(additional) +', ' + str(another) +'.'
            # desc= desc_before.replace("None", "")
            desc = descriptopn(desc_list)

        db.execute("INSERT INTO log (user_id , description , sample_type, sample_no, frm, to_depth, N15, N30, N45, recovery, notes, bh_no ,N) VALUES(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",session["user_id"], desc, sample_type, sample_no, depth_from, depth_to, n1, n2, n3, recovery, notes, bh, N)
        return render_template("log.html",bh =bh , project_id =project_id )




@app.route("/add_rock" , methods=["POST" , "GET"])
@login_required
def add_rock():
    if request.method=="POST":
        bh = request.form.get("bh_no")
        project_id = request.form.get("project")
        sample_no = request.form.get("sample_no")
        sample_type = 'core'
        depth_from = request.form.get("from")
        depth_to = request.form.get("to")
        scr = request.form.get("scr")
        rqd = request.form.get("rqd")
        strength = request.form.get("strength")
        weathering = request.form.get("weathering")
        rock_type = request.form.get("type")
        grain = request.form.get("grain")
        recovery = request.form.get("recovery")
        color = request.form.get("color")
        adj = request.form.get("adj")
        additional=request.form.get("additional")
        another = request.form.get("another")
        notes= request.form.get("notes")
        if another == "Ditto" or another =="ditto":
            desc = "Ditto."
        else:
            desc_list=[str(strength),str(weathering),str(color), str(grain),   str(type) ,str(adj),  str(additional), str(another)]
            # desc_before = density_text +', ' + str(color) + ', ' + str(mainor) +' ' + str(major) +', ' + str(adj) + ' '+ str(additional) +', ' + str(another) +'.'
            # desc= desc_before.replace("None", "")
            desc = descriptopn(desc_list)

        db.execute("INSERT INTO log (user_id , description , sample_type, sample_no, frm, to_depth, N15, N30, N45, recovery, notes, bh_no ,N) VALUES(?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",session["user_id"], desc, sample_type, sample_no, depth_from, depth_to, n1, n2, n3, recovery, notes, bh, N)
        return render_template("log.html",bh =bh , project_id =project_id )





@app.route("/pdf" , methods=["POST" , "GET"])
@login_required
def pdf():

    out = render_template("new_log.html")

            # PDF options
    options = {
                "orientation": "landscape",
                "page-size": "A4",
                "margin-top": "1.0cm",
                "margin-right": "1.0cm",
                "margin-bottom": "1.0cm",
                "margin-left": "1.0cm",
                "encoding": "UTF-8",
            }

            # Build PDF from HTML
    pdf = pdfkit.from_string(out, options=options)

            # Download the PDF
    return Response(pdf, mimetype="application/pdf")
