import { useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

export default function UploadDataset() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(null);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      if (res.ok) {
        if (data.status === 'preview') {
          setPreview(data);
        } else if (data.status === 'complete') {
          setResult(data);
          setFile(null);
        }
      } else {
        setError(data.error || 'Upload failed');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleConfirm = async () => {
    setUploading(true);

    try {
      const res = await fetch('http://localhost:5000/api/upload/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: preview.filename })
      });

      const data = await res.json();

      if (res.ok) {
        setResult(data);
        setPreview(null);
        setFile(null);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Confirmation failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">Upload Dataset</h2>

      {/* Upload Section */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          
          <input
            type="file"
            accept=".csv,.xlsx,.xls,.json"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          
          <label
            htmlFor="file-upload"
            className="cursor-pointer text-green-500 hover:text-green-400"
          >
            Choose File
          </label>
          
          {file && (
            <div className="mt-4 flex items-center justify-center gap-2 text-gray-300">
              <FileText className="h-5 w-5" />
              <span>{file.name}</span>
              <span className="text-gray-500">({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="mt-4 w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 
                     text-white px-4 py-2 rounded transition"
        >
          {uploading ? 'Processing...' : 'Upload & Validate'}
        </button>

        <p className="text-xs text-gray-400 mt-2">
          Supported formats: CSV, Excel, JSON. Max 500,000 rows.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 mb-6 flex items-start gap-3">
          <XCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-400">Upload Failed</p>
            <p className="text-sm text-gray-300">{error}</p>
          </div>
        </div>
      )}

      {/* Preview Section */}
      {preview && (
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="h-5 w-5 text-yellow-500" />
            <h3 className="text-lg font-semibold">Preview & Confirm</h3>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
            <div>
              <span className="text-gray-400">Total Rows:</span>
              <span className="ml-2 font-semibold">{preview.statistics.total_rows.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-gray-400">Classification:</span>
              <span className="ml-2 font-semibold">
                {preview.statistics.needs_classification ? 'ML Auto-Classify' : 'Manual'}
              </span>
            </div>
          </div>

          {preview.statistics.warnings?.length > 0 && (
            <div className="bg-yellow-900/30 border border-yellow-700 rounded p-3 mb-4">
              <p className="text-sm text-yellow-400">
                {preview.statistics.warnings.join(', ')}
              </p>
            </div>
          )}

          <div className="overflow-x-auto mb-4">
            <table className="w-full text-sm">
              <thead className="bg-gray-700">
                <tr>
                  {Object.keys(preview.preview[0] || {}).slice(0, 5).map(col => (
                    <th key={col} className="px-3 py-2 text-left">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {preview.preview.slice(0, 3).map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).slice(0, 5).map((val, i) => (
                      <td key={i} className="px-3 py-2 text-gray-300 truncate max-w-xs">
                        {String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={handleConfirm}
            disabled={uploading}
            className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded transition"
          >
            Confirm & Process
          </button>
        </div>
      )}

      {/* Success Result */}
      {result && (
        <div className="bg-green-900/30 border border-green-700 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-6 w-6 text-green-500 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-green-400 mb-2">Upload Complete</h3>
              
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-gray-400">Rows Inserted:</span>
                  <span className="ml-2 font-semibold text-white">
                    {result.inserted_rows?.toLocaleString() || result.total_rows?.toLocaleString()}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Method:</span>
                  <span className="ml-2 font-semibold text-white">
                    {result.classification_method || 'Unknown'}
                  </span>
                </div>
              </div>

              {result.low_confidence_count > 0 && (
                <p className="text-yellow-400 text-sm mt-2">
                  {result.low_confidence_count} records flagged for review (low confidence)
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}