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
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
      {/* Header */}
      <header className="mb-8 border-b border-slate-700 pb-6">
        <h1 className="text-2xl font-semibold text-slate-100 mb-2">
          SQL Query Assistant
        </h1>
        <p className="text-sm text-slate-400">
          Query your sales database using natural language
        </p>
      </header>

      {/* Input Section */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-5 mb-6">
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Enter your question
        </label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Example: How many products do we have? What is the total sales by region?"
          className="w-full h-28 bg-slate-900 border border-slate-600 rounded-md px-3 py-2.5 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none text-sm"
          disabled={loading}
        />
        <div className="flex items-center justify-between mt-3">
          <span className="text-xs text-slate-500">
            <kbd className="px-1.5 py-0.5 bg-slate-700 rounded text-slate-400 text-xs font-mono">Ctrl+Enter</kbd> to execute
          </span>
          <button
            onClick={handleSubmit}
            disabled={loading || !question.trim()}
            className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Running...
              </>
            ) : (
              'Run Query'
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-800 rounded-md p-4 mb-6">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-300 mb-1">Error</p>
              <p className="text-sm text-red-400">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="space-y-4">
          {/* Generated SQL */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 bg-slate-700/30 border-b border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">SQL Query</span>
              </div>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(result.generated_sql)
                  // Simple feedback - could add toast notification
                }}
                className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
              >
                Copy
              </button>
            </div>
            <div className="p-4">
              <pre className="text-sm text-slate-200 font-mono whitespace-pre-wrap overflow-x-auto">
                {result.generated_sql}
              </pre>
            </div>
          </div>

          {/* Results Table */}
          <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 bg-slate-700/30 border-b border-slate-700">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                Results ({result.results.length} {result.results.length === 1 ? 'row' : 'rows'})
              </span>
            </div>
            <div className="overflow-x-auto">
              {result.results.length > 0 ? (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-slate-700/30 border-b border-slate-700">
                      {Object.keys(result.results[0]).map((col) => (
                        <th
                          key={col}
                          className="px-4 py-2.5 text-left text-xs font-medium text-slate-400 uppercase tracking-wide"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700">
                    {result.results.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-700/50 transition-colors">
                        {Object.values(row).map((val, i) => (
                          <td key={i} className="px-4 py-2.5 text-slate-200 whitespace-nowrap">
                            {val !== null ? String(val) : <span className="text-slate-500">—</span>}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="px-4 py-8 text-center text-sm text-slate-500">
                  No results returned
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SQLChat
