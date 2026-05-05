from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import pandas as pd
import json
import re
from flask import render_template
#from reportlab.pdfgen import canvas
#from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# -------------------------
# MONGODB CONNECTION
# -------------------------
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import pandas as pd
import json
import re
from flask import render_template
#from reportlab.pdfgen import canvas
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# -------------------------
# MONGODB CONNECTION
# -------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["whatsapp_chat_analyzer"]
collection = db["analyses"]

# -------------------------
# SAVE ANALYSIS
# -------------------------


@app.route('/save_analysis', methods=['POST'])
def save_analysis():
    data = request.json

    user = data.get("user")
    file_name = data.get("file_name")
    result = data.get("result")
    print(data)
    collection.insert_one({
        "user": user,
        "file_name": file_name,
        "result": result,
        "created_at": datetime.now()
    })

    return jsonify({"success": True})

# -------------------------
# GET HISTORY
# -------------------------


@app.route('/get_analysis', methods=['GET'])
def get_analysis():
    user = request.args.get("user")
    print("USER FROM REQUEST:", user)
    records = collection.find({"user": user}).sort("created_at", -1)

    data = []
    for r in records:
        data.append({
            "id": str(r["_id"]),
            "file_name": r["file_name"],
            "result": r["result"],
            "created_at": r["created_at"].strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(data)

# -------------------------
# RUN SERVER
# -------------------------


if __name__ == '__main__':
    app.run(debug=True)
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"txt", "zip", "csv", "json", "pdf", "docx"}

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# ---------------- DATABASE ---------------- #


def connect_db():
    return sqlite3.connect("database.db")


def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        file_name TEXT,
        total_messages INTEGER,
        total_words INTEGER,
        media_messages INTEGER,
        links_shared INTEGER
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# ---------------- HELPER FUNCTIONS ---------------- #


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

"""


def extract_text(filepath):

    ext = filepath.split(".")[-1]
    text=""

    if ext=="txt":
        with open(filepath,"r",encoding="utf-8") as f:
            text=f.read()

    elif ext=="csv":
        df=pd.read_csv(filepath)
        text=" ".join(df.astype(str).values.flatten())

    elif ext=="json":
        with open(filepath) as f:
            data=json.load(f)
            text=str(data)

    elif ext=="docx":
        doc=Document(filepath)
        for para in doc.paragraphs:
            text+=para.text

    elif ext=="pdf":
        text="PDF uploaded successfully"

    elif ext=="zip":
        text="ZIP uploaded successfully"

    return text
"""


def extract_text(filepath):
    ext = filepath.split(".")[-1].lower()
    text = ""

    try:
        # ✅ TXT
        if ext == "txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        # ✅ CSV
        elif ext == "csv":
            df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")
            text = " ".join(df.astype(str).values.flatten())

        # ✅ JSON
        elif ext == "json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                text = json.dumps(data)

        # ✅ DOCX
        elif ext == "docx":
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])

        # ✅ PDF (REAL FIX)
        elif ext == "pdf":
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                for page in reader.pages:
                    if page.extract_text():
                        text += page.extract_text()
            except:
                text = "PDF text extraction failed"

        # ✅ ZIP (REAL FIX)
        elif ext == "zip":
            import zipfile

            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(app.config["UPLOAD_FOLDER"])

            for file in os.listdir(app.config["UPLOAD_FOLDER"]):
                if file.endswith(".txt"):
                    with open(os.path.join(app.config["UPLOAD_FOLDER"], file), "r", encoding="utf-8", errors="ignore") as f:
                        text += f.read()

        else:
            text = "Unsupported file"

    except Exception as e:
        print("❌ Error reading file:", e)
        text = ""

    return text


def analyze_chat(chat_text):

    messages = chat_text.split("\n")
    users = []
    msgs = []

    for message in messages:
        entry = re.split(r" - ", message)

        if len(entry) > 1:
            user_msg = entry[1]
            user = user_msg.split(":")[0]
            msg = ":".join(user_msg.split(":")[1:])

            users.append(user)
            msgs.append(msg)

    df = pd.DataFrame({"user": users, "message": msgs})

    total_messages = df.shape[0]
    total_words = sum(df["message"].apply(lambda x: len(x.split())))
    media_mes = df[df["message"].str.contains("omitted", case=False)]
    media_messages = media_mes.shape[0]
    links_shared = df["message"].str.contains("http").sum()

    return total_messages, total_words, media_messages, links_shared


def generate_pdf(file_name, stats):

    pdf = canvas.Canvas("report.pdf")

    pdf.drawString(100, 750, "WhatsApp Chat Analysis Report")
    pdf.drawString(100, 720, f"File Name: {file_name}")

    pdf.drawString(100, 680, f"Total Messages: {stats[0]}")
    pdf.drawString(100, 660, f"Total Words: {stats[1]}")
    pdf.drawString(100, 640, f"Media Messages: {stats[2]}")
    pdf.drawString(100, 620, f"Links Shared: {stats[3]}")

    pdf.save()

    return "report.pdf"

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("miniproject.html")


