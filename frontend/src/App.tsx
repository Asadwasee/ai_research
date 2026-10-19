import { useState, useRef } from 'react';
import { Search, Loader2, BookOpen, Activity, CheckCircle2, AlertCircle } from 'lucide-react';
import ReportViewer from './ReportViewer';

interface ProgressEvent {
  status: string;
  node?: string;
  detail?: string;
  feedback?: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('quick');
  const [isResearching, setIsResearching] = useState(false);
  const [progressLogs, setProgressLogs] = useState<ProgressEvent[]>([]);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    // Reset states for new research
    setIsResearching(true);
    setProgressLogs([]);
    setReport(null);
    setError(null);

    abortControllerRef.current = new AbortController();

    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${API_BASE_URL}/api/v1/research/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, mode }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status} ${response.statusText}`);
      }

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Parse SSE lines (data: {...}\n\n)
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // Keep the last incomplete chunk in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.status === 'completed' && data.report) {
                setReport(data.report);
              } else if (data.status === 'error') {
                setError(data.detail || 'Workflow error occurred.');
              } else {
                setProgressLogs((prev) => [...prev, data]);
              }
            } catch (err) {
              console.error("Failed to parse stream data:", err);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('Request aborted');
      } else {
        setError(err.message || "An unexpected error occurred.");
      }
    } finally {
      setIsResearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 font-sans selection:bg-indigo-100 selection:text-indigo-900 pb-20">
      <header className="bg-white border-b border-zinc-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center gap-3">
          <div className="bg-indigo-600 p-1.5 rounded-lg">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-lg font-semibold tracking-tight">AI Research Agent</h1>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Search Input Section */}
        <section className="bg-white rounded-2xl shadow-sm border border-zinc-200 p-6 transition-all">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label htmlFor="query" className="text-sm font-medium text-zinc-700">
                Research Topic
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="w-5 h-5 text-zinc-400" />
                </div>
                <input
                  id="query"
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter a complex topic to research..."
                  className="w-full pl-10 pr-4 py-3 bg-zinc-50 border border-zinc-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-colors"
                  disabled={isResearching}
                />
              </div>
            </div>

            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex gap-2">
                {['quick', 'standard', 'deep'].map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setMode(m)}
                    disabled={isResearching}
                    className={`px-4 py-2 text-sm font-medium rounded-lg capitalize transition-colors ${
                      mode === m ? 'bg-zinc-900 text-white' : 'bg-zinc-100 text-zinc-600 hover:bg-zinc-200'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>

              <button
                type="submit"
                disabled={!query.trim() || isResearching}
                className="px-6 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
              >
                {isResearching ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Researching...
                  </>
                ) : (
                  'Start Research'
                )}
              </button>
            </div>
          </form>
        </section>

        {/* Progress & Error Display */}
        {(progressLogs.length > 0 || error) && !report && (
          <section className="bg-white rounded-2xl shadow-sm border border-zinc-200 p-6">
            <h2 className="text-sm font-semibold text-zinc-900 mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-600" />
              Workflow Execution
            </h2>
            <div className="space-y-3 font-mono text-sm">
              {progressLogs.map((log, idx) => (
                <div key={idx} className="flex items-start gap-3 text-zinc-600">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 mt-0.5 shrink-0" />
                  <div>
                    <span className="font-medium text-zinc-900 capitalize">{log.node}</span>
                    <span className="text-zinc-500 ml-2">[{log.status}]</span>
                    {log.feedback && (
                      <div className="mt-1 text-amber-600 bg-amber-50 p-2 rounded border border-amber-200 text-xs">
                        Correction needed: {log.feedback}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {error && (
                <div className="flex items-start gap-3 text-red-600 bg-red-50 p-3 rounded-lg border border-red-200">
                  <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                  <div>
                    <span className="font-semibold block">Execution Error</span>
                    {error}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {/* Final Report Display */}
        {report && <ReportViewer report={report} />}
      </main>
    </div>
  );
}

export default App;