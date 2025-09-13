import { useState } from 'react';
import './App.css';

// The main App component for your frontend
function App() {
  // State variables for managing the UI and data flow
  const [crop, setCrop] = useState('Rice'); // Holds the user's selected crop
  const [soil, setSoil] = useState('Low Nitrogen'); // Holds the user's selected soil condition
  const [location, setLocation] = useState(''); // New state for user's location
  const [weather, setWeather] = useState(''); // New state for user's weather condition
  const [uploadedFile, setUploadedFile] = useState(null); // New state for the uploaded file
  const [recommendation, setRecommendation] = useState(''); // Stores the AI-generated recommendation text
  const [loading, setLoading] = useState(false); // Tracks if an API request is in progress
  const [error, setError] = useState(null); // Stores any error messages that occur

  // Async function to handle the API call to the backend
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevents the form from causing a page reload

    // Reset UI state before starting the new request
    setLoading(true);
    setError(null);
    setRecommendation('');
    
    // Log the request details for debugging
    const url = 'http://localhost:5000/get-recommendation';
    console.log(`Sending request to: ${url}`);

    // Create a data object to be sent as JSON
    const dataToSend = {
      crop,
      soil,
      location,
      weather,
    };
    
    // NOTE: The previous code sent a FormData object which can cause a 415 error.
    // We are now sending a JSON object, which is more reliable for this type of data.
    // The file upload functionality has been removed in this version to simplify the data format.
    try {
      console.log('Sending JSON data:', dataToSend);

      // Use the fetch API to send a POST request with JSON data
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json', // This header tells the server to expect JSON
        },
        body: JSON.stringify(dataToSend), // Convert the data object to a JSON string
      });
      
      console.log(`Response received with status: ${response.status}`);

      // Check for a successful HTTP status code (200-299)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Parse the JSON response from the backend
      const data = await response.json();
      console.log("Received data:", data);

      // Update the recommendation state with the received data
      setRecommendation(data.recommendation);

    } catch (err) {
      // Handle any errors during the fetch process
      console.error("Failed to fetch recommendation:", err);
      setError(`Failed to get recommendation. Please try again. (${err.message})`);
    } finally {
      // This block will always execute, resetting the loading state
      setLoading(false);
    }
  };

  return (
    <>
      <style></style>

      <div className="container">
        <h1>Agri-Advisor MVP</h1>

        {/* The form for user input */}
        <form onSubmit={handleSubmit} className="advisor-form">
          <div className="form-group">
            <label htmlFor="crop-select">Select Crop:</label>
            <select
              id="crop-select"
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
            >
              <option value="Rice">Rice</option>
              <option value="Wheat">Wheat</option>
              <option value="Sugarcane">Sugarcane</option>
              <option value="Cotton">Cotton</option>
              <option value="Maize">Maize</option>
              <option value="Pulses">Pulses</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="soil-select">Select Soil Condition:</label>
            <select
              id="soil-select"
              value={soil}
              onChange={(e) => setSoil(e.target.value)}
            >
              <option value="Low Nitrogen">Low Nitrogen</option>
              <option value="Acidic and Low Phosphorus">Acidic and Low Phosphorus</option>
              <option value="Loamy Soil">Loamy Soil</option>
              <option value="Clayey Soil">Clayey Soil</option>
              <option value="Sandy Soil">Sandy Soil</option>
              <option value="Saline Soil">Saline Soil</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="location-select">Select Location:</label>
            <select
              id="location-select"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            >
              <option value="">Select a city...</option>
              <option value="Delhi">Delhi</option>
              <option value="Mumbai">Mumbai</option>
              <option value="Bengaluru">Bengaluru</option>
              <option value="Hyderabad">Hyderabad</option>
              <option value="Kolkata">Kolkata</option>
              <option value="Jaipur">Jaipur</option>
              <option value="Kanpur">Kanpur</option>
              <option value="Ludhiana">Ludhiana</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="weather-select">Select Weather Condition:</label>
            <select
              id="weather-select"
              value={weather}
              onChange={(e) => setWeather(e.target.value)}
            >
              <option value="">Select a weather condition...</option>
              <option value="Sunny">Sunny</option>
              <option value="Rainy">Rainy</option>
              <option value="Humid">Humid</option>
              <option value="Cold">Cold</option>
              <option value="Dry">Dry</option>
            </select>
          </div>

          <div className="form-group file-upload">
            <label htmlFor="file-upload-input">
              Upload Image or PDF of Report
              <br/>
              <small>Click to select file or drag & drop here</small>
            </label>
            <input
              id="file-upload-input"
              type="file"
              accept="image/*,.pdf"
              onChange={(e) => setUploadedFile(e.target.files[0])}
              hidden
            />
            {uploadedFile && <p style={{marginTop: '10px', fontSize: '0.9rem'}}>Selected file: {uploadedFile.name}</p>}
          </div>

          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Generating Recommendation...' : 'Get Recommendation'}
          </button>
        </form>

        {/* Area to display the recommendation or status messages */}
        <div className="recommendation-output">
          {loading && <p className="loading-message">Generating recommendation, please wait...</p>}
          {error && <p className="error-message">Error: {error}</p>}
          {recommendation && (
            <div className="recommendation-content">
              <h3>Your Personalized Advisory:</h3>
              <pre>{recommendation}</pre> {/* <pre> tag preserves the formatting from the API response */}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App; // Export the component
