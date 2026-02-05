import { useEffect, useState } from "react";
import { uploadAudioFile, getJobStatus } from "../services/api";

export default function InsightsDashboard() {

  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [report, setReport] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // =========================================================
  // SAFE FILE UPLOAD
  // =========================================================
  const handleUpload = async (e) => {

    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setError(null);
      setLoading(true);

      const newJobId = await uploadAudioFile(file);

      setJobId(newJobId);

    } catch (err) {
      console.error(err);
      setError("Upload failed.");
      setLoading(false);
    }
  };

  // =========================================================
  // POLLING LOOP (ULTRA SAFE)
  // =========================================================
  useEffect(() => {

    if (!jobId) return;

    let interval;

    const poll = async () => {

      try {
        const data = await getJobStatus(jobId);

        setStatus(data);

        if (data.transcript) {
          setTranscript(data.transcript);
        }

        if (data.report) {
          setReport(data.report);
        }

        if (data.status === "completed" || data.status === "failed") {
          setLoading(false);
          clearInterval(interval);
        }

      } catch (err) {
        console.error(err);
        setError("Failed to fetch job status.");
        setLoading(false);
        clearInterval(interval);
      }
    };

    poll();
    interval = setInterval(poll, 3000);

    return () => clearInterval(interval);

  }, [jobId]);

  // =========================================================
  // SAFE RENDER HELPERS
  // =========================================================
  const renderTranscript = () => {

    if (!transcript?.segments?.length) {
      return <p>No transcript available.</p>;
    }

    return transcript.segments.map((seg, i) => (
      <p key={i}>
        <b>{seg.speaker}</b>: {seg.text}
      </p>
    ));
  };

  const renderReport = () => {

    if (!report) return <p>No report yet.</p>;

    return (
      <div>

        <h3>Overall Score: {report.overall_score}</h3>

        <h4>Strengths</h4>
        <ul>
          {(report.strengths || []).map((s, i) => <li key={i}>{s}</li>)}
        </ul>

        <h4>Areas To Improve</h4>
        <ul>
          {(report.areas_to_improve || []).map((w, i) => <li key={i}>{w}</li>)}
        </ul>

        <h4>Missed Opportunities</h4>
        <ul>
          {(report.missed_opportunities || []).map((m, i) => <li key={i}>{m}</li>)}
        </ul>

      </div>
    );
  };

  // =========================================================
  // MAIN UI
  // =========================================================
  return (
    <div style={{ padding: "30px", fontFamily: "sans-serif" }}>

      <h1>AI Sales Coach Dashboard</h1>

      <input type="file" accept="audio/*" onChange={handleUpload} />

      {loading && <p>Processing audio...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {status && (
        <div>
          <h3>Status: {status.status}</h3>
          <p>Progress: {status.progress_percentage}%</p>
        </div>
      )}

      <hr />

      <h2>Transcript</h2>
      {renderTranscript()}

      <hr />

      <h2>Insights</h2>
      {renderReport()}

    </div>
  );
}
