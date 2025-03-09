import React, { useState } from "react";

const FileUploader = () => {
    const [file, setFile] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = () => {
        alert("Document processing feature coming soon!");
    };

    return (
        <div className="upload-container">
            <h2>Upload Immigration Documents</h2>
            <input type="file" accept=".pdf" onChange={handleFileChange} />
            {file && <button onClick={handleUpload}>Upload</button>}
        </div>
    );
};

export default FileUploader;
