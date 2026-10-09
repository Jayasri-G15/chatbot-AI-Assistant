import { useState, useEffect } from 'react'

export function ActivitiesView() {
  const [activities, setActivities] = useState<any[]>([])
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchActivities() {
      try {
        setIsLoading(true)
        const token = localStorage.getItem('crm_auth_token')
        const params = new URLSearchParams()
        if (typeFilter) params.append('type', typeFilter)
        const res = await fetch(`/api/v1/admin/activities?${params.toString()}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        const json = await res.json()
        if (json.success || json.data) {
          const d = json.data || json
          setActivities(d.items || d.activities || [])
        }
      } catch (err) {
        console.error('Failed to fetch user activities:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchActivities()
  }, [typeFilter])

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">System User Activity Audit Log</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">Automated CRM event tracking for Signups, Logins, Chats, Subscriptions & Payments</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-ink-muted-48)] font-medium">Activity Event:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3 py-1.5 text-xs text-[var(--color-ink)] outline-none shadow-2xs"
          >
            <option value="">All Activity Events</option>
            <option value="SIGNUP">SIGNUP</option>
            <option value="LOGIN">LOGIN</option>
            <option value="LOGOUT">LOGOUT</option>
            <option value="CHAT_STARTED">CHAT_STARTED</option>
            <option value="MESSAGE_SENT">MESSAGE_SENT</option>
            <option value="DOCUMENT_UPLOADED">DOCUMENT_UPLOADED</option>
            <option value="SUBSCRIPTION_CHANGED">SUBSCRIPTION_CHANGED</option>
            <option value="PAYMENT_COMPLETED">PAYMENT_COMPLETED</option>
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-auto space-y-2.5 pr-1">
        {isLoading ? (
          <div className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
            Loading real activity audit log…
          </div>
        ) : activities.length === 0 ? (
          <div className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
            No activity records matching criteria.
          </div>
        ) : (
          activities.map((act) => (
            <div key={act.id} className="rounded-xl border border-[var(--color-hairline)] p-3.5 bg-[var(--color-canvas)] shadow-2xs space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase ${
                    act.activity_type === 'SIGNUP' ? 'bg-emerald-500/10 text-emerald-600' :
                    act.activity_type === 'LOGIN' ? 'bg-blue-500/10 text-blue-600' :
                    act.activity_type === 'PAYMENT_COMPLETED' ? 'bg-indigo-500/10 text-indigo-600' :
                    'bg-gray-500/10 text-gray-600'
                  }`}>
                    {act.activity_type}
                  </span>
                  <span className="font-semibold text-xs text-[var(--color-ink)]">{act.user_name || act.user_email || 'User'}</span>
                  {act.user_email && <span className="text-[11px] text-[var(--color-ink-muted-48)]">({act.user_email})</span>}
                </div>
                <span className="text-[10px] text-[var(--color-ink-muted-48)] font-mono">
                  {act.timestamp ? new Date(act.timestamp).toLocaleString() : 'N/A'}
                </span>
              </div>
              {act.metadata && (
                <p className="text-[11px] font-mono text-[var(--color-ink-muted-80)] bg-[var(--color-canvas-parchment)]/50 p-2 rounded-lg border border-[var(--color-hairline)]">
                  {typeof act.metadata === 'object' ? JSON.stringify(act.metadata) : act.metadata}
                </p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
