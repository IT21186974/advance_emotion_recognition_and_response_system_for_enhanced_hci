const express = require("express");
const cors = require("cors");
const axios = require("axios");

const app = express();
const port = 5000;

app.use(cors());
app.use(express.json());

// Define a route for chat completion
app.post("/chat", async (req, res) => {
   // Get the user message from the frontend
  const { userMessage } = req.body;

  try {
    // Send a request to the Python server running on port 5001
    const response = await axios.post("http://127.0.0.1:5001/generate", { userMessage });

    // Send the response from the Python server back to the frontend
    res.json({ message: response.data.message });
  } catch (error) {
    // Handle errors and send error response
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
