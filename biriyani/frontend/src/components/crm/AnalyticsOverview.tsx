import { useState, useEffect } from 'react'

export function AnalyticsOverview() {
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        setIsLoading(true)
        const token = localStorage.getItem('crm_auth_token')
        const res = await fetch('/api/v1/admin/analytics', {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        const json = await res.json().catch(() => ({}))
        if (!res.ok) {
          throw new Error(json.detail?.error?.message || (typeof json.detail === 'string' ? json.detail : null) || json.error?.message || 'Failed to load analytics')
        }
        setData(json.data || json)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setIsLoading(false)
      }
    }
    fetchAnalytics()
  }, [])

  if (isLoading) {
    return <div className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">Loading CRM Analytics…</div>
  }

  if (error) {
    return (
      <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-600 text-sm font-medium">
        ⚠️ {error}
      </div>
    )
  }

  const overview = data?.overview || {}
  const subs = data?.subscriptions_breakdown || {}

  return (
    <div className="space-y-6 flex-1 overflow-y-auto pr-1">
      {/* Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">Total Users</span>
          <p className="text-2xl font-bold text-[var(--color-ink)] mt-1">{overview.total_users ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">Active Users</span>
          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">{overview.active_users ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">Paid Users</span>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">{overview.paid_users ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">New This Month</span>
          <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">{overview.new_users_this_month ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">Conversations</span>
          <p className="text-2xl font-bold text-[var(--color-ink)] mt-1">{overview.total_conversations ?? 0}</p>
        </div>
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-4 shadow-2xs">
          <span className="text-[11px] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">Total Messages</span>
          <p className="text-2xl font-bold text-[var(--color-ink)] mt-1">{overview.total_messages ?? 0}</p>
        </div>
      </div>

      {/* Subscription Breakdown & Quick Feeds */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Subscription Breakdown */}
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-5 shadow-2xs space-y-3">
          <h3 className="text-sm font-bold text-[var(--color-ink)]">Subscription Plans Distribution</h3>
          <div className="space-y-2 pt-1">
            {Object.entries(subs).map(([plan, count]: [string, any]) => (
              <div key={plan} className="flex items-center justify-between text-xs font-medium">
                <span className="capitalize px-2 py-0.5 rounded bg-[var(--color-canvas-parchment)] text-[var(--color-ink)]">
                  {plan}
                </span>
                <span className="font-bold text-[var(--color-ink)]">{count} users</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Signups */}
        <div className="rounded-2xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] p-5 shadow-2xs space-y-3 md:col-span-2">
          <h3 className="text-sm font-bold text-[var(--color-ink)]">Recent Registered Application Users</h3>
          <div className="divide-y divide-[var(--color-hairline)]">
            {(data?.recent_signups || []).slice(0, 5).map((u: any) => (
              <div key={u.id} className="py-2.5 flex items-center justify-between text-xs">
                <div>
                  <p className="font-semibold text-[var(--color-ink)]">{u.name}</p>
                  <p className="text-[var(--color-ink-muted-48)]">{u.email}</p>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                    u.role === 'ADMIN' ? 'bg-amber-500/10 text-amber-600' : 'bg-emerald-500/10 text-emerald-600'
                  }`}>
                    {u.role}
                  </span>
                  <p className="text-[10px] text-[var(--color-ink-muted-48)] mt-0.5">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
