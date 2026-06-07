from flask import Flask , render_template, request, jsonify, session
from reg_engine import ask_question
import os
import subprocess
from database import db, ChatMessage
import sys
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024 
ALLOWED_EXTENTIONS = {'pdf'}
UPLOAD_FOLDER = 'data'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENTIONS

def validate_pdf_upload(file):
    errors=[]

    if not file or file.filename == '':
        return {"valid": False, "error": "No file selected"}
    
    if not allowed_file(file.filename):
        return {"valid": False, "error": "Only PDF files allowed. Got: "+
                file.filename.rsplit('.',1)[-1].upper()}
    
    file.seek(0, os.SEEK_END) 
    file_size = file.tell()
    file.seek(0)

    if file_size == 0:
        return{"valid": False, "error": "File is empty"}
    if file_size > MAX_FILE_SIZE:
        return {"valid": False, "error": f"File too large. Max: {MAX_FILE_SIZE/{1024*1024}:.0f} MB"}
    
    return {"valid": True, "error": None}

load_dotenv()

app =Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL','sqlite:///chat_history.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key = os.getenv('SECRET_KEY',"dev-secret-key")
db.init_app(app)
with app .app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    try:
        #Validate input
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message field is required"}), 400
        
        user_message = data['message']
        if not user_message:
            return jsonify({"error": "message cannot be empty"}), 400
        
        if len(user_message) > 500:
            return jsonify({"error": "Message too long (max 5000 chars)"}), 400
        
        #Get response from LLM
        response = ask_question(user_message)

        #Save to database
        chat_message = ChatMessage(user_message=user_message,
                                bot_response=response["answer"],
                                )
        db.session.add(chat_message)
        db.session.commit()
        return jsonify({
            "response": response["answer"],
            "sources": response["sources"]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to process message"}), 500

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if 'pdf' not in request.files:
            logger.warning("Upload request missing 'pdf' field")
            return jsonify({"error": "No 'pdf' file field in request"}), 400
        
        file =request.files["pdf"]
        validation_result = validate_pdf_upload(file)
        if not validation_result['valid']:
            logger.warning(f"Invalid file upload: {validation_result['error']}")
            return jsonify({"error": validation_result['error']}), 400
        
        filename = secure_filename(file.filename)
        save_path =os.path.join(UPLOAD_FOLDER, file.filename)
        
        if os.path.exists(save_path):
            logger.info(f"file already exists: {filename}")
            return jsonify({"message": "PDF uploaded successfully! (File was already in database)"}), 200
    
        try:
            file.save(save_path)
            logger.info(f"file saved: {save_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            return jsonify({"error": "Failed to save file"}), 500
        
        # Trigger the ingestion process
        try:
            subprocess.run([
            sys.executable,'ingest.py',save_path],
            check=True,
            capture_output=True,
            timeout=300
            )
            logger.info(f"Ingestion completed for: {filename}")
        except subprocess.TimeoutExpired:
            logger.error(f"Ingestion timeout for: {filename}")
            return jsonify({"error": "PDF processipn timed out"}), 500
        except subprocess.CalledProcessError as e:
            logger.error(f"Ingestion failed: {e.stderr.decode()}"), 500
        return jsonify({
            "message": "PDF uploaded successfully!",
            "filename": filename
        }), 200 
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == "__main__":
    app.run(debug=True)