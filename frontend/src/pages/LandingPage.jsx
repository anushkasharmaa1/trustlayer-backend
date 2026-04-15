function LandingPage({ onStart }) {
  return (
    <div className="page-container">
      <div className="hero-panel">
        <div className="hero-eyebrow">TrustLayer</div>
        <h1 className="hero-title">Behavioral Credit Intelligence for the Gig Economy</h1>
        <p className="hero-copy">
          A modern financial dashboard that interprets cash flow, work diversification and savings behavior for independent workers.
          Trusted insights designed to support smarter credit access without traditional bureau bias.
        </p>
        <div className="cta-grid">
          <button className="cta-button" onClick={onStart}>
            View Demo Dashboard
          </button>
          <span className="note-pill">No login required — just demo insights.</span>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
