import React, { useState } from "react";
import axios from "axios";

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { text: input, sender: "user" };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsTyping(true);

        try {
            const res = await axios.get("http://127.0.0.1:8000/query", { params: { question: input } });
            const botMessage = { text: res.data.answer, sender: "bot", references: res.data.references || [] };
            
            setTimeout(() => {
                setMessages((prev) => [...prev, botMessage]);
                setIsTyping(false);
            }, 1000);
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
                    <div dangerouslySetInnerHTML={{ __html: msg.text.replace(/\n/g, '<br />') }}></div><br />
                    {msg.references && msg.references.length > 0 && (
                        <div className="references">
                            <br /> 
                            <h4>References:</h4>
                            <ul>
                                {msg.references.map((ref, i) => (
                                    <li key={i}><strong>{ref.title}</strong>{ref.page ? ` - Page ${ref.page}` : ""}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            ))}
            {isTyping && <div className="typing-indicator">LexI is typing...</div>}
            <div className="input-container">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask something about immigration law..."
                />
                <button onClick={handleSend}>Send</button>
            </div>
        </div>
    );
};

export default Chatbot;
