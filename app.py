from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/elements")
def elements():
    return render_template("elements.html")

@app.route("/imgtry")
def imgtry():
    return render_template("imgtry.html")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/sigup")
def sigup():
    return render_template("sigup.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/sample")
def sample():
    return render_template("sample.html")


if __name__ == "__main__":
    app.run(debug=True)