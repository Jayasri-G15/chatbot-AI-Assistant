import { useState, useEffect } from 'react'

export function ActivitiesView() {
  const [activities, setActivities] = useState<any[]>([])
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function fetchActivities() {
      try {
        setIsLoading(true)
        const q = typeFilter ? `?type=${typeFilter}` : ''
        const res = await fetch(`/api/v1/activities${q}`)
        const json = await res.json()
        if (json.success) {
          setActivities(json.data.items)
        }
      } catch (err) {
        console.error('Failed to fetch activities:', err)
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
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">Customer Activities Log</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">Recent calls, meetings, emails, and notes</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-ink-muted-48)] font-medium">Type:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3 py-1.5 text-xs text-[var(--color-ink)] outline-none shadow-2xs"
          >
            <option value="">All Activity Types</option>
            <option value="call">Call</option>
            <option value="meeting">Meeting</option>
            <option value="email">Email</option>
            <option value="note">Note</option>
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-auto space-y-3 pr-1">
        {isLoading ? (
          <div className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
            Loading activity log…
          </div>
        ) : activities.length === 0 ? (
          <div className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
            No activities recorded matching criteria.
          </div>
        ) : (
          activities.map((act) => (
            <div key={act.id} className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas)] shadow-2xs">
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase bg-blue-500/10 text-blue-600">
                    {act.type}
                  </span>
                  <span className="font-semibold text-sm text-[var(--color-ink)]">{act.customer_name}</span>
                </div>
                <span className="text-xs text-[var(--color-ink-muted-48)]">
                  {act.activity_date ? new Date(act.activity_date).toLocaleDateString() : 'N/A'}
                </span>
              </div>
              <p className="font-semibold text-sm text-[var(--color-ink)]">{act.subject}</p>
              {act.notes && (
                <p className="text-xs text-[var(--color-ink-muted-80)] mt-1.5 leading-relaxed bg-[var(--color-canvas-parchment)]/40 p-2.5 rounded-lg border border-[var(--color-hairline)]">
                  {act.notes}
                </p>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
