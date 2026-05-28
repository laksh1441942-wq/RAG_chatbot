from flask import Flask , render_template, request, jsonify
from reg_engine import ask_question
import os
import subprocess
app =Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']
    response = ask_question(user_message)
    return jsonify({
        "response": response
    })

@app.route("/upload", methods=["POST"])
def upload():
    file =request.files["pdf"]
    save_path =os.path.join("data", file.filename)
    file.save(save_path)
    # Trigger the ingestion process
    subprocess.run(['python', 'ingest.py', save_path])

    return jsonify({
        "message": "PDF uploaded successfully!"
    })

if __name__ == "__main__":
    app.run(debug=True)