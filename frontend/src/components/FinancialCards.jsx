function FinancialCards({ avgIncome, savingsRate, billRegularity }) {
  const cards = [
    { label: 'Average Monthly Income', value: `₹${avgIncome.toLocaleString()}` },
    { label: 'Savings Rate', value: `${Math.round(savingsRate * 100)}%` },
    { label: 'Bill Regularity', value: `${Math.round(billRegularity * 100)}%` }
  ];

  return (
    <div className="card-grid-3">
      {cards.map((item) => (
        <div key={item.label} className="mini-card">
          <p className="mini-card-label">{item.label}</p>
          <div className="mini-card-value">{item.value}</div>
        </div>
      ))}
    </div>
  );
}

export default FinancialCards;
