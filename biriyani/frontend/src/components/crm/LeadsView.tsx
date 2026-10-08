import { useState, useEffect } from 'react'

export function LeadsView() {
  const [leads, setLeads] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchLeads() {
      try {
        setIsLoading(true)
        const q = statusFilter ? `?status=${statusFilter}` : ''
        const res = await fetch(`/api/v1/leads${q}`)
        const json = await res.json()
        if (json.success) {
          setLeads(json.data.items)
          setTotal(json.data.total)
        }
      } catch (err) {
        console.error('Failed to fetch leads:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchLeads()
  }, [statusFilter])

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">Sales Leads</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">Total {total} prospects and inbound inquiries</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-ink-muted-48)] font-medium">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3 py-1.5 text-xs text-[var(--color-ink)] outline-none shadow-2xs"
          >
            <option value="">All Lead Statuses</option>
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="qualified">Qualified</option>
            <option value="unqualified">Unqualified</option>
            <option value="converted">Converted</option>
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-auto rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-2xs">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">
              <th className="p-3.5">Lead Name</th>
              <th className="p-3.5">Company</th>
              <th className="p-3.5">Source</th>
              <th className="p-3.5">Status</th>
              <th className="p-3.5">Date Added</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-hairline)]">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  Loading leads…
                </td>
              </tr>
            ) : leads.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  No matching leads found.
                </td>
              </tr>
            ) : (
              leads.map((l) => (
                <tr key={l.id} className="hover:bg-[var(--color-canvas-parchment)]/60 transition">
                  <td className="p-3.5 font-semibold text-[var(--color-ink)]">{l.name}</td>
                  <td className="p-3.5 font-medium text-[var(--color-ink-muted-80)]">{l.company}</td>
                  <td className="p-3.5 text-xs uppercase font-mono text-[var(--color-ink-muted-48)]">{l.source}</td>
                  <td className="p-3.5">
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold uppercase bg-purple-500/10 text-purple-600">
                      {l.status}
                    </span>
                  </td>
                  <td className="p-3.5 text-xs text-[var(--color-ink-muted-80)]">
                    {l.created_at ? new Date(l.created_at).toLocaleDateString() : 'N/A'}
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
