import React from "react";
import Chatbot from "./components/ChatBot";
// import Mission from "./components/Mission";
import "./styles.css";

function App() {
    return (
        <div className="app-container">
            <header className="header-container">
                <h1>LexI: AI-Powered Immigration Assistant</h1>
                <p>Your trusted AI assistant for legal immigration guidance</p>
            </header>
            <Chatbot />
            {/* <Mission /> */}
        </div>
    );
}

export default App;
