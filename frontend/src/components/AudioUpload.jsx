import { useState } from "react";
import { uploadAudioFile } from "../services/api";

export default function AudioUpload({ setJobId }) {
  const [progress, setProgress] = useState(0);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const jobId = await uploadAudioFile(file, setProgress);

      localStorage.setItem("jobId", jobId);
      setJobId(jobId);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  }

  return (
    <div style={{ padding: 40 }}>
      <input type="file" onChange={handleUpload} />
      <p>Upload Progress: {progress}%</p>
    </div>
  );
}
