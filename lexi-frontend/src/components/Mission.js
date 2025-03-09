import React, { useEffect, useState } from "react";
import axios from "axios";

const Mission = () => {
    const [mission, setMission] = useState("");

    useEffect(() => {
        axios.get("http://127.0.0.1:8000/mission")
            .then((res) => setMission(res.data.mission))
            .catch(() => setMission("Providing compassionate and high-quality legal services to immigrants and their families."));
    }, []);

    return (
        <div className="mission-container">
            <h2>Our Mission</h2>
            <p>{mission}</p>
        </div>
    );
};

export default Mission;
