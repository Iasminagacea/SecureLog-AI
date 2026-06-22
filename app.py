import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configure MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "securelog_db")

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client[MONGO_DB_NAME]
    reports_collection = db["reports"]
    # Check connection
    mongo_client.server_info()
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Warning: Could not connect to MongoDB: {e}")
    reports_collection = None

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("Warning: GEMINI_API_KEY is not set. The analysis endpoint will fail until it is provided.")

@app.route("/health", methods=["GET"])
def health():
    mongo_status = "Connected" if reports_collection is not None else "Disconnected"
    gemini_status = "Configured" if GEMINI_API_KEY else "Not Configured"
    return jsonify({
        "status": "healthy",
        "mongodb": mongo_status,
        "gemini": gemini_status,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route("/analyze", methods=["POST"])
def analyze_logs():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API Key is not configured. Please set GEMINI_API_KEY in the environment."}), 500

    # Obtain logs content from either a file upload or direct JSON body
    logs_content = ""
    
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty file uploaded"}), 400
        try:
            logs_content = file.read().decode("utf-8")
        except Exception as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 400
    elif request.is_json:
        try:
            logs_content = json.dumps(request.json, indent=2)
        except Exception as e:
            return jsonify({"error": f"Failed to parse JSON body: {str(e)}"}), 400
    else:
        # Fallback to raw text body if provided
        logs_content = request.data.decode("utf-8")

    if not logs_content.strip():
        return jsonify({"error": "No logs provided. Please send JSON body or upload a logs file."}), 400

    # Prepare prompt engineering for security analysis
    system_prompt = (
        "Ești un expert în securitate cibernetică. Analizează următoarele log-uri și spune-mi dacă există "
        "suspiciuni de atac (de tip Brute Force, SQL Injection, Cross-Site Scripting (XSS), Unauthorized Access etc.). "
        "Oferă un raport în format JSON cu nivelul de risc (Low/Medium/High) și pașii de rezolvare."
    )
    
    user_prompt = f"Aici sunt log-urile pe care trebuie să le analizezi:\n\n{logs_content}"

    try:
        # Use gemini-2.5-flash which is fast, cost-effective and supports structured JSON outputs
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash", 
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Call Gemini API
        response = model.generate_content(
            contents=[system_prompt, user_prompt]
        )
        
        # Parse the JSON response from Gemini
        analysis_result = json.loads(response.text)
        
        # Handle cases where the model returns a list instead of a dictionary
        if isinstance(analysis_result, list):
            risk_level = "Unknown"
            for item in analysis_result:
                if isinstance(item, dict):
                    temp_risk = item.get("risk_level", item.get("risc", "Unknown"))
                    if temp_risk != "Unknown":
                        risk_level = temp_risk
                        break
            analysis_result = {
                "risk_level": risk_level,
                "analysis_details": analysis_result
            }
        
        # Prepare document to store in MongoDB
        report_document = {
            "timestamp": datetime.utcnow(),
            "risk_level": analysis_result.get("risk_level", analysis_result.get("risc", "Unknown")),
            "analysis": analysis_result,
            "raw_logs_preview": logs_content[:1000] # Save a preview of logs to prevent db overflow
        }
        
        # Store in MongoDB if connected
        inserted_id = None
        if reports_collection is not None:
            result = reports_collection.insert_one(report_document)
            inserted_id = str(result.inserted_id)
            analysis_result["report_id"] = inserted_id
        else:
            analysis_result["warning"] = "Report was not saved because MongoDB is unavailable."
            
        return jsonify(analysis_result), 200

    except json.JSONDecodeError as je:
        return jsonify({
            "error": "Failed to parse Gemini response as JSON",
            "details": str(je),
            "raw_response": response.text if 'response' in locals() else None
        }), 500
    except Exception as e:
        # Check if it's a quota / rate limit error
        error_msg = str(e)
        if "429" in error_msg or "Quota exceeded" in error_msg or "ResourceExhausted" in error_msg:
            return jsonify({
                "error": "Rate limit exceeded / Quota exceeded",
                "details": "You have exceeded the Gemini API free tier rate limits (typically 5 requests per minute). Please wait a moment before trying again.",
                "original_error": error_msg
            }), 429
        return jsonify({"error": "An error occurred during log analysis", "details": error_msg}), 500

@app.route("/reports", methods=["GET"])
def get_reports():
    if reports_collection is None:
        return jsonify({"error": "MongoDB is not available."}), 500
        
    try:
        # Retrieve latest 20 reports
        reports = list(reports_collection.find().sort("timestamp", -1).limit(20))
        for r in reports:
            r["_id"] = str(r["_id"])
            if "timestamp" in r:
                r["timestamp"] = r["timestamp"].isoformat()
        return jsonify(reports), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch reports", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Run host 0.0.0.0 to expose it from the Docker container
    app.run(host="0.0.0.0", port=port, debug=True)
