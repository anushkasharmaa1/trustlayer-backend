function Tabs({ items, activeItem, onChange }) {
  return (
    <div className="tab-list" style={{ marginBottom: '22px' }}>
      {items.map((item) => (
        <button
          key={item}
          className={`tab-button ${activeItem === item ? 'active' : ''}`}
          onClick={() => onChange(item)}
        >
          {item}
        </button>
      ))}
    </div>
  );
}

export default Tabs;
