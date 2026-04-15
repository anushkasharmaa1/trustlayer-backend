import { useMemo } from 'react';

function TrustScoreGauge({ score }) {
  const progress = Math.min(Math.max(score / 1000, 0), 1);
  const radius = 74;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - progress);

  const gaugeColor = useMemo(() => {
    if (score >= 750) return '#0d9488';
    if (score >= 650) return '#14b8a6';
    if (score >= 550) return '#f59e0b';
    return '#ef4444';
  }, [score]);

  return (
    <div className="trust-gauge" style={{ width: 240, height: 220, position: 'relative' }}>
      <svg width="240" height="220" viewBox="0 0 240 220">
        <circle
          cx="120"
          cy="120"
          r={radius}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth="16"
          strokeLinecap="round"
          transform="rotate(-140 120 120)"
        />
        <circle
          cx="120"
          cy="120"
          r={radius}
          fill="none"
          stroke={gaugeColor}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-140 120 120)"
          style={{ transition: 'stroke-dashoffset 0.8s ease, stroke 0.3s ease' }}
        />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '3.6rem', fontWeight: 800, lineHeight: 1 }}>{score}</div>
          <div style={{ color: '#475569', marginTop: 6 }}>Trust Score</div>
        </div>
      </div>
    </div>
  );
}

export default TrustScoreGauge;
