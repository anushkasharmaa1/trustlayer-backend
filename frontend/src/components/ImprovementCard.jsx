function ImprovementCard({ recommendation, improvementValue }) {
  return (
    <div className="card" style={{ padding: '28px', minHeight: '220px' }}>
      <div className="card-header">
        <div>
          <h3 className="card-title">Improvement suggestion</h3>
          <p className="card-note">A simple step that could lift your trust score.</p>
        </div>
      </div>
      <div style={{ display: 'grid', gap: '18px', marginTop: '14px' }}>
        <div style={{ fontSize: '1.4rem', fontWeight: 700, lineHeight: 1.4 }}>{recommendation}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span className="signal-chip">+{improvementValue} pts</span>
          <span style={{ color: '#475569' }}>Move toward a stronger RBI-compatible behaviour profile.</span>
        </div>
      </div>
    </div>
  );
}

export default ImprovementCard;
