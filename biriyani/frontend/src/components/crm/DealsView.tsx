import { useState, useEffect } from 'react'

export function DealsView() {
  const [deals, setDeals] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [summary, setSummary] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchDeals() {
      try {
        setIsLoading(true)
        const q = statusFilter ? `?status=${statusFilter}` : ''
        const res = await fetch(`/api/v1/deals${q}`)
        const json = await res.json()
        if (json.success) {
          setDeals(json.data.items)
          setTotal(json.data.total)
        }

        const sumRes = await fetch('/api/v1/deals/summary')
        const sumJson = await sumRes.json()
        if (sumJson.success) {
          setSummary(sumJson.data)
        }
      } catch (err) {
        console.error('Failed to fetch deals:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchDeals()
  }, [statusFilter])

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Metrics Banner */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
            <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Open Pipeline Value</span>
            <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
              ₹{(summary.total_open_pipeline_value || 0).toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
            <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Won Deals Value</span>
            <p className="text-xl font-bold text-blue-600 dark:text-blue-400 mt-1">
              ₹{(summary.total_won_value || 0).toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
            <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Open Deals Count</span>
            <p className="text-xl font-bold text-[var(--color-ink)] mt-1">{summary.total_open_deals || 0}</p>
          </div>
          <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
            <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Total Accounts</span>
            <p className="text-xl font-bold text-[var(--color-ink)] mt-1">{summary.total_customers || 0}</p>
          </div>
        </div>
      )}

      {/* Filter Controls */}
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">Deals & Opportunities</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">Total {total} deals matching filter</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-ink-muted-48)] font-medium">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3 py-1.5 text-xs text-[var(--color-ink)] outline-none shadow-2xs"
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="won">Won</option>
            <option value="lost">Lost</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-2xs">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">
              <th className="p-3.5">Deal Title</th>
              <th className="p-3.5">Customer</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5">Close Date</th>
              <th className="p-3.5 text-right">Value</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-hairline)]">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  Loading deals…
                </td>
              </tr>
            ) : deals.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  No matching deals found.
                </td>
              </tr>
            ) : (
              deals.map((d) => (
                <tr key={d.id} className="hover:bg-[var(--color-canvas-parchment)]/60 transition">
                  <td className="p-3.5 font-semibold text-[var(--color-ink)]">{d.title}</td>
                  <td className="p-3.5">
                    <p className="font-medium text-[var(--color-ink)]">{d.customer_name}</p>
                    <p className="text-xs text-[var(--color-ink-muted-48)]">{d.company}</p>
                  </td>
                  <td className="p-3.5">
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                        d.status === 'won'
                          ? 'bg-emerald-500/10 text-emerald-600'
                          : d.status === 'lost'
                          ? 'bg-red-500/10 text-red-600'
                          : 'bg-amber-500/10 text-amber-600'
                      }`}
                    >
                      {d.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-xs text-[var(--color-ink-muted-80)]">
                    {d.close_date ? new Date(d.close_date).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="p-3.5 text-right font-bold text-emerald-600 dark:text-emerald-400">
                    ₹{d.value.toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
