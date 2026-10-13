import os, io, json, sqlite3, random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(APP_DIR, "frontend")
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
DB_PATH = os.path.join(APP_DIR, "predictions.db")
MODEL_PATH = os.path.join(APP_DIR, "model.keras")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
CLASSES = ["Plastic", "Paper", "Cardboard", "Glass", "Metal", "Organic Waste", "Trash"]
MODEL = None
MODEL_STATUS = "Demo mode — add a trained model.keras file to enable CNN inference."
try:
    import tensorflow as tf
    if os.path.exists(MODEL_PATH):
        MODEL = tf.keras.models.load_model(MODEL_PATH)
        MODEL_STATUS = "CNN model loaded from model.keras"
except Exception:
    MODEL_STATUS = "Demo mode — TensorFlow/model not available; demo predictions are used."

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT, category TEXT, confidence REAL, created_at TEXT, mode TEXT
    )""")
    con.commit()
    return con

def predict_image(image):
    if MODEL is not None:
        import numpy as np
        image = image.convert("RGB").resize((224, 224))
        arr = np.asarray(image, dtype="float32") / 255.0
        probs = MODEL.predict(arr[None, ...], verbose=0)[0]
        idx = int(probs.argmax())
        return CLASSES[idx], float(probs[idx]), "CNN model"
    # Deterministic demo mode so the interface works without a trained model.
    # This is a placeholder and is NOT a real machine-learning prediction.
    seed = int(image.size[0] * 31 + image.size[1] * 17 + image.convert("RGB").getpixel((0, 0))[0])
    rng = random.Random(seed)
    idx = rng.randrange(len(CLASSES))
    return CLASSES[idx], round(rng.uniform(0.78, 0.97), 3), "Demo simulation"

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/status")
def status():
    return jsonify({"ok": True, "model_loaded": MODEL is not None, "model_status": MODEL_STATUS, "classes": CLASSES})

@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Please choose an image first."}), 400
    f = request.files["image"]
    if not f.filename:
        return jsonify({"error": "Please choose an image first."}), 400
    try:
        image = Image.open(f.stream).convert("RGB")
        filename = os.path.basename(f.filename).replace(" ", "_")
        category, confidence, mode = predict_image(image)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con = db()
        con.execute("INSERT INTO predictions(filename, category, confidence, created_at, mode) VALUES(?,?,?,?,?)",
                    (filename, category, confidence, stamp, mode))
        con.commit()
        con.close()
        return jsonify({"category": category, "confidence": confidence, "confidence_percent": round(confidence*100, 1),
                        "mode": mode, "timestamp": stamp, "tip": recycle_tip(category)})
    except Exception:
        return jsonify({"error": "That file could not be read as an image. Please try JPG, PNG or WEBP."}), 400

def recycle_tip(category):
    tips = {
        "Plastic": "Rinse the container and check local recycling symbols before placing it in the recycling bin.",
        "Paper": "Keep paper clean and dry; greasy or wet paper may not be recyclable.",
        "Cardboard": "Flatten cardboard boxes and keep them dry before recycling.",
        "Glass": "Empty and rinse glass containers. Handle broken glass carefully.",
        "Metal": "Empty metal cans and rinse away food residue where practical.",
        "Organic Waste": "Place food scraps in a compost or organic-waste collection stream if available.",
        "Trash": "Check local disposal guidance; this item may not fit common recyclable categories."
    }
    return tips.get(category, "Check your local recycling guidance.")

@app.route("/api/history")
def history():
    con = db()
    rows = con.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 30").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    con = db()
    con.execute("DELETE FROM predictions")
    con.commit()
    con.close()
    return jsonify({"ok": True, "message": "Prediction history cleared."})

@app.route("/api/dataset")
def dataset():
    # Project's seven labels, based on the presentation. Counts are intentionally
    # not fabricated; user can replace them with actual dataset counts.
    return jsonify([{"name": c, "images": "Add dataset count", "description": d} for c, d in zip(CLASSES, [
        "Bottles, wrappers and other plastic items", "Sheets, newspapers and clean paper",
        "Packaging boxes and corrugated board", "Bottles and jars made of glass",
        "Cans and other metal packaging", "Food scraps and biodegradable waste", "Mixed or non-recyclable waste"
    ])])

@app.route("/api/model-info")
def model_info():
    return jsonify({"architecture": "CNN / Transfer Learning", "input_size": "224 × 224 RGB",
                    "output_classes": CLASSES, "model_file": "model.keras", "status": MODEL_STATUS,
                    "note": "A real prediction requires a trained model whose output order matches the seven classes listed in this app."})

@app.errorhandler(413)
def too_large(_):
    return jsonify({"error": "Image is too large. Please upload an image smaller than 12 MB."}), 413

if __name__ == "__main__":
    db()
    app.run(host="127.0.0.1", port=5000, debug=True)
