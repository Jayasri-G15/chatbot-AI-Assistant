import { useState } from 'react'

interface QueryData {
  answer: string
  crm_tool: string
  crm_results: any
  source: string
  agent_trace: Array<{ agent: string; action: string }>
}

export function CRMAssistantView() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState<QueryData | null>(null)
  const [error, setError] = useState<string | null>(null)

  const sampleQueries = [
    'How many total users signed up?',
    'Show subscription breakdown across tiers',
    'How many users are on the Pro plan?',
    'Show total payment revenue and count',
    'Find users who have not logged in recently',
  ]

  const handleQuery = async (qStr: string) => {
    if (!qStr.trim() || isLoading) return
    setIsLoading(true)
    setError(null)
    setData(null)

    try {
      const token = localStorage.getItem('crm_auth_token') || localStorage.getItem('token') || ''
      const res = await fetch('/api/v1/admin/assistant/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query: qStr.trim() }),
      })

      if (!res.ok) {
        if (res.status === 403) {
          throw new Error('Access Denied: Admin privileges required for AI CRM queries.')
        }
        throw new Error(`Query failed with status ${res.status}`)
      }

      const json = await res.json().catch(() => ({}))
      if (json.success && json.data) {
        setData(json.data)
      } else {
        throw new Error(json.error?.message || 'Failed to process CRM query.')
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred while querying the CRM Assistant.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex h-full flex-col bg-[var(--color-canvas)] p-6 rounded-2xl border border-[var(--color-hairline)] shadow-xs overflow-y-auto">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-2xl">🤖</span>
        <div>
          <h2 className="text-lg font-bold text-[var(--color-ink)]">Admin AI CRM Assistant</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">
            Ask natural-language questions grounded strictly in authorized real database records.
          </p>
        </div>
      </div>

      {/* Suggested Quick Queries */}
      <div className="mb-6 flex flex-wrap gap-2">
        {sampleQueries.map((q, idx) => (
          <button
            key={idx}
            onClick={() => {
              setQuery(q)
              handleQuery(q)
            }}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-[var(--color-canvas-parchment)] border border-[var(--color-hairline)] text-[var(--color-ink)] hover:bg-[var(--color-primary-light,#eef2ff)] hover:text-[var(--color-primary)] transition disabled:opacity-50"
          >
            💡 {q}
          </button>
        ))}
      </div>

      {/* Query Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault()
          handleQuery(query)
        }}
        className="flex gap-2 mb-6"
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a CRM question (e.g. How many users signed up this month?)..."
          disabled={isLoading}
          className="flex-1 px-4 py-2.5 rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] text-sm text-[var(--color-ink)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="px-5 py-2.5 rounded-xl bg-[var(--color-primary)] text-white text-sm font-semibold hover:opacity-90 transition disabled:opacity-50"
        >
          {isLoading ? 'Analyzing CRM…' : 'Query CRM'}
        </button>
      </form>

      {/* Error View */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm font-medium mb-4">
          ⚠️ {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center gap-3 p-6 justify-center bg-[var(--color-canvas-parchment)] rounded-xl border border-[var(--color-hairline)]">
          <div className="w-5 h-5 border-2 border-[var(--color-primary)] border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-[var(--color-ink-muted-48)] font-medium">
            Analyzing real PostgreSQL database aggregates via read-only tools…
          </span>
        </div>
      )}

      {/* Results View */}
      {data && !isLoading && (
        <div className="space-y-4">
          {/* Grounded Text Answer */}
          <div className="p-4 rounded-xl bg-[var(--color-canvas-parchment)] border border-[var(--color-hairline)]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-primary)]">
                Grounded Answer
              </span>
              <span className="text-xs text-[var(--color-ink-muted-48)]">
                Source: {data.source}
              </span>
            </div>
            <p className="text-sm font-medium text-[var(--color-ink)] leading-relaxed">
              {data.answer}
            </p>
          </div>

          {/* Agent Trace */}
          {data.agent_trace && data.agent_trace.length > 0 && (
            <div className="p-4 rounded-xl bg-[var(--color-canvas-parchment)] border border-[var(--color-hairline)]">
              <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-ink-muted-48)] block mb-2">
                Execution Audit Trail
              </span>
              <div className="space-y-1.5">
                {data.agent_trace.map((step, idx) => (
                  <div key={idx} className="text-xs text-[var(--color-ink-muted-48)] flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]" />
                    <span className="font-semibold text-[var(--color-ink)]">{step.agent}:</span> {step.action}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw Structured Data Result */}
          {data.crm_results && (
            <div className="p-4 rounded-xl bg-[var(--color-canvas-parchment)] border border-[var(--color-hairline)]">
              <span className="text-xs font-bold uppercase tracking-wider text-[var(--color-ink-muted-48)] block mb-2">
                Tool Data Output (`{data.crm_tool}`)
              </span>
              <pre className="text-xs bg-[var(--color-canvas)] p-3 rounded-lg overflow-x-auto text-[var(--color-ink)] font-mono">
                {JSON.stringify(data.crm_results, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
