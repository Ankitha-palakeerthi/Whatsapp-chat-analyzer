from flask import Flask, request, jsonify
from flask_cors import CORS 
import pickle

app = Flask(__name__)
CORS(app) 

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    messages = data["messages"]

    X = vectorizer.transform(messages)
    predictions = model.predict(X)

    return jsonify({
        "predictions": predictions.tolist()
    })

if __name__ == "__main__":
    app.run(debug=True)