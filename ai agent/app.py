"""
REST API wrapper for the Support Ticket Classifier.
Run with: python app.py
"""

from flask import Flask, request, jsonify
from classifier import SupportClassifier

app = Flask(__name__)
classifier = SupportClassifier(api_key="")


@app.route("/classify", methods=["POST"])
def classify():
    data = request.get_json(force=True, silent=True)
    if not data or "messages" not in data:
        return jsonify({"error": "Request body must be JSON with a 'messages' key."}), 400

    messages = data["messages"]
    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "'messages' must be a non-empty list of strings."}), 400

    try:
        results = classifier.classify(messages)
        return jsonify(results), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        return jsonify({"error": f"Classification failed: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
