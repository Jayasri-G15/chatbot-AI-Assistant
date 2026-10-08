import { useState, useEffect } from 'react'
import { CustomerDetailModal } from './CustomerDetailModal'

export function CustomerList() {
  const [customers, setCustomers] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null)

  useEffect(() => {
    async function fetchCustomers() {
      try {
        setIsLoading(true)
        const res = await fetch(`/api/v1/customers?search=${encodeURIComponent(search)}&page=${page}&limit=10`)
        const json = await res.json()
        if (json.success) {
          setCustomers(json.data.items)
          setTotal(json.data.total)
        }
      } catch (err) {
        console.error('Failed to fetch customers:', err)
      } finally {
        setIsLoading(false)
      }
    }
    const timer = setTimeout(fetchCustomers, 300)
    return () => clearTimeout(timer)
  }, [search, page])

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Top Header & Search bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">Customers Directory</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">
            Total {total} account{total !== 1 ? 's' : ''} registered
          </p>
        </div>
        <div className="relative w-full sm:w-72">
          <input
            type="text"
            placeholder="Search customers, company, email…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3.5 py-2 text-sm text-[var(--color-ink)] placeholder-[var(--color-ink-muted-48)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)] shadow-2xs"
          />
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-2xs">
        <table className="w-full text-left text-sm border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">
              <th className="p-3.5">Customer / Company</th>
              <th className="p-3.5">Email</th>
              <th className="p-3.5">Phone</th>
              <th className="p-3.5">Deals</th>
              <th className="p-3.5">Open Pipeline</th>
              <th className="p-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-hairline)]">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  Loading customers…
                </td>
              </tr>
            ) : customers.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  No matching customers found.
                </td>
              </tr>
            ) : (
              customers.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => setSelectedCustomerId(c.id)}
                  className="hover:bg-[var(--color-canvas-parchment)]/60 cursor-pointer transition"
                >
                  <td className="p-3.5">
                    <p className="font-semibold text-[var(--color-ink)]">{c.name}</p>
                    <p className="text-xs text-[var(--color-ink-muted-48)]">{c.company}</p>
                  </td>
                  <td className="p-3.5 text-[var(--color-ink-muted-80)]">{c.email}</td>
                  <td className="p-3.5 text-[var(--color-ink-muted-80)] font-mono text-xs">{c.phone || '—'}</td>
                  <td className="p-3.5 font-medium">{c.deals_count}</td>
                  <td className="p-3.5 font-bold text-emerald-600 dark:text-emerald-400">
                    ₹{c.open_deal_value.toLocaleString()}
                  </td>
                  <td className="p-3.5 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedCustomerId(c.id)
                      }}
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-[var(--color-primary)]/10 text-[var(--color-primary)] hover:bg-[var(--color-primary)]/20 transition"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-xs text-[var(--color-ink-muted-48)] pt-1">
        <span>Showing page {page} of {Math.ceil(total / 10) || 1}</span>
        <div className="flex gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage(p => p - 1)}
            className="px-3 py-1.5 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas)] disabled:opacity-40 hover:bg-[var(--color-canvas-parchment)] transition"
          >
            Previous
          </button>
          <button
            disabled={page >= Math.ceil(total / 10)}
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1.5 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas)] disabled:opacity-40 hover:bg-[var(--color-canvas-parchment)] transition"
          >
            Next
          </button>
        </div>
      </div>

      {selectedCustomerId && (
        <CustomerDetailModal customerId={selectedCustomerId} onClose={() => setSelectedCustomerId(null)} />
      )}
    </div>
  )
}
