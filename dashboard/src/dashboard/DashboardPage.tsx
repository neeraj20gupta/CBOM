import { useEffect, useMemo, useState } from 'react';
import DonutCard, { DonutDatum } from './components/DonutCard';
import BubblePack, { BubbleDatum } from './components/BubblePack';
import LegendPanel from './components/LegendPanel';
import FileUploader from './components/FileUploader';
import RepoAnalyzer from './components/RepoAnalyzer';
import { DashboardData, parseCbom } from './data/parseCbom';

const COLORS = {
  quantumSafe: '#34d399',
  notQuantumSafe: '#f97316',
  unknown: '#64748b',
  hash: '#38bdf8',
  mac: '#f472b6',
  blockCipher: '#60a5fa',
  pke: '#c084fc',
  signature: '#fb7185',
  ae: '#fbbf24',
  other: '#94a3b8',
  functions: ['#60a5fa', '#34d399', '#f97316', '#f472b6', '#fbbf24', '#c084fc', '#38bdf8', '#94a3b8']
};

const DashboardPage = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeFile, setActiveFile] = useState<string | null>(null);

  useEffect(() => {
    fetch('/sample.json')
      .then((response) => response.json())
      .then((payload) => {
        setData(parseCbom(payload));
      })
      .catch(() => {
        setError('Unable to load sample.json. Upload a CBOM or CycloneDX file.');
      });
  }, []);

  const handleFileLoaded = (payload: unknown, fileName: string) => {
    try {
      setData(parseCbom(payload));
      setError(null);
      setActiveFile(fileName);
    } catch (err) {
      setError('Unable to parse file. Ensure it is valid CBOM or CycloneDX JSON.');
    }
  };

  const quantumDonut = useMemo<DonutDatum[]>(() => {
    if (!data) return [];
    return [
      { name: 'Quantum Safe', value: data.quantumSafety.quantumSafe, color: COLORS.quantumSafe },
      { name: 'Not Quantum Safe', value: data.quantumSafety.notQuantumSafe, color: COLORS.notQuantumSafe },
      { name: 'Unknown', value: data.quantumSafety.unknown, color: COLORS.unknown }
    ];
  }, [data]);

  const primitivesDonut = useMemo<DonutDatum[]>(() => {
    if (!data) return [];
    return [
      { name: 'Hash', value: data.primitives.hash, color: COLORS.hash },
      { name: 'MAC', value: data.primitives.mac, color: COLORS.mac },
      { name: 'Block Cipher', value: data.primitives['block-cipher'], color: COLORS.blockCipher },
      { name: 'PKE', value: data.primitives.pke, color: COLORS.pke },
      { name: 'Signature', value: data.primitives.signature, color: COLORS.signature },
      { name: 'AEAD', value: data.primitives.ae, color: COLORS.ae },
      { name: 'Other', value: data.primitives.other, color: COLORS.other }
    ];
  }, [data]);

  const functionsDonut = useMemo<DonutDatum[]>(() => {
    if (!data) return [];
    const entries = Object.entries(data.functions);
    return entries.map(([name, value], index) => ({
      name,
      value,
      color: COLORS.functions[index % COLORS.functions.length]
    }));
  }, [data]);

  const bubbleData = useMemo<BubbleDatum[]>(() => {
    if (!data) return [];
    return [
      { name: 'Hash', value: data.primitives.hash, color: COLORS.hash },
      { name: 'MAC', value: data.primitives.mac, color: COLORS.mac },
      { name: 'Block', value: data.primitives['block-cipher'], color: COLORS.blockCipher },
      { name: 'PKE', value: data.primitives.pke, color: COLORS.pke },
      { name: 'Sign', value: data.primitives.signature, color: COLORS.signature },
      { name: 'AEAD', value: data.primitives.ae, color: COLORS.ae },
      { name: 'Other', value: data.primitives.other, color: COLORS.other }
    ].filter((item) => item.value > 0);
  }, [data]);

  if (!data) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-header">
          <div>
            <div className="dashboard-title">CBOM Dashboard</div>
            <div className="dashboard-subtitle">Loading crypto coverage snapshot…</div>
          </div>
          <FileUploader onFileLoaded={handleFileLoaded} error={error} activeFile={activeFile} />
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <div className="dashboard-title">CBOM Dashboard</div>
          <div className="dashboard-subtitle">Crypto asset coverage & evidence quality overview</div>
        </div>
        <FileUploader onFileLoaded={handleFileLoaded} error={error} activeFile={activeFile} />
      </div>

      <RepoAnalyzer />

      <div className="card-grid">
        <DonutCard title="Crypto Assets" value={data.totalAssets} data={quantumDonut} />
        <DonutCard title="Crypto Primitives" value={data.totalPrimitives} data={primitivesDonut} />
        <DonutCard title="Crypto Functions" value={data.totalFunctions} data={functionsDonut} />
      </div>

      <div className="chart-row">
        <div className="card bubble-card">
          <div className="card-title">Primitive Distribution</div>
          <BubblePack data={bubbleData} />
        </div>
        <div className="card">
          <LegendPanel
            groups={[
              {
                title: 'Quantum Safety',
                items: [
                  { label: 'Quantum Safe', color: COLORS.quantumSafe },
                  { label: 'Not Quantum Safe', color: COLORS.notQuantumSafe },
                  { label: 'Unknown', color: COLORS.unknown }
                ]
              },
              {
                title: 'Primitive Categories',
                items: [
                  { label: 'Hash', color: COLORS.hash },
                  { label: 'MAC', color: COLORS.mac },
                  { label: 'Block Cipher', color: COLORS.blockCipher },
                  { label: 'PKE', color: COLORS.pke },
                  { label: 'Signature', color: COLORS.signature },
                  { label: 'AEAD', color: COLORS.ae },
                  { label: 'Other', color: COLORS.other }
                ]
              }
            ]}
          />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
