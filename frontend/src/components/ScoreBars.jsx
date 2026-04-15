function ScoreBars({ items }) {
  return (
    <div style={{ display: 'grid', gap: '18px' }}>
      {items.map((item) => (
        <div key={item.label}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
            <span style={{ fontWeight: 600 }}>{item.label}</span>
            <span style={{ color: '#475569' }}>{Math.round(item.value * 100)}%</span>
          </div>
          <div className="score-bar">
            <div className="score-bar-fill" style={{ width: `${Math.round(item.value * 100)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default ScoreBars;
