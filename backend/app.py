import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Flask app and enable CORS for all routes
app = Flask(__name__)
CORS(app)

# Configure the Gemini API with your key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# A helper function to create a personalized prompt for the AI
def generate_prompt(crop, soil):
    """
    Crafts a detailed prompt for Gemini based on user inputs.
    """
    return (
        f"You are a helpful agricultural expert for Indian farmers. "
        f"Provide a simple, three-part advisory for a farmer growing {crop} "
        f"in a soil condition of '{soil}'. Use simple language. "
        f"Section 1: **Soil Health** (explain the issue and a simple fix). "
        f"Section 2: **Fertilizer Guidance** (recommend a specific fertilizer like Urea or DAP and the amount in kg/acre). "
        f"Section 3: **General Tip** (a simple tip about farming practice or pests). "
        f"Format your response with the bolded headings. Do not add extra text."
    )

# The main API endpoint that the frontend will call
@app.route('/get-recommendation', methods=['POST'])
def get_recommendation():
    """
    Handles POST requests from the React frontend, gets a recommendation from Gemini, and sends it back.
    """
    data = request.json
    crop = data.get('crop')
    soil = data.get('soil')

    # Basic input validation
    if not all([crop, soil]):
        return jsonify({'error': 'Missing crop or soil information.'}), 400

    # Generate the prompt and get a response from Gemini
    prompt = generate_prompt(crop, soil)
    try:
        response = model.generate_content(prompt)
        recommendation_text = response.text
        return jsonify({'recommendation': recommendation_text})
    except Exception as e:
        # Return an error if the Gemini API call fails
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Run the Flask app on port 5000
if __name__ == '__main__':
    app.run(debug=True, port=5000)
