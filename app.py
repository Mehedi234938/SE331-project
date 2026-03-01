from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

sections = {
    "A": {"limit": 2, "students": []},
    "B": {"limit": 2, "students": []},
    "C": {"limit": 2, "students": []}
}

@app.route("/enroll", methods=["POST"])
def enroll():
    data = request.json
    name = data["name"]

    for sec in sections:
        if len(sections[sec]["students"]) < sections[sec]["limit"]:
            sections[sec]["students"].append(name)
            return jsonify({"status": "success", "section": sec})

    return jsonify({"status": "full"})


@app.route("/students", methods=["GET"])
def students():
    result = []
    for sec in sections:
        for s in sections[sec]["students"]:
            result.append({"name": s, "section": sec})
    return jsonify(result)


@app.route("/delete", methods=["POST"])
def delete():
    data = request.json
    name = data["name"]

    for sec in sections:
        if name in sections[sec]["students"]:
            sections[sec]["students"].remove(name)
            break

    return jsonify({"status": "deleted"})


if __name__ == "__main__":
    app.run(debug=True)