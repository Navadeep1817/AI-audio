/**
 * LoadingSpinner (Processing Page)
 *
 * Props:
 *   progress      number   0–100 percentage fed into the ring + step tracker
 *   currentStep   string   Human-readable label for what is happening right now
 */
export default function LoadingSpinner({ progress, currentStep }) {
  // ── pipeline step definitions ───────────────────────────────────────────
  const steps = [
    { name: "Upload",         desc: "Audio stored in S3" },
    { name: "Transcribe",     desc: "AWS Transcribe running" },
    { name: "RAG Retrieval",  desc: "Querying knowledge base" },
    { name: "Agent Analysis", desc: "3 specialist agents analyzing" },
    { name: "Report",         desc: "Synthesizing final insights" },
  ];

  // Map progress 0-100 → which step is currently active (0-indexed)
  const activeIdx =
    progress < 20  ? 0 :
    progress < 40  ? 1 :
    progress < 60  ? 2 :
    progress < 80  ? 3 : 4;

  // ── SVG ring math ───────────────────────────────────────────────────────
  const RADIUS = 54;
  const CIRCUMFERENCE = 2 * Math.PI * RADIUS;                // ≈ 339.29
  const offset = CIRCUMFERENCE - (progress / 100) * CIRCUMFERENCE;

  // ── render ──────────────────────────────────────────────────────────────
  return (
    <div className="page">
      <div className="processing-page">

        {/* ── Animated Progress Ring ────────────────────────────────── */}
        <div className="progress-ring-wrap">
          <svg className="progress-ring">
            {/* background track */}
            <circle
              className="progress-ring-bg"
              cx="70" cy="70" r={RADIUS}
            />
            {/* animated foreground arc */}
            <circle
              className="progress-ring-fg"
              cx="70" cy="70" r={RADIUS}
              strokeDasharray={CIRCUMFERENCE}
              strokeDashoffset={offset}
            />
          </svg>

          {/* centered percentage + label */}
          <div className="progress-ring-center">
            <span className="pct">{progress}%</span>
            <span className="label">Processing</span>
          </div>
        </div>

        {/* ── 5-Step Pipeline Tracker ───────────────────────────────── */}
        <div className="pipeline-steps">
          {steps.map((step, i) => {
            const isDone   = i < activeIdx;
            const isActive = i === activeIdx;

            return (
              <div className="pipeline-step" key={i}>
                {/* dot + connector column */}
                <div className="step-line-wrap">
                  <div
                    className={`step-dot ${
                      isDone ? "done" : isActive ? "active" : ""
                    }`}
                  >
                    {isDone ? "✓" : i + 1}
                  </div>

                  {/* vertical connector between dots (not after the last one) */}
                  {i < steps.length - 1 && (
                    <div className={`step-connector ${isDone ? "done" : ""}`} />
                  )}
                </div>

                {/* label column */}
                <div className="step-text">
                  <div
                    className={`step-name ${
                      isDone ? "done" : isActive ? "active" : ""
                    }`}
                  >
                    {step.name}
                  </div>
                  <div className="step-desc">{step.desc}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* ── Current-step live label ───────────────────────────────── */}
        <div className="current-step-label">{currentStep}</div>
      </div>
    </div>
  );
}
