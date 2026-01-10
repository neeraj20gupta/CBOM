import { ChangeEvent } from 'react';

type FileUploaderProps = {
  onFileLoaded: (payload: unknown, fileName: string) => void;
  error?: string | null;
  activeFile?: string | null;
};

const FileUploader = ({ onFileLoaded, error, activeFile }: FileUploaderProps) => {
  const handleChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    const parsed = JSON.parse(text);
    onFileLoaded(parsed, file.name);
  };

  return (
    <div>
      <div className="file-uploader">
        <input type="file" accept="application/json" onChange={handleChange} />
        <span className="file-status">
          {activeFile ? `Loaded: ${activeFile}` : 'Using sample.json'}
        </span>
      </div>
      {error && <div className="notice">{error}</div>}
    </div>
  );
};

export default FileUploader;
