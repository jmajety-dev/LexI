import React, { useState } from "react";
import axios from "axios";

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        // Add user message
        const userMessage = { text: input, sender: "user" };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        // Show typing indicator
        setIsTyping(true);

        try {
            const res = await axios.get("http://127.0.0.1:8000/query", { params: { question: input } });
            const botMessage = { text: res.data.answer, sender: "bot" };
            setTimeout(() => {
                setMessages((prev) => [...prev, botMessage]);
                setIsTyping(false);
            }, 1000); // Simulate response delay
        } catch (error) {
            setTimeout(() => {
                setMessages((prev) => [...prev, { text: "Error fetching response. Please try again.", sender: "bot" }]);
                setIsTyping(false);
            }, 1000);
        }
    };

    return (
        <div className="chat-container">
            {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.sender === "user" ? "user-message" : "bot-message"}`}>
                    {msg.sender === "bot"} {/* Replacing 🤖 with ⚖️ */}
                    {msg.text}
                </div>
            ))}
            {isTyping && <div className="typing-indicator">LexI is typing...</div>}
            <div className="input-container">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask something..."
                />
                <button onClick={handleSend}>Send</button>
            </div>
        </div>
    );
};

export default Chatbot;
