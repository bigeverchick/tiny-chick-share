from flask import Flask, request, render_template
import os

app = Flask(__name__)

SAVE_DIR = "pic"
TEXT_DIR = "text"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)

TEXT_FILE = os.path.join(TEXT_DIR, "latest.txt")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

    f = request.files["file"]

    f.save(os.path.join(SAVE_DIR, f.filename))

    return "ok"

@app.route("/send_text", methods=["POST"])
def send_text():

    text = request.form["text"]

    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(text)

    return "ok"

@app.route("/get_text")
def get_text():

    if not os.path.exists(TEXT_FILE):
        return ""

    with open(TEXT_FILE, "r", encoding="utf-8") as f:
        return f.read()

app.run(host="0.0.0.0", port=5000)
