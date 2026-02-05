import { useState } from "react";
import InsightsDashboard from "./components/InsightsDashboard";
import AudioUpload from "./components/AudioUpload";
import ErrorBoundary from "./components/ErrorBoundary";

export default function App() {
  const [jobId, setJobId] = useState(
    localStorage.getItem("jobId") || null
  );

  return (
    <ErrorBoundary>
      <div style={{ background: "#000", minHeight: "100vh" }}>
        <AudioUpload setJobId={setJobId} />
        <InsightsDashboard jobId={jobId} />
      </div>
    </ErrorBoundary>
  );
}
