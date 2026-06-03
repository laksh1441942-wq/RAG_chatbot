from flask import Flask , render_template, request, jsonify, session
from reg_engine import ask_question
import os
import subprocess
from database import db, ChatMessage

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)
with app .app_context():
    db.create_all()

app.secret_key = "secret_key_for_session_management"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data['message']
    response = ask_question(user_message)

    chat_message = ChatMessage(user_message=user_message,
                              bot_response=response["answer"],
                              )
    db.session.add(chat_message)
    db.session.commit()
    return jsonify({
        "response": response["answer"],
        "sources": response["sources"]
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

@app.route("/history", methods=["GET"])
def history():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.desc()).all()
    return jsonify([message.to_dict() for message in messages])

@app.route("/clear-history",methods=['POST'])
def clear_history():
    ChatMessage.query.delete()
    db.session.commit()
    return jsonify({
        "message": "Chat history cleared successfully!"
    })

if __name__ == "__main__":
    app.run(debug=True)