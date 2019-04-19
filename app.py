# type of entry file
from flask import Flask, render_template

# create instance of Flask class
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("HTML/home.html")



if __name__ == "__main__":
    app.run(debug=True)
