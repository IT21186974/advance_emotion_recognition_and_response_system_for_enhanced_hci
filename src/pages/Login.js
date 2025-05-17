import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import loginImage from "../assets/login-image.jpg";
import "../styles/Login.css";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === "nadee" && password === "nadee123") {
      navigate("/chat");
    } else {
      alert("Invalid username or password");
    }
  };

  return (
    <div className="login-page">
      {/* Left side with image */}
      <div className="login-image">
        <img src={loginImage} alt="Chat Illustration" />
      </div>

      {/* Right side with login form */}
      <div className="login-container">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          <button className="button" type="submit">Login</button>
        </form>
      </div>
    </div>
  );
}

export default Login;
