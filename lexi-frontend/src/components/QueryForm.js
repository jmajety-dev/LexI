import React, { useState } from "react";
import axios from "axios";

const QueryForm = () => {
    const [query, setQuery] = useState("");
    const [response, setResponse] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.get("http://127.0.0.1:8000/query", { params: { question: query } });
            setResponse(res.data.answer);
        } catch (error) {
            setResponse("Error fetching response. Please try again.");
        }
    };

    return (
        <div className="query-container">
            <h2>Ask Your Immigration Question</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter your question"
                    required
                />
                <br />
                <button type="submit">Get Answer</button>
            </form>
            {response && <div className="response"><strong>Answer:</strong> {response}</div>}
        </div>
    );
};

export default QueryForm;
