from flask import Flask, render_template, request, session, logging, url_for, redirect, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from pprint import pprint
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy

#creating connection

#local connection
# engine = create_engine("mysql+pymysql://root@localhost/signup", pool_pre_ping=True)

#heroku connection
engine = create_engine("mysql+pymysql://b77e84f6bd937c:cc695d3a@us-cdbr-east-02.cleardb.com/heroku_ce45a510ac0de22", pool_pre_ping=True)

db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)

app.secret_key="1234567notetaking"

@app.route("/")
def index():
    return render_template("index.html")
  
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/app")
def application():
    return render_template("application.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        secure_password = sha256_crypt.encrypt(str(password))
        
        if password == confirm:
            db.execute("INSERT INTO users(name, username, password) VALUES(:name, :username,:password)",
            {"name":name, "username":username,"password":password}) 
           
            db.commit()
            flash("you are registered and can login","success")
            return redirect(url_for('login'))
        else:
            flash("Password does not match","danger")
            return render_template("signup.html")

    return render_template("signup.html")

@app.route("/login", methods = ['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        usernamedata = db.execute("SELECT username FROM users WHERE username=:username",{"username":username}).fetchone()
        passworddata = db.execute("SELECT password FROM users WHERE username=:username",{"username":username}).fetchone()


        if usernamedata is None:
            flash("No username","danger")
            return render_template("login.html")
        else:
            for password_data in passworddata:
                # if sha256_crypt.verify(password, password_data):
                if password in password_data:
                    session['userLoggedIn'] = username
                    session["log"] = True
                    flash("You are now logged in", "success")
                    return redirect(url_for('userpage'))
                else: 
                    flash("incorrect password","danger")
                    return render_template("login.html")

    return render_template("login.html")

@app.route("/userpage")
def userpage():
    username = session['userLoggedIn']
    resultproxy = db.execute("SELECT * FROM notes WHERE username=:username",{"username":username})

    html_content = []

    print("ALL NOTES")
    for row in resultproxy:
        html_content.append(row)
            
    return render_template("userpage.html", html_content = html_content)

@app.route("/newnote", methods = ['GET','POST'])
def newnote():
    if request.method == "POST":
        title = request.form.get("title")
        timestamp = request.form.get("date")
        note = request.form.get("note")
        username = session['userLoggedIn']

        db.execute("INSERT INTO notes(title,timestamp, note, username) VALUES(:title, :timestamp, :note, :username)",
        {"title":title, "timestamp":timestamp, "note":note, "username": username})
        db.commit()

        flash("Your note is created","success")

    return render_template("newnote.html")

@app.route("/<note_id>/editnote", methods = ['GET','POST'])
def editnote(note_id):

    if request.method == "POST":
        title = request.form.get("title")
        timestamp = request.form.get("date")
        note = request.form.get("note")
        username = session['userLoggedIn']

        print(note_id)

        db.execute("UPDATE notes SET title = :title, timestamp = :timestamp, note= :note, id= :1",
        {"title":title, "timestamp":timestamp, "note":note, "id":1})
    
        db.commit()

        flash("Your note is updated","success")

    return render_template("newnote.html")
@app.route("/logout")
def logout():
    session.clear()
    flash("You are now logged out", "success")
    return  redirect(url_for('login'))
  
@app.route("/terms")
def terms():
    return render_template("terms.html")

if __name__ == "__main__":
    app.run(debug=True)