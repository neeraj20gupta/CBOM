import { Pie, PieChart, Cell, ResponsiveContainer } from 'recharts';

export type DonutDatum = {
  name: string;
  value: number;
  color: string;
};

type DonutCardProps = {
  title: string;
  value: number;
  data: DonutDatum[];
};

const renderLabel = ({ percent }: { percent: number }) => {
  if (percent <= 0) return '';
  return `${Math.round(percent * 100)}%`;
};

const DonutCard = ({ title, value, data }: DonutCardProps) => {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="donut-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={55}
              outerRadius={82}
              paddingAngle={2}
              label={renderLabel}
              labelLine={false}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} stroke="#0b0f1a" />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="donut-center">
          <div className="donut-value">{value}</div>
          <div className="donut-label">Total</div>
        </div>
      </div>
    </div>
  );
};

export default DonutCard;
