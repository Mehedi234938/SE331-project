from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import uuid

app = Flask(__name__)
CORS(app)

# ---------- DB ----------
def db():
    return sqlite3.connect("database.db")

def init():
    conn=db()
    c=conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        uid TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY,
        name TEXT,
        section TEXT
    )
    """)

    conn.commit()
    conn.close()

init()

# ---------- HELPER ----------
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def gen_uid():
    return str(uuid.uuid4())[:8]

# ---------- SIGNUP ----------
@app.route("/signup", methods=["POST"])
def signup():
    data=request.json
    uid=gen_uid()
    password=hash_pass(data["password"])
    role=data["role"]

    conn=db()
    c=conn.cursor()

    c.execute("INSERT INTO users(uid,password,role) VALUES (?,?,?)",
              (uid,password,role))
    conn.commit()
    conn.close()

    return jsonify({"uid":uid})

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data=request.json
    uid=data["uid"]
    password=hash_pass(data["password"])

    conn=db()
    c=conn.cursor()

    c.execute("SELECT role FROM users WHERE uid=? AND password=?", (uid,password))
    user=c.fetchone()
    conn.close()

    if user:
        return jsonify({"status":"ok","role":user[0]})
    return jsonify({"status":"fail"})

# ---------- RESET ----------
@app.route("/reset", methods=["POST"])
def reset():
    data=request.json
    uid=data["uid"]
    new_pass=hash_pass(data["password"])

    conn=db()
    c=conn.cursor()

    c.execute("UPDATE users SET password=? WHERE uid=?", (new_pass,uid))
    conn.commit()
    conn.close()

    return jsonify({"status":"updated"})

# ---------- ENROLL ----------
@app.route("/enroll", methods=["POST"])
def enroll():
    name=request.json["name"]

    conn=db()
    c=conn.cursor()

    for sec in ["A","B","C"]:
        c.execute("SELECT COUNT(*) FROM students WHERE section=?", (sec,))
        if c.fetchone()[0] < 2:
            c.execute("INSERT INTO students(name,section) VALUES (?,?)",(name,sec))
            conn.commit()
            conn.close()
            return jsonify({"section":sec})

    conn.close()
    return jsonify({"section":"Full"})

# ---------- GET ----------
@app.route("/students", methods=["GET"])
def students():
    conn=db()
    c=conn.cursor()
    c.execute("SELECT id,name,section FROM students")

    data=[{"id":r[0],"name":r[1],"section":r[2]} for r in c.fetchall()]
    conn.close()
    return jsonify(data)

# ---------- DELETE ----------
@app.route("/delete/<int:id>", methods=["DELETE"])
def delete(id):
    conn=db()
    c=conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"status":"deleted"})

if __name__ == "__main__":
    app.run(debug=True)
