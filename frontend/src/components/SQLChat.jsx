import { useState } from 'react'

function SQLChat() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    if (!question.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question.trim() }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to get response')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      handleSubmit()
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      {/* Header */}
      <header className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-800 border border-slate-700 text-sm text-slate-400 mb-6">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          Powered by Llama 3 + LoRA
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          <span className="gradient-text">Ask your database</span>
          <br />
          <span className="text-slate-100">anything</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto">
          Type a question in plain English. The AI will generate SQL and fetch the results from your sales database.
        </p>
      </header>

      {/* Input Section */}
      <div className="glow rounded-2xl bg-slate-800/80 backdrop-blur border border-slate-700 p-6 mb-8">
        <label className="block text-sm font-medium text-slate-400 mb-3">
          Your question
        </label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="e.g., How many keyboards did we sell last month? Which region has the highest sales?"
          className="w-full h-32 bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500 transition-all resize-none font-sans"
          disabled={loading}
        />
        <div className="flex items-center justify-between mt-4">
          <span className="text-sm text-slate-500">
            Press <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded text-slate-400 text-xs">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded text-slate-400 text-xs">Enter</kbd> to run
          </span>
          <button
            onClick={handleSubmit}
            disabled={loading || !question.trim()}
            className="px-6 py-2.5 bg-gradient-to-r from-sky-500 to-cyan-500 text-slate-900 font-semibold rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Generating...
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Run Query
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="rounded-xl bg-red-500/10 border border-red-500/30 p-4 mb-8">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-red-300">{error}</p>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-6 animate-in fade-in duration-500">
          {/* Generated SQL */}
          <div className="rounded-2xl bg-slate-800/80 backdrop-blur border border-slate-700 overflow-hidden">
            <div className="px-5 py-3 border-b border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <span className="text-sm font-medium text-slate-400">Generated SQL</span>
              </div>
              <button
                onClick={() => navigator.clipboard.writeText(result.generated_sql)}
                className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
              >
                Copy
              </button>
            </div>
            <div className="p-5">
              <pre className="code-block text-cyan-400 whitespace-pre-wrap">
                {result.generated_sql}
              </pre>
            </div>
          </div>

          {/* Results Table */}
          <div className="rounded-2xl bg-slate-800/80 backdrop-blur border border-slate-700 overflow-hidden">
            <div className="px-5 py-3 border-b border-slate-700 flex items-center gap-2">
              <svg className="w-4 h-4 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span className="text-sm font-medium text-slate-400">
                Results ({result.results.length} row{result.results.length !== 1 ? 's' : ''})
              </span>
            </div>
            <div className="overflow-x-auto">
              {result.results.length > 0 ? (
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      {Object.keys(result.results[0]).map((col) => (
                        <th
                          key={col}
                          className="px-5 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50">
                    {result.results.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-700/30 transition-colors">
                        {Object.values(row).map((val, i) => (
                          <td key={i} className="px-5 py-3 text-sm text-slate-100 whitespace-nowrap">
                            {val !== null ? String(val) : <span className="text-slate-500 italic">null</span>}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="px-5 py-8 text-center text-slate-500">
                  No results returned
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="mt-16 text-center text-sm text-slate-500">
        <p>
          NL-to-SQL Demo · Fine-tuned with{' '}
          <span className="text-slate-400">Unsloth</span> +{' '}
          <span className="text-slate-400">LoRA</span>
        </p>
      </footer>
    </div>
  )
}

export default SQLChat
