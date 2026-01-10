import { hierarchy, pack } from 'd3-hierarchy';
import { useEffect, useMemo, useRef, useState } from 'react';

export type BubbleDatum = {
  name: string;
  value: number;
  color: string;
};

type BubblePackProps = {
  data: BubbleDatum[];
};

const BubblePack = ({ data }: BubblePackProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [size, setSize] = useState({ width: 520, height: 260 });

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (entry) {
        setSize({ width: entry.contentRect.width, height: entry.contentRect.height });
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const nodes = useMemo(() => {
    const root = hierarchy({ children: data }).sum((d) => (d as BubbleDatum).value || 1);
    return pack<BubbleDatum>()
      .size([size.width, size.height])
      .padding(8)(root)
      .leaves();
  }, [data, size.height, size.width]);

  return (
    <div className="bubble-canvas" ref={containerRef}>
      <svg width={size.width} height={size.height}>
        {nodes.map((node) => (
          <g key={node.data.name} transform={`translate(${node.x}, ${node.y})`}>
            <circle r={node.r} fill={node.data.color} opacity={0.85} />
            <text
              textAnchor="middle"
              dy="0.35em"
              fontSize={Math.max(10, node.r / 3)}
              fill="#0b0f1a"
            >
              {node.data.name}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
};

export default BubblePack;
