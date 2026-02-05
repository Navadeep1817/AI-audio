/**
 * TranscriptViewer
 *
 * Props:
 *   transcript   object | null   TranscriptResponse from backend
 */
export default function TranscriptViewer({ transcript }) {
  // ── empty state ───────────────────────────────────────────────
  if (!transcript || !transcript.segments || transcript.segments.length === 0) {
    return (
      <div className="page">
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h3>No Transcript Available</h3>
          <p>
            Upload a sales call first. The transcript will appear here once
            AWS Transcribe finishes processing.
          </p>
        </div>
      </div>
    );
  }

  // ── derived stats ─────────────────────────────────────────────
  const repSegments  = transcript.segments.filter((s) => s.speaker === "spk_0");
  const custSegments = transcript.segments.filter((s) => s.speaker === "spk_1");

  const countWords = (segs) =>
    segs.reduce((acc, s) => acc + s.text.split(" ").length, 0);

  const repWords  = countWords(repSegments);
  const custWords = countWords(custSegments);
  const totalWords = repWords + custWords || 1;

  const repPct  = Math.round((repWords / totalWords) * 100);
  const custPct = Math.round((custWords / totalWords) * 100);

  const talkScore = Math.max(
    0,
    Math.min(10, 10 - Math.abs(custPct - 65) / 3.5)
  );

  // ── helpers ───────────────────────────────────────────────────
  const fmtTime = (seconds) => {
    const m   = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  // ── render ────────────────────────────────────────────────────
  return (
    <div className="page">
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header">
          <h3>Call Transcript</h3>
          <span className="badge">
            {transcript.segments.length} segments · {fmtTime(transcript.duration)} duration
          </span>
        </div>
      </div>

      <div className="transcript-page">
        {/* ── messages ───────────────────────── */}
        <div className="transcript-scroll">
          {transcript.segments.map((seg, i) => {
            const isRep = seg.speaker === "spk_0";

            return (
              <div className="transcript-msg" key={i}>
                <div className={`msg-avatar ${isRep ? "rep" : "cust"}`}>
                  {isRep ? "SR" : "CU"}
                </div>

                <div className="msg-content">
                  <div className="msg-header">
                    <span className="msg-speaker">
                      {isRep ? "Sales Rep" : "Customer"}
                    </span>
                    <span className="msg-time">
                      {fmtTime(seg.start_time)} – {fmtTime(seg.end_time)}
                    </span>
                  </div>

                  <div className="msg-text">{seg.text}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── sidebar ───────────────────────── */}
        <div className="transcript-meta">
          <div className="meta-card">
            <div className="meta-label">Speaker Breakdown</div>

            <div className="speaker-legend">
              <div className="legend-row">
                <span className="legend-dot rep" />
                <span className="legend-label">Sales Rep</span>
                <span className="legend-pct">{repPct}%</span>
              </div>

              <div className="legend-row">
                <span className="legend-dot cust" />
                <span className="legend-label">Customer</span>
                <span className="legend-pct">{custPct}%</span>
              </div>
            </div>

            <div style={{ marginTop: 14 }}>
              <ScoreBar score={parseFloat(talkScore.toFixed(1))} />
              <p className="talk-ratio-note">
                Customer talk ratio (target: 60–70 %)
              </p>
            </div>
          </div>

          <div className="meta-card">
            <div className="meta-label">Call Stats</div>
            <div className="meta-value">
              <div className="meta-row">
                <span>Duration</span>
                <strong>{fmtTime(transcript.duration)}</strong>
              </div>
              <div className="meta-row">
                <span>Word Count</span>
                <strong>{transcript.word_count}</strong>
              </div>
              <div className="meta-row">
                <span>Segments</span>
                <strong>{transcript.segments.length}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── ScoreBar ───────────────────────── */
function ScoreBar({ score, max = 10 }) {
  const pct = (score / max) * 100;

  const color =
    pct >= 70
      ? "var(--accent)"
      : pct >= 45
      ? "var(--warn)"
      : "var(--danger)";

  return (
    <div className="score-bar-wrap">
      <div className="score-bar-track">
        <div
          className="score-bar-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="score-bar-label">{score}/10</span>
    </div>
  );
}
