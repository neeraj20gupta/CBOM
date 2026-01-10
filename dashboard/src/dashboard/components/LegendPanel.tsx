type LegendItem = {
  label: string;
  color: string;
};

type LegendGroup = {
  title: string;
  items: LegendItem[];
};

type LegendPanelProps = {
  groups: LegendGroup[];
};

const LegendPanel = ({ groups }: LegendPanelProps) => {
  return (
    <div className="legend-grid">
      {groups.map((group) => (
        <div key={group.title}>
          <div className="legend-group-title">{group.title}</div>
          {group.items.map((item) => (
            <div key={item.label} className="legend-item">
              <span className="legend-swatch" style={{ backgroundColor: item.color }} />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default LegendPanel;
