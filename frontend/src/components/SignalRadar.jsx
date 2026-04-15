import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer
} from 'recharts';

function SignalRadar({ data }) {
  return (
    <div style={{ width: '100%', height: 380 }}>
      <ResponsiveContainer>
        <RadarChart data={data} outerRadius="80%">
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12, fill: '#475569' }} />
          <PolarRadiusAxis angle={30} domain={[0, 1]} tickCount={5} axisLine={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
          <Radar dataKey="value" stroke="#0d9488" fill="#0d9488" fillOpacity={0.2} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default SignalRadar;
