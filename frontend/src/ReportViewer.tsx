import { useState } from 'react';
import { Book, Link as LinkIcon, FileText, CheckCircle, Copy, Download, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface ReportViewerProps {
  report: any;
}

export default function ReportViewer({ report }: ReportViewerProps) {
  const [isCopied, setIsCopied] = useState(false);

  if (!report) return null;

  // Utility to convert report object into a clean Markdown string
  const getMarkdownText = () => {
    let md = `# ${report.query}\n\n`;
    md += `*Generated on ${new Date(report.generated_at).toLocaleString()} • ${report.mode} mode*\n\n`;
    
    md += `## Executive Summary\n${report.executive_summary}\n\n`;
    
    report.sections.forEach((sec: any) => {
      md += `## ${sec.title}\n${sec.content}\n\n`;
    });
    
    md += `## Sources & References\n`;
    report.sources.forEach((src: any) => {
      md += `- [${src.title}](${src.url})\n`;
    });
    
    return md;
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(getMarkdownText());
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([getMarkdownText()], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.query.replace(/\s+/g, '-').toLowerCase()}-research.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const MarkdownComponents = {
    p: ({ node, ...props }: any) => <p className="mb-3 last:mb-0 leading-relaxed" {...props} />,
    ul: ({ node, ...props }: any) => <ul className="list-disc pl-5 mb-3 space-y-1" {...props} />,
    ol: ({ node, ...props }: any) => <ol className="list-decimal pl-5 mb-3 space-y-1" {...props} />,
    li: ({ node, ...props }: any) => <li className="text-zinc-700" {...props} />,
    strong: ({ node, ...props }: any) => <strong className="font-semibold text-zinc-900" {...props} />,
    a: ({ node, ...props }: any) => <a className="text-indigo-600 hover:underline font-medium" target="_blank" rel="noreferrer" {...props} />
  };

  return (
    <article className="bg-white rounded-2xl shadow-sm border border-zinc-200 overflow-hidden transition-all animate-in fade-in duration-500">
      
      {/* Header Section */}
      <div className="bg-zinc-900 px-8 py-10 text-white">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-indigo-400 mb-4 text-sm font-medium">
              <CheckCircle className="w-4 h-4" />
              <span>Research Complete</span>
            </div>
            <h1 className="text-3xl font-semibold tracking-tight leading-tight mb-2">
              {report.query}
            </h1>
            <p className="text-zinc-400 text-sm">
              Generated on {new Date(report.generated_at).toLocaleString()} • {report.mode} mode
            </p>
          </div>
          
          {/* Action Buttons */}
          <div className="flex items-center gap-2 shrink-0">
            <button 
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white rounded-xl text-sm font-medium transition-colors"
            >
              {isCopied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              {isCopied ? 'Copied' : 'Copy'}
            </button>
            <button 
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 hover:text-white rounded-xl text-sm font-medium transition-colors"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
          </div>
        </div>
      </div>

      <div className="p-8 space-y-10">
        
        {/* Executive Summary */}
        <section className="bg-indigo-50/50 border border-indigo-100 p-6 rounded-xl text-indigo-950">
          <h3 className="font-semibold mb-3 flex items-center gap-2 text-indigo-900">
            <Book className="w-4 h-4" /> 
            Executive Summary
          </h3>
          <div className="text-sm text-indigo-950/90">
            <ReactMarkdown components={MarkdownComponents}>
              {report.executive_summary}
            </ReactMarkdown>
          </div>
        </section>

        {/* Report Sections */}
        <div className="space-y-8">
          {report.sections.map((sec: any, idx: number) => (
            <section key={idx}>
              <h2 className="text-xl font-semibold text-zinc-900 mb-3">
                {sec.title}
              </h2>
              <div className="text-zinc-600 text-sm">
                <ReactMarkdown components={MarkdownComponents}>
                  {sec.content}
                </ReactMarkdown>
              </div>
            </section>
          ))}
        </div>

        <hr className="border-zinc-100" />

        {/* References / Sources */}
        <section>
          <h3 className="text-lg font-semibold text-zinc-900 mb-4 flex items-center gap-2">
            <FileText className="w-4 h-4 text-zinc-500" /> 
            Sources & References
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {report.sources.map((src: any) => (
              <a 
                key={src.source_id} 
                href={src.url} 
                target="_blank" 
                rel="noreferrer" 
                className="flex items-start gap-3 p-4 rounded-xl border border-zinc-200 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all group"
              >
                <div className="bg-zinc-100 p-2 rounded-lg group-hover:bg-indigo-100 transition-colors shrink-0">
                  <LinkIcon className="w-4 h-4 text-zinc-500 group-hover:text-indigo-600" />
                </div>
                <div className="min-w-0">
                  <p className="font-medium text-zinc-900 text-sm truncate">
                    {src.title}
                  </p>
                  {src.url && (
                    <p className="text-xs text-zinc-500 mt-1 truncate">
                      {new URL(src.url).hostname}
                    </p>
                  )}
                </div>
              </a>
            ))}
          </div>
        </section>

      </div>
    </article>
  );
}