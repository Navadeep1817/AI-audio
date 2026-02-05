import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error) {
    console.error("UI Crash:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 40, color: "white" }}>
          ⚠️ UI crashed — reload page
        </div>
      );
    }
    return this.props.children;
  }
}
