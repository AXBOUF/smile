from flask import Flask, jsonify, request, render_template
import requests
import json

app = Flask(__name__, template_folder='templates', static_folder='static')

# The backend capture service (runs separately)
CAPTURE_URL = "http://127.0.0.1:5002/capture"   # change if capture runs elsewhere

@app.route('/shopping', methods=['GET', 'POST'])
def shopping():
    if request.method == 'GET':
        return render_template('shopping1.html')

    item = request.form.get('item', '').strip()
    quantity = request.form.get('quantity', '').strip()
    cart_raw = request.form.get('cart')
    if cart_raw:
        try:
            cart_obj = json.loads(cart_raw)
            payload = {"cart": json.dumps(cart_obj["items"])}  # or send the whole cart onward
            resp = requests.post(CAPTURE_URL, data=payload, timeout=20)
            resp.raise_for_status()
            capture_result = resp.json()
            return jsonify({
                "status": "ok",
                "cart": cart_obj,
                "capture": capture_result
            }), 200
        except Exception as e:
            return jsonify({"error": "bad cart", "detail": str(e)}), 400


    if not item or not quantity:
        return jsonify({"error": "All fields required"}), 400

    # Trigger backend capture (no browser camera; POS webcam lives on capture service)
    
    try:
        # You can pass cart metadata along if useful to your capture backend
        payload = {"cart": json.dumps([{"item": item, "quantity": int(quantity)}])}
        resp = requests.post(CAPTURE_URL, data=payload, timeout=15)
        resp.raise_for_status()
        capture_result = resp.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "capture service unreachable", "detail": str(e)}), 502
    except ValueError:
        return jsonify({"error": "invalid JSON from capture service"}), 502

    # Return a clean JSON summary
    return jsonify({
        "status": "ok",
        "cart": [{"item": item, "quantity": int(quantity)}],
        "capture": capture_result
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
