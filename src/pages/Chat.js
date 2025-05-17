import React, { useState } from "react";
import axios from "axios";
import "../styles/Chat.css"; // Import your CSS file for styling
import chatBackground from "../assets/chat-background.jpg";

function formatBotMessage(message) {
  // Convert headings (## -> <h2> tag)
  let formattedMessage = message.replace(/## (.*?)(?=\n)/g, "<h2>$1</h2>");

  // Convert bold text (**text** -> <strong>text</strong>)
  formattedMessage = formattedMessage.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Convert unordered lists (* or - to <ul><li></li></ul>)
  formattedMessage = formattedMessage.replace(/^\s*[*-]\s+(.*?)(?=\n|$)/gm, "<ul><li>$1</li></ul>");

  // Convert ordered lists (1. text -> <ol><li>text</li></ol>)
  formattedMessage = formattedMessage.replace(/^\d+\.\s+(.*?)(?=\n|$)/gm, "<ol><li>$1</li></ol>");

  // Convert paragraphs (double newlines -> <p> tags)
  formattedMessage = formattedMessage.replace(/\n\n+/g, "</p><p>");

  // Wrap the entire message in a <p> tag to ensure proper formatting of first and last paragraphs
  formattedMessage = `<p>${formattedMessage}</p>`;

  return formattedMessage;
}

function Chat() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  const handleMessageChange = (e) => {
    setMessage(e.target.value);
  };

  const handleSendMessage = async () => {
    if (message.trim() === "") return;
  
    const userMessage = { sender: "user", text: message };
    setChatHistory((prevState) => [...prevState, userMessage]);
  
    try {
      const response = await axios.post("http://localhost:5000/chat", { userMessage: message });
      const botMessage = { sender: "bot", text: response.data.message };
  
      // Use formatBotMessage to format the bot's response
      const formattedMessage = formatBotMessage(botMessage.text);
      const formattedBotMessage = { sender: "bot", text: formattedMessage };

      setTimeout(() => {
        setChatHistory((prevState) => [...prevState, formattedBotMessage]);
      }, 300);
      setMessage("");
    } catch (error) {
      console.error("Error fetching response:", error);
    }
  };
  
  return (
    <div className="chat-container" style={{ backgroundImage: `url(${chatBackground})` }}>
      <div className="chat-box">
        {chatHistory.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`} dangerouslySetInnerHTML={{ __html: msg.text }}></div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={message}
          onChange={handleMessageChange}
          placeholder="Type your message..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default Chat;
