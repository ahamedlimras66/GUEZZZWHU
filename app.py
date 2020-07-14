from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/sigin")
def login():
    return render_template("sigin.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    app.run(debug=True)