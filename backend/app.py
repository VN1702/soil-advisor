import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, RecommendationHistory
from soil_analysis import image_processor, pdf_processor, location_fetcher

# Load .env
load_dotenv()

# Configs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_DB = os.getenv("MYSQL_DB")

app = Flask(__name__)
CORS(app)

# Gemini API config
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# MySQL DB config
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# Prompt generator
def generate_detailed_prompt(crop, soil_info, language):
    lang_intro = {
        'en': "You are an expert agricultural advisor for Indian farmers.",
        'hi': "आप भारतीय किसानों के लिए एक कृषि विशेषज्ञ सलाहकार हैं।",
        'kn': "ನೀವು ಭಾರತೀಯ ರೈತರಿಗೆ ಕೃಷಿ ತಜ್ಞ ಸಲಹೆಗಾರರಾಗಿದ್ದೀರಿ।"
    }
    intro_text = lang_intro.get(language, lang_intro['en'])

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

# Get Recommendation API
@app.route('/get-recommendation', methods=['POST'])
def get_recommendation():
    data = request.form
    crop = data.get('crop')
    location = data.get('location')
    language = data.get('language', 'en')
    image_file = request.files.get('soil_image')
    pdf_file = request.files.get('soil_pdf')

    soil_info = None

    if image_file:
        soil_info = image_processor.process(image_file)
    elif pdf_file:
        soil_info = pdf_processor.extract(pdf_file)
    elif location:
        soil_info = location_fetcher.fetch(location)
    else:
        return jsonify({'error': 'No soil input provided.'}), 400

    prompt = generate_detailed_prompt(crop, soil_info, language)

    try:
        response = model.generate_content(prompt)
        recommendation_text = response.text

        history_entry = RecommendationHistory(
            crop=crop,
            soil_info=soil_info,
            recommendation=recommendation_text,
            language=language
        )
        db.session.add(history_entry)
        db.session.commit()

        return jsonify({'recommendation': recommendation_text})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# History API
@app.route('/history', methods=['GET'])
def get_history():
    records = RecommendationHistory.query.order_by(RecommendationHistory.timestamp.desc()).all()
    history = [{
        'id': r.id,
        'crop': r.crop,
        'soil_info': r.soil_info,
        'recommendation': r.recommendation,
        'language': r.language,
        'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for r in records]

    return jsonify({'history': history})

# Run app
if __name__ == '__main__':
    app.run(debug=True, port=5000)
