from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)

tox_model = pickle.load(open("tox_model.pkl", "rb"))
tox_vectorizer = pickle.load(open("tox_vectorizer.pkl", "rb"))

@app.route("/predict_toxic", methods=["POST"])
def predict_toxic():
    data = request.json
    messages = data["messages"]

    X = tox_vectorizer.transform(messages)
    preds = tox_model.predict(X)

    return jsonify({"toxicity": preds.tolist()})

if __name__ == "__main__":
    app.run(port=5001)