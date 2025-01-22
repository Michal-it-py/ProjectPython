from flask import Flask,request,render_template
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("main.html")

if(__name__)=="__main__":
    app.run(host ='127.0.0.1',port=5001, debug = True)

