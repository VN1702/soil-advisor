import { useState } from 'react';

// The main App component for your frontend
function App() {
  // State variables for managing the UI and data flow
  const [crop, setCrop] = useState('Rice'); // Holds the user's selected crop
  const [soil, setSoil] = useState('Low Nitrogen'); // Holds the user's selected soil condition
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

    try {
      // Use the fetch API to send a POST request to the backend
      const response = await fetch('http://localhost:5000/get-recommendation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ crop, soil }), // Send the selected crop and soil as a JSON payload
      });

      // Check for a successful HTTP status code (200-299)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Parse the JSON response from the backend
      const data = await response.json();
      
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
              {/* Add more crop options as needed */}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="soil-select">Simulated Soil Condition:</label>
            <select 
              id="soil-select" 
              value={soil} 
              onChange={(e) => setSoil(e.target.value)}
            >
              <option value="Low Nitrogen">Low Nitrogen</option>
              <option value="Acidic and Low Phosphorus">Acidic and Low Phosphorus</option>
              {/* Add more soil conditions as needed */}
            </select>
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
