import React, { useState, useEffect } from "react";
import axios from "axios";

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const [systemHealth, setSystemHealth] = useState(null);
    const [showAgentDetails, setShowAgentDetails] = useState(false);

    // Check system health on component mount
    useEffect(() => {
        checkSystemHealth();
    }, []);

    const checkSystemHealth = async () => {
        try {
            const response = await axios.get("http://127.0.0.1:8000/health");
            setSystemHealth(response.data);
        } catch (error) {
            console.error("Health check failed:", error);
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = { 
            text: input, 
            sender: "user",
            timestamp: new Date().toLocaleTimeString()
        };
        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsTyping(true);

        try {
            const startTime = Date.now();
            const res = await axios.get("http://127.0.0.1:8000/query", { 
                params: { question: input } 
            });
            const processingTime = Date.now() - startTime;
            
            // Enhanced bot message with multi-agent response data
            const botMessage = { 
                text: res.data.answer, 
                sender: "bot",
                timestamp: new Date().toLocaleTimeString(),
                // Multi-agent system metadata
                sources: res.data.sources || [],
                confidence_score: res.data.confidence_score || 0,
                processing_time: res.data.processing_time || processingTime / 1000,
                agent_metrics: res.data.agent_metrics || {},
                optimization_applied: res.data.optimization_applied || {},
                legal_domain: res.data.legal_domain,
                response_quality_score: res.data.response_quality_score
            };
            
            setTimeout(() => {
                setMessages((prev) => [...prev, botMessage]);
                setIsTyping(false);
            }, 1000);
        } catch (error) {
            setTimeout(() => {
                setMessages((prev) => [...prev, { 
                    text: "Error fetching response. Please try again.", 
                    sender: "bot",
                    timestamp: new Date().toLocaleTimeString(),
                    isError: true
                }]);
                setIsTyping(false);
            }, 1000);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const formatConfidenceScore = (score) => {
        if (!score) return "N/A";
        return `${(score * 100).toFixed(1)}%`;
    };

    const getConfidenceColor = (score) => {
        if (score >= 0.8) return "#28a745"; // Green
        if (score >= 0.6) return "#ffc107"; // Yellow
        return "#dc3545"; // Red
    };

    return (
        <div className="chat-container">
            {/* System Status Header */}
            {systemHealth && (
                <div className="system-status">
                    <div className="status-indicator">
                        <span className={`status-dot ${systemHealth.status === 'healthy' ? 'healthy' : 'unhealthy'}`}></span>
                        <span className="status-text">
                            Multi-Model Agents: {systemHealth.status} 
                            ({systemHealth.agents_initialized} agents active)
                        </span>
                        <button 
                            className="details-toggle"
                            onClick={() => setShowAgentDetails(!showAgentDetails)}
                        >
                            {showAgentDetails ? 'Hide' : 'Show'} Details
                        </button>
                    </div>
                    
                    {showAgentDetails && (
                        <div className="agent-details">
                            <div className="optimization-status">
                                <h4>🎯 70% Accuracy Optimization Active</h4>
                                <div className="optimization-features">
                                    <span className="feature">✓ PyTorch Embedding Optimization</span>
                                    <span className="feature">✓ Legal Domain Fine-tuning</span>
                                    <span className="feature">✓ Multi-Strategy Retrieval</span>
                                    <span className="feature">✓ Agent-based Workflows</span>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Chat Messages */}
            <div className="messages-container">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender === "user" ? "user-message" : "bot-message"}`}>
                        {/* Message Header */}
                        <div className="message-header">
                            <span className="sender-name">
                                {msg.sender === "user" ? "You" : "LexI AI"}
                            </span>
                            <span className="timestamp">{msg.timestamp}</span>
                            {msg.legal_domain && (
                                <span className="legal-domain">{msg.legal_domain}</span>
                            )}
                        </div>

                        {/* Message Content */}
                        <div className="message-content">
                            <div dangerouslySetInnerHTML={{ __html: msg.text.replace(/\n/g, '<br />') }}></div>
                        </div>

                        {/* Multi-Agent System Metadata (for bot messages) */}
                        {msg.sender === "bot" && !msg.isError && (
                            <div className="agent-metadata">
                                {/* Confidence and Quality Scores */}
                                <div className="scores-container">
                                    <div className="score-item">
                                        <span className="score-label">Confidence:</span>
                                        <span 
                                            className="score-value"
                                            style={{ color: getConfidenceColor(msg.confidence_score) }}
                                        >
                                            {formatConfidenceScore(msg.confidence_score)}
                                        </span>
                                    </div>
                                    {msg.response_quality_score && (
                                        <div className="score-item">
                                            <span className="score-label">Quality:</span>
                                            <span className="score-value">
                                                {formatConfidenceScore(msg.response_quality_score)}
                                            </span>
                                        </div>
                                    )}
                                    <div className="score-item">
                                        <span className="score-label">Response Time:</span>
                                        <span className="score-value">
                                            {msg.processing_time?.toFixed(2)}s
                                        </span>
                                    </div>
                                </div>

                                {/* Optimization Applied */}
                                {msg.optimization_applied && Object.keys(msg.optimization_applied).length > 0 && (
                                    <div className="optimization-applied">
                                        <h5>🔧 Optimizations Applied:</h5>
                                        <div className="optimization-list">
                                            {Object.entries(msg.optimization_applied).map(([key, value]) => (
                                                value && (
                                                    <span key={key} className="optimization-tag">
                                                        {key.replace(/_/g, ' ')}
                                                    </span>
                                                )
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Legal Sources */}
                                {msg.sources && msg.sources.length > 0 && (
                                    <div className="sources-section">
                                        <h5>📚 Legal Sources:</h5>
                                        <div className="sources-list">
                                            {msg.sources.map((source, i) => (
                                                <div key={i} className="source-item">
                                                    <div className="source-header">
                                                        <strong>{source.title}</strong>
                                                        {source.legal_authority_level && (
                                                            <span className={`authority-badge ${source.legal_authority_level}`}>
                                                                {source.legal_authority_level}
                                                            </span>
                                                        )}
                                                    </div>
                                                    {source.source_type && (
                                                        <span className="source-type">
                                                            Type: {source.source_type}
                                                        </span>
                                                    )}
                                                    {source.relevance_score && (
                                                        <span className="relevance-score">
                                                            Relevance: {(source.relevance_score * 100).toFixed(1)}%
                                                        </span>
                                                    )}
                                                    {source.retrieval_method && (
                                                        <span className="retrieval-method">
                                                            Retrieved via: {source.retrieval_method}
                                                        </span>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Agent Performance Metrics */}
                                {msg.agent_metrics && Object.keys(msg.agent_metrics).length > 0 && (
                                    <details className="agent-metrics">
                                        <summary>🤖 Agent Performance Details</summary>
                                        <div className="metrics-grid">
                                            {Object.entries(msg.agent_metrics).map(([key, value]) => (
                                                <div key={key} className="metric-item">
                                                    <span className="metric-label">
                                                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                                                    </span>
                                                    <span className="metric-value">
                                                        {typeof value === 'number' && key.includes('time') 
                                                            ? `${value.toFixed(3)}s` 
                                                            : value?.toString()}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </details>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Typing Indicator */}
            {isTyping && (
                <div className="typing-indicator">
                    <div className="typing-animation">
                        <span>🤖</span>
                        <span>LexI Multi-Agents are processing...</span>
                        <div className="dots">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
            )}

            {/* Input Container */}
            <div className="input-container">
                <div className="input-wrapper">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask about immigration law, regulations, or legal procedures..."
                        rows="2"
                        className="chat-input"
                    />
                    <button 
                        onClick={handleSend} 
                        disabled={!input.trim() || isTyping}
                        className="send-button"
                    >
                        {isTyping ? (
                            <span className="processing">Processing...</span>
                        ) : (
                            <span>Send 🚀</span>
                        )}
                    </button>
                </div>
                <div className="input-footer">
                    <span className="powered-by">
                        Powered by Multi-Model Agents • LlamaIndex • PyTorch Optimization
                    </span>
                </div>
            </div>
        </div>
    );
};

export default Chatbot;
