export function Icon({ name, className = "", style = {} }) {
  const icons = {
    upload: "⬆️",
    fileText: "📄",
    barChart: "📊",
    mic: "🎤",
    check: "✔️",
    arrowRight: "➡️",
    chevronDown: "⌄",
    alertCircle: "⚠️",
    target: "🎯",
    brain: "🧠",
    users: "👥",
  };

  return (
    <span className={className} style={{ display: "inline-block", ...style }}>
      {icons[name] || "•"}
    </span>
  );
}
