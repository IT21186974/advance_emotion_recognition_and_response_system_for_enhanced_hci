import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./pages/Layout";
import Login from "./pages/Login";
import Chat from "./pages/Chat";
import Dashboard from "./pages/Dashboard"; // Your new page
import Settings from "./pages/Settings"; // Your new page
import Profile from "./pages/Profile"; // Your new page
import Logout from "./pages/Logout"; // Your new page

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />  {/* Keep Login page as it is */}
        <Route path="/" element={<Layout />}>
          <Route path="chat" element={<Chat />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="settings" element={<Settings />} />
          <Route path="profile" element={<Profile />} />
          <Route path="logout" element={<Logout />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