# ---------- SIGNUP ---------- #

@app.route("/register",methods=["POST"])
def register():

    data=request.json

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(
        "INSERT INTO users(username,email,password) VALUES(?,?,?)",
        (data["username"],data["email"],data["password"])
    )

    conn.commit()
    conn.close()

    return jsonify({"message":"User registered successfully"})


# ---------- LOGIN ---------- #

@app.route("/login",methods=["POST"])
def login():

    data=request.json

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data["email"],data["password"])
    )

    user=cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"message":"Login successful","user_id":user[0]})
    else:
        return jsonify({"message":"Invalid credentials"})


# ---------- FILE UPLOAD ---------- #

@app.route("/upload_chat", methods=["POST"])
def upload_chat():

    if "file" not in request.files:
        return jsonify({"error":"No file uploaded"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error":"No file selected"})

    if file and allowed_file(file.filename):

        filepath = os.path.join(app.config["UPLOAD_FOLDER"],file.filename)
        file.save(filepath)

        chat_text = extract_text(filepath)

        return jsonify({
            "message":"File uploaded successfully",
            "chat":chat_text
        })

    return jsonify({"error": "Unsupported file type"})


# ---------- ANALYZE CHAT ---------- #

@app.route("/analyze",methods=["POST"])
def analyze():

    data = request.json
    chat = data["chat"]
    user_id = data["user_id"]
    file_name = data["file_name"]

    stats = analyze_chat(chat)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO analysis(user_id,file_name,total_messages,total_words,media_messages,links_shared)
    VALUES(?,?,?,?,?,?)
    """, (user_id, file_name, stats[0], stats[1], stats[2], stats[3]))

    conn.commit()
    conn.close()

    result=[
        {"name":"Total Messages","value":stats[0]},
        {"name":"Total Words","value":stats[1]},
        {"name":"Media Messages","value":stats[2]},
        {"name":"Links Shared","value":stats[3]}
    ]

    return jsonify(result)


# ---------- DASHBOARD HISTORY ---------- #

@app.route("/history/<user_id>")
def history(user_id):

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM analysis WHERE user_id=?",
        (user_id,)
    )

    data=cursor.fetchall()
    conn.close()

    return jsonify(data)


# ---------- PDF REPORT ---------- #

@app.route("/download_report",methods=["POST"])
def download_report():

    data=request.json

    stats=(
        data["messages"],
        data["words"],
        data["media"],
        data["links"]
    )

    file=generate_pdf(data["file_name"],stats)

    return jsonify({"file":file})


# ---------------- RUN SERVER ---------------- #

if __name__=="__main__":
    app.run(debug=True)


# -------------------------
# SAVE ANALYSIS
# -------------------------


@app.route('/save_analysis', methods=['POST'])
def save_analysis():
    data = request.json

    user = data.get("user")
    file_name = data.get("file_name")
    result = data.get("result")
    print(data)
    collection.insert_one({
        "user": user,
        "file_name": file_name,
        "result": result,
        "created_at": datetime.now()
    })

    return jsonify({"success": True})

# -------------------------
# GET HISTORY
# -------------------------


@app.route('/get_analysis', methods=['GET'])
def get_analysis():
    user = request.args.get("user")
    print("USER FROM REQUEST:", user)
    records = collection.find({"user": user}).sort("created_at", -1)

    data = []
    for r in records:
        data.append({
            "id": str(r["_id"]),
            "file_name": r["file_name"],
            "result": r["result"],
            "created_at": r["created_at"].strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(data)

# -------------------------
# RUN SERVER
# -------------------------


if __name__ == '__main__':
    app.run(debug=True)
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"txt", "zip", "csv", "json", "pdf", "docx"}

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# ---------------- DATABASE ---------------- #


def connect_db():
    return sqlite3.connect("database.db")


def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        file_name TEXT,
        total_messages INTEGER,
        total_words INTEGER,
        media_messages INTEGER,
        links_shared INTEGER
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# ---------------- HELPER FUNCTIONS ---------------- #


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

"""


def extract_text(filepath):

    ext = filepath.split(".")[-1]
    text=""

    if ext=="txt":
        with open(filepath,"r",encoding="utf-8") as f:
            text=f.read()

    elif ext=="csv":
        df=pd.read_csv(filepath)
        text=" ".join(df.astype(str).values.flatten())

    elif ext=="json":
        with open(filepath) as f:
            data=json.load(f)
            text=str(data)

    elif ext=="docx":
        doc=Document(filepath)
        for para in doc.paragraphs:
            text+=para.text

    elif ext=="pdf":
        text="PDF uploaded successfully"

    elif ext=="zip":
        text="ZIP uploaded successfully"

    return text
"""


def extract_text(filepath):
    ext = filepath.split(".")[-1].lower()
    text = ""

    try:
        # ✅ TXT
        if ext == "txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        # ✅ CSV
        elif ext == "csv":
            df = pd.read_csv(filepath, encoding="utf-8", on_bad_lines="skip")
            text = " ".join(df.astype(str).values.flatten())

        # ✅ JSON
        elif ext == "json":
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                text = json.dumps(data)

        # ✅ DOCX
        elif ext == "docx":
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])

        # ✅ PDF (REAL FIX)
        elif ext == "pdf":
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                for page in reader.pages:
                    if page.extract_text():
                        text += page.extract_text()
            except:
                text = "PDF text extraction failed"

        # ✅ ZIP (REAL FIX)
        elif ext == "zip":
            import zipfile

            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(app.config["UPLOAD_FOLDER"])

            for file in os.listdir(app.config["UPLOAD_FOLDER"]):
                if file.endswith(".txt"):
                    with open(os.path.join(app.config["UPLOAD_FOLDER"], file), "r", encoding="utf-8", errors="ignore") as f:
                        text += f.read()

        else:
            text = "Unsupported file"

    except Exception as e:
        print("❌ Error reading file:", e)
        text = ""

    return text


def analyze_chat(chat_text):

    messages = chat_text.split("\n")
    users = []
    msgs = []

    for message in messages:
        entry = re.split(r" - ", message)

        if len(entry) > 1:
            user_msg = entry[1]
            user = user_msg.split(":")[0]
            msg = ":".join(user_msg.split(":")[1:])

            users.append(user)
            msgs.append(msg)

    df = pd.DataFrame({"user": users, "message": msgs})

    total_messages = df.shape[0]
    total_words = sum(df["message"].apply(lambda x: len(x.split())))
    media_mes = df[df["message"].str.contains("omitted", case=False)]
    media_messages = media_mes.shape[0]
    links_shared = df["message"].str.contains("http").sum()

    return total_messages, total_words, media_messages, links_shared


def generate_pdf(file_name, stats):

    pdf = canvas.Canvas("report.pdf")

    pdf.drawString(100, 750, "WhatsApp Chat Analysis Report")
    pdf.drawString(100, 720, f"File Name: {file_name}")

    pdf.drawString(100, 680, f"Total Messages: {stats[0]}")
    pdf.drawString(100, 660, f"Total Words: {stats[1]}")
    pdf.drawString(100, 640, f"Media Messages: {stats[2]}")
    pdf.drawString(100, 620, f"Links Shared: {stats[3]}")

    pdf.save()

    return "report.pdf"

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template("miniproject.html")


# ---------- SIGNUP ---------- #

@app.route("/register",methods=["POST"])
def register():

    data=request.json

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(
        "INSERT INTO users(username,email,password) VALUES(?,?,?)",
        (data["username"],data["email"],data["password"])
    )

    conn.commit()
    conn.close()

    return jsonify({"message":"User registered successfully"})


# ---------- LOGIN ---------- #

@app.route("/login",methods=["POST"])
def login():

    data=request.json

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data["email"],data["password"])
    )

    user=cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"message":"Login successful","user_id":user[0]})
    else:
        return jsonify({"message":"Invalid credentials"})


# ---------- FILE UPLOAD ---------- #

@app.route("/upload_chat", methods=["POST"])
def upload_chat():

    if "file" not in request.files:
        return jsonify({"error":"No file uploaded"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error":"No file selected"})

    if file and allowed_file(file.filename):

        filepath = os.path.join(app.config["UPLOAD_FOLDER"],file.filename)
        file.save(filepath)

        chat_text = extract_text(filepath)

        return jsonify({
            "message":"File uploaded successfully",
            "chat":chat_text
        })

    return jsonify({"error": "Unsupported file type"})


# ---------- ANALYZE CHAT ---------- #

@app.route("/analyze",methods=["POST"])
def analyze():

    data = request.json
    chat = data["chat"]
    user_id = data["user_id"]
    file_name = data["file_name"]

    stats = analyze_chat(chat)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO analysis(user_id,file_name,total_messages,total_words,media_messages,links_shared)
    VALUES(?,?,?,?,?,?)
    """, (user_id, file_name, stats[0], stats[1], stats[2], stats[3]))

    conn.commit()
    conn.close()

    result=[
        {"name":"Total Messages","value":stats[0]},
        {"name":"Total Words","value":stats[1]},
        {"name":"Media Messages","value":stats[2]},
        {"name":"Links Shared","value":stats[3]}
    ]

    return jsonify(result)


# ---------- DASHBOARD HISTORY ---------- #

@app.route("/history/<user_id>")
def history(user_id):

    conn=connect_db()
    cursor=conn.cursor()

    cursor.execute(
        "SELECT * FROM analysis WHERE user_id=?",
        (user_id,)
    )

    data=cursor.fetchall()
    conn.close()

    return jsonify(data)


# ---------- PDF REPORT ---------- #

@app.route("/download_report",methods=["POST"])
def download_report():

    data=request.json

    stats=(
        data["messages"],
        data["words"],
        data["media"],
        data["links"]
    )

    file=generate_pdf(data["file_name"],stats)

    return jsonify({"file":file})


# ---------------- RUN SERVER ---------------- #

if __name__=="__main__":
    app.run(debug=True)
