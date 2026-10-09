import { useState, useEffect } from 'react'

export function SubscriptionsView() {
  const [subscriptions, setSubscriptions] = useState<any[]>([])
  const [breakdown, setBreakdown] = useState<any>({})
  const [planFilter, setPlanFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchSubscriptions() {
      try {
        setIsLoading(true)
        const token = localStorage.getItem('crm_auth_token')
        const params = new URLSearchParams()
        if (planFilter) params.append('plan', planFilter)
        const res = await fetch(`/api/v1/admin/subscriptions?${params.toString()}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        const json = await res.json().catch(() => ({}))
        if (json.success || json.data) {
          const d = json.data || json
          setSubscriptions(d.items || d.subscriptions || [])
          setBreakdown(d.plan_breakdown || {})
        }
      } catch (err) {
        console.error('Failed to fetch subscriptions:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchSubscriptions()
  }, [planFilter])

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Plan Distribution Header Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {['FREE', 'PRO', 'PREMIUM', 'ENTERPRISE'].map((plan) => (
          <div key={plan} className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
            <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase">{plan} Plan Users</span>
            <p className="text-xl font-bold text-[var(--color-ink)] mt-1">{breakdown[plan] || 0}</p>
          </div>
        ))}
      </div>

      {/* Filter Header */}
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">Subscriptions Directory</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">Active subscription plans linked to registered CRM users</p>
        </div>
        <select
          value={planFilter}
          onChange={(e) => setPlanFilter(e.target.value)}
          className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3 py-1.5 text-xs text-[var(--color-ink)] outline-none shadow-2xs"
        >
          <option value="">All Subscription Plans</option>
          <option value="FREE">FREE</option>
          <option value="PRO">PRO</option>
          <option value="PREMIUM">PREMIUM</option>
          <option value="ENTERPRISE">ENTERPRISE</option>
        </select>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-2xs">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">
              <th className="p-3">User</th>
              <th className="p-3">Email</th>
              <th className="p-3">Plan</th>
              <th className="p-3">Status</th>
              <th className="p-3">Billing Cycle</th>
              <th className="p-3">Start Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-hairline)]">
            {isLoading ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  Loading subscriptions…
                </td>
              </tr>
            ) : subscriptions.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  No subscription records found.
                </td>
              </tr>
            ) : (
              subscriptions.map((s) => (
                <tr key={s.id} className="hover:bg-[var(--color-canvas-parchment)]/60 transition">
                  <td className="p-3 font-semibold text-[var(--color-ink)]">{s.user_name || 'N/A'}</td>
                  <td className="p-3 text-[var(--color-ink-muted-80)]">{s.user_email || 'N/A'}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      s.plan === 'PRO' ? 'bg-purple-500/10 text-purple-600' :
                      s.plan === 'PREMIUM' ? 'bg-indigo-500/10 text-indigo-600' :
                      'bg-gray-500/10 text-gray-600'
                    }`}>
                      {s.plan}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-600">
                      {s.status}
                    </span>
                  </td>
                  <td className="p-3 font-medium text-[var(--color-ink-muted-80)]">{s.billing_cycle || 'MONTHLY'}</td>
                  <td className="p-3 text-[var(--color-ink-muted-48)]">
                    {s.start_date ? new Date(s.start_date).toLocaleDateString() : 'N/A'}
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
