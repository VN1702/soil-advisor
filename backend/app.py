import os
import urllib.parse
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from models import db, RecommendationHistory
from soil_analysis import image_processor, pdf_processor, location_fetcher

# Load environment variables from .env
load_dotenv()

# MySQL credentials and encoding
MYSQL_USER = os.getenv("MYSQL_USER", "")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_DB = os.getenv("MYSQL_DB", "")

user_enc = urllib.parse.quote_plus(MYSQL_USER)
pass_enc = urllib.parse.quote_plus(MYSQL_PASSWORD)

print(f"Using DB config: {MYSQL_USER}@{MYSQL_HOST}/{MYSQL_DB}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{user_enc}:{pass_enc}@{MYSQL_HOST}/{MYSQL_DB}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)
with app.app_context():
    db.create_all()

# Google Gemini AI initialization with fallback
def init_generate_text():
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        def generate(prompt):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return getattr(response, "text", "")

        return generate
    except Exception:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-pro')

        def generate(prompt):
            response = model.generate_content(prompt)
            return getattr(response, "text", "")

        return generate

generate_text = init_generate_text()

# Prompt generator helper
def generate_detailed_prompt(crop, soil_info, language):
    introductions = {
        "en": "You are an expert agricultural advisor for Indian farmers.",
        "hi": "आप भारतीय किसानों के लिए एक कृषि विशेषज्ञ सलाहकार हैं।",
        "kn": "ನೀವು ಭಾರತೀಯ ರೈತರಿಗೆ ಕೃಷಿ ತಜ್ಞ ಸಲಹೆಗಾರರಾಗಿದ್ದೀರಿ।"
    }
    intro_text = introductions.get(language, introductions["en"])
    return (
        f"{intro_text}\n"
        f"The farmer wants to grow {crop}. Soil analysis info:\n"
        f"{soil_info}\n\n"
        f"Provide:\n"
        f"1. Chemical fertilizer recommendations.\n"
        f"2. Pretreatment steps.\n"
        f"3. Local organic solutions.\n"
        f"Use simple language."
    )

# Clean up DB session after each request
@app.teardown_request
def teardown_request(exception=None):
    try:
        if exception:
            db.session.rollback()
    finally:
        db.session.remove()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

# API endpoint
@app.route("/get-recommendation", methods=["POST"])
def get_recommendation():
    data = request.form
    crop = data.get("crop")
    location = data.get("location")
    language = data.get("language", "en")
    image_file = request.files.get("soil_image")
    pdf_file = request.files.get("soil_pdf")

    if not crop:
        return jsonify({"error": "Crop is required."}), 400

    soil_info = None
    if image_file:
        soil_info = image_processor.process(image_file)
    elif pdf_file:
        soil_info = pdf_processor.extract(pdf_file)
    elif location:
        soil_info = location_fetcher.fetch(location)
    else:
        return jsonify({"error": "Provide soil image, PDF, or location."}), 400

    prompt = generate_detailed_prompt(crop, soil_info, language)

    try:
        recommendation_text = generate_text(prompt)
        history_entry = RecommendationHistory(
            crop=crop,
            soil_info=soil_info,
            recommendation=recommendation_text,
            language=language
        )
        db.session.add(history_entry)
        db.session.commit()

        return jsonify({
            "recommendation": recommendation_text,
            "id": history_entry.id,
            "language": language
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
