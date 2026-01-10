import { FormEvent, useEffect, useRef, useState } from 'react';

const stepLabels = [
  'Provide repository URL and branch',
  'Checkout branch',
  'Analyze crypto assets',
  'Prepare CBOM dashboard'
];

type RunSummary = {
  repoUrl: string;
  branch: string;
  submittedAt: string;
};

const RepoAnalyzer = () => {
  const [repoUrl, setRepoUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [activeStep, setActiveStep] = useState(0);
  const [runSummary, setRunSummary] = useState<RunSummary | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const timersRef = useRef<number[]>([]);

  useEffect(() => {
    return () => {
      timersRef.current.forEach((timer) => window.clearTimeout(timer));
    };
  }, []);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!repoUrl.trim()) return;
    timersRef.current.forEach((timer) => window.clearTimeout(timer));
    timersRef.current = [];
    setActiveStep(1);
    setIsRunning(true);
    setRunSummary({
      repoUrl: repoUrl.trim(),
      branch: branch.trim() || 'main',
      submittedAt: new Date().toLocaleString()
    });

    timersRef.current.push(
      window.setTimeout(() => setActiveStep(2), 900),
      window.setTimeout(() => setActiveStep(3), 1800),
      window.setTimeout(() => setIsRunning(false), 2400)
    );
  };

  const handleReset = () => {
    timersRef.current.forEach((timer) => window.clearTimeout(timer));
    timersRef.current = [];
    setIsRunning(false);
    setActiveStep(0);
    setRunSummary(null);
    setRepoUrl('');
    setBranch('main');
  };

  return (
    <div className="card repo-card">
      <div className="card-title">Repository Intake</div>
      <form className="repo-form" onSubmit={handleSubmit}>
        <label className="field">
          <span className="field-label">Git repository URL</span>
          <input
            type="url"
            placeholder="https://github.com/org/project.git"
            value={repoUrl}
            onChange={(event) => setRepoUrl(event.target.value)}
            required
            disabled={isRunning}
          />
        </label>
        <label className="field">
          <span className="field-label">Branch name</span>
          <input
            type="text"
            placeholder="main"
            value={branch}
            onChange={(event) => setBranch(event.target.value)}
            disabled={isRunning}
          />
        </label>
        <div className="button-row">
          <button className="primary-button" type="submit" disabled={isRunning}>
            {isRunning ? 'Running analysis…' : 'Checkout & Analyze'}
          </button>
          {runSummary && (
            <button className="secondary-button" type="button" onClick={handleReset} disabled={isRunning}>
              New analysis
            </button>
          )}
        </div>
      </form>
      {runSummary ? (
        <div className="repo-status">
          <div className="status-summary">
            <span>Queued analysis for</span>
            <strong>{runSummary.repoUrl}</strong>
            <span>on</span>
            <strong>{runSummary.branch}</strong>
            <span className="muted">({runSummary.submittedAt})</span>
            <span className="status-pill">{isRunning ? 'In progress' : 'Ready'}</span>
          </div>
        </div>
      ) : (
        <div className="repo-status muted">
          Provide a repo and branch to trigger checkout and crypto asset analysis.
        </div>
      )}
      <ol className="repo-steps">
        {stepLabels.map((label, index) => (
          <li
            key={label}
            className={index < activeStep ? 'completed' : index === activeStep ? 'active' : 'pending'}
          >
            <span className="step-index">{index + 1}</span>
            <span>{label}</span>
          </li>
        ))}
      </ol>
    </div>
  );
};

export default RepoAnalyzer;
