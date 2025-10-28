from flask import Flask, jsonify, request, render_template
import requests, json, os

app = Flask(__name__, template_folder='templates', static_folder='static')

CAPTURE_URL = "http://127.0.0.1:5002/capture"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_FILE = os.path.join(BASE_DIR, 'data', 'db.json')

def load_points():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_points(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/shopping", methods=["GET", "POST"])
def shopping():
    if request.method == "GET":
        return render_template("shopping.html")

    cart_raw = request.form.get("cart", "")
    total = float(request.form.get("cart_total", 0))

    if not cart_raw:
        return jsonify({"error": "No cart received"}), 400

    try:
        cart = json.loads(cart_raw)
    except Exception:
        return jsonify({"error": "Invalid cart JSON"}), 400

    # Send capture trigger
    try:
        payload = {"cart": json.dumps(cart)}
        resp = requests.post(CAPTURE_URL, data=payload, timeout=15)
        resp.raise_for_status()
        capture_result = resp.json()
    except Exception as e:
        return jsonify({"error": "Capture service unreachable", "detail": str(e)}), 502

    person = capture_result.get("person", "Unknown")

    # 🎯 Loyalty logic
    db = load_points()
    user = db.setdefault(person, {"points": 0})

    earned = 5  # base rule
    if total >= 20:
        earned += 20  # bonus rule

    user["points"] += earned
    save_points(db)

    return jsonify({
        "status": "ok",
        "person": person,
        "cart": cart,
        "cart_total": total,
        "earned_points": earned,
        "total_points": user["points"],
        "capture": capture_result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
