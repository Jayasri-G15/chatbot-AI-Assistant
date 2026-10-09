import { useState, useEffect } from 'react'

export function PaymentsView() {
  const [payments, setPayments] = useState<any[]>([])
  const [metrics, setMetrics] = useState<any>({})
  const [statusFilter, setStatusFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchPayments() {
      try {
        setIsLoading(true)
        const token = localStorage.getItem('crm_auth_token')
        const params = new URLSearchParams()
        if (statusFilter) params.append('status', statusFilter)
        const res = await fetch(`/api/v1/admin/payments?${params.toString()}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        const json = await res.json()
        if (json.success || json.data) {
          const d = json.data || json
          setPayments(d.items || d.payments || [])
          setMetrics({
            total_amount: d.total_revenue || d.total_amount || 0,
            paid_count: d.paid_count || 0,
            pending_count: d.pending_count || 0,
          })
        }
      } catch (err) {
        console.error('Failed to fetch payments:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchPayments()
  }, [statusFilter])

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase">Total Revenue</span>
          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
            ₹{(metrics.total_amount || 0).toLocaleString()}
          </p>
        </div>
        <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase">Successful Transactions</span>
          <p className="text-2xl font-bold text-[var(--color-ink)] mt-1">{metrics.paid_count || 0}</p>
        </div>
        <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase">Pending Transactions</span>
          <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">{metrics.pending_count || 0}</p>
        </div>
      </div>

      {/* Filter Header */}
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">Payment History & Ledger</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">Safe reference ledger (No credit card or CVV details stored)</p>
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3 py-1.5 text-xs text-[var(--color-ink)] outline-none shadow-2xs"
        >
          <option value="">All Payment Statuses</option>
          <option value="PAID">PAID</option>
          <option value="PENDING">PENDING</option>
          <option value="FAILED">FAILED</option>
          <option value="REFUNDED">REFUNDED</option>
        </select>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-2xs">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">
              <th className="p-3">Customer</th>
              <th className="p-3">Provider Ref ID</th>
              <th className="p-3">Amount</th>
              <th className="p-3">Status</th>
              <th className="p-3">Payment Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-hairline)]">
            {isLoading ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  Loading payment history…
                </td>
              </tr>
            ) : payments.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  No payment records found.
                </td>
              </tr>
            ) : (
              payments.map((p) => (
                <tr key={p.id} className="hover:bg-[var(--color-canvas-parchment)]/60 transition">
                  <td className="p-3 font-semibold text-[var(--color-ink)]">{p.user_name || p.user_email || 'N/A'}</td>
                  <td className="p-3 font-mono text-[11px] text-[var(--color-ink-muted-48)]">{p.provider_payment_id || p.id}</td>
                  <td className="p-3 font-bold text-emerald-600 dark:text-emerald-400">
                    ₹{p.amount ? p.amount.toLocaleString() : '0'} {p.currency || 'INR'}
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      p.status === 'PAID' ? 'bg-emerald-500/10 text-emerald-600' :
                      p.status === 'PENDING' ? 'bg-amber-500/10 text-amber-600' :
                      'bg-red-500/10 text-red-600'
                    }`}>
                      {p.status}
                    </span>
                  </td>
                  <td className="p-3 text-[var(--color-ink-muted-48)]">
                    {p.payment_date ? new Date(p.payment_date).toLocaleString() : 'N/A'}
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
