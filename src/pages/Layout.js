import React, { useState } from "react";
import { Link, Outlet } from "react-router-dom";
import "../styles/Layout.css";


function Layout() {
    const [isSidebarExpanded, setIsSidebarExpanded] = useState(true);
  
    const toggleSidebar = () => {
      setIsSidebarExpanded(!isSidebarExpanded);
    };
  
    return (
      <div className="layout-container">
        {/* Side Panel */}
        <div className={`side-panel ${isSidebarExpanded ? "expanded" : "collapsed"}`}>
          <button className="toggle-btn" onClick={toggleSidebar}>
            {isSidebarExpanded ? "<<" : ">>"}
          </button>
          <ul>
            <li><Link to="/dashboard">Dashboard</Link></li>
            <li><Link to="/settings">Settings</Link></li>
            <li><Link to="/profile">Profile</Link></li>
            <li><Link to="/logout">Logout</Link></li>
          </ul>
        </div>
  
        {/* Main Content Area */}
        <div className="main-content">
                  <div className="top-nav">
                    <div className="nav-left">
                      <h1>App Name</h1>
                    </div>
                    <div className="nav-right">
                      <button className="chat-btn" onClick={() => window.location.href = '/chat'}>Chat</button>
                      <button className="logout-btn" onClick={() => window.location.href = '/logout'}>Logout</button>
                      <button className="profile-btn" onClick={() => window.location.href = '/profile'}>Profile</button>
                    </div>
                  </div>
          
                  {/* Page Content */}
          <div className="page-content">
            <Outlet />
          </div>
        </div>
      </div>
    );
  }
  
  export default Layout;