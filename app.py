# type of entry file
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from data import articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt   #-> For encrypting password
from functools import wraps

# create instance of Flask class
app = Flask(__name__)

# Config MySQL
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Dunno11pass"
app.config["MYSQL_DB"] = "myflaskapp"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"   # For calling methods to execute queries

# initialize MySQl - now we can create a cursor and execute queries
mysql = MySQL(app)

Articles = articles()

#GetReguest which goes to a page and loads it
@app.route("/")
def index():
    return render_template("home.html")

# Index
@app.route("/about")
def about():
    return render_template("about.html")

# Articles
@app.route("/articles")
def articles():
    return render_template("articles.html", articles=Articles)

# Single Article
@app.route("/article/<string:id>/")
def article(id):
    return render_template("article.html", id=id)

# Register Form Class
class RegisterForm(Form):
    name = StringField("Name", [validators.Length(min=1, max=50)])
    username = StringField("Username", [validators.Length(min=4, max=25)])
    email = StringField("Email", [validators.Length(min=6, max=50)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirm", message="Passwords do not match")
    ])
    confirm = PasswordField("Confirm Password")

#PostRequest and GetReguest - User Register
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        passsword = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor
        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO users(name, email, username, password) "
                    "VALUES(%s, %s, %s, %s)",
                    (name, email, username, passsword))

        # Commit to database
        mysql.connection.commit()

        # Close database connection
        cur.close()

        flash("You are now registered and can log in", "success")

        return redirect(url_for("login"))

    # Pass form value with template
    return render_template("register.html", form=form)

# User login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get Form fields
        username = request.form["username"]
        password_candidate = request.form["password"]

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username passed through the form
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash - looks into query and matches first one it finds
            data = cur.fetchone()
            password = data["password"]

            # Compare passwords

            if sha256_crypt.verify(password_candidate, password):
                # Passed login
                session["logged_in"] = True
                session["username"] = username

                flash("You are now logged in", "success")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid login"
                return render_template("login.html", error=error)
            # Close connection
            cur.close()
        else:
            error = "Username not found"
            return render_template("login.html", error=error)

    return render_template("login.html")


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, Pleease log in", "danger")
            return redirect(url_for("login"))
    return wrap


# Logout
@app.route("/logout")
def logout():
    session.clear()     # Kills the session that is currently running
    flash("You are now logged out", "success")
    return redirect(url_for("login"))


# Dashboard
@app.route("/dashboard")
@is_logged_in
def dashboard():
    return render_template("dashboard.html")




if __name__ == "__main__":
    app.secret_key="secret123"
    app.run(debug=True)
