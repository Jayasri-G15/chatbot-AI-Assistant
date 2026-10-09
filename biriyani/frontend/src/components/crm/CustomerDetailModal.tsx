import { useState, useEffect } from 'react'

interface Props {
  userId: string
  onClose: () => void
}

export function CustomerDetailModal({ userId, onClose }: Props) {
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'profile' | 'subscription' | 'conversations' | 'activities'>('profile')

  useEffect(() => {
    async function fetchDetails() {
      try {
        setIsLoading(true)
        const token = localStorage.getItem('crm_auth_token')
        const res = await fetch(`/api/v1/admin/users/${userId}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        const json = await res.json().catch(() => ({}))
        if (json.success || json.data) {
          setData(json.data || json)
        }
      } catch (err) {
        console.error('Failed to load user details:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchDetails()
  }, [userId])

  if (!userId) return null

  const profile = data?.profile || {}
  const sub = data?.subscription || {}
  const activities = data?.recent_activities || []
  const conversations = data?.conversations_summary?.items || []

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="w-full max-w-3xl max-h-[85vh] flex flex-col rounded-2xl bg-[var(--color-canvas)] border border-[var(--color-hairline)] shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)]">
          <div>
            <h2 className="text-xl font-bold text-[var(--color-ink)]">
              {isLoading ? 'Loading CRM User Profile…' : profile.name}
            </h2>
            {profile.email && (
              <p className="text-xs text-[var(--color-ink-muted-48)]">{profile.email} • Role: {profile.role}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-xl text-[var(--color-ink-muted-48)] hover:bg-black/5 dark:hover:bg-white/10 hover:text-[var(--color-ink)]"
          >
            ✕
          </button>
        </div>

        {/* Navigation Tabs */}
        {data && (
          <div className="flex border-b border-[var(--color-hairline)] px-6 bg-[var(--color-canvas)] gap-4 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'profile'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Account Info
            </button>
            <button
              onClick={() => setActiveTab('subscription')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'subscription'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Subscription & Payments
            </button>
            <button
              onClick={() => setActiveTab('conversations')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'conversations'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Conversations ({data.conversations_summary?.total ?? 0})
            </button>
            <button
              onClick={() => setActiveTab('activities')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'activities'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Activity Feed ({activities.length})
            </button>
          </div>
        )}

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {isLoading ? (
            <div className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
              Loading user profile data…
            </div>
          ) : !data ? (
            <div className="py-12 text-center text-sm text-red-600">
              User details could not be retrieved.
            </div>
          ) : (
            <>
              {activeTab === 'profile' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">User ID</span>
                    <p className="font-mono mt-1 text-[var(--color-ink)]">{profile.user_id}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">Email</span>
                    <p className="font-medium mt-1 text-[var(--color-ink)]">{profile.email}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">Phone</span>
                    <p className="font-medium mt-1 text-[var(--color-ink)]">{profile.phone || 'N/A'}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">Role & Status</span>
                    <p className="font-semibold mt-1 text-[var(--color-ink)]">{profile.role} • {profile.account_status}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">Login Count</span>
                    <p className="font-bold text-sm mt-1 text-[var(--color-ink)]">{profile.login_count}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">Last Login</span>
                    <p className="font-medium mt-1 text-[var(--color-ink)]">
                      {profile.last_login ? new Date(profile.last_login).toLocaleString() : 'N/A'}
                    </p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">Conversations / Messages</span>
                    <p className="font-semibold mt-1 text-[var(--color-ink)]">
                      {profile.conversation_count} conversations ({profile.message_count} messages)
                    </p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="font-semibold text-[var(--color-ink-muted-48)] uppercase">Account Created</span>
                    <p className="font-medium mt-1 text-[var(--color-ink)]">
                      {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
              )}

              {activeTab === 'subscription' && (
                <div className="space-y-4 text-xs">
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30 space-y-2">
                    <h4 className="font-bold text-sm text-[var(--color-ink)]">Current Subscription</h4>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <span className="text-[var(--color-ink-muted-48)]">Plan:</span>
                        <p className="font-bold text-indigo-600 dark:text-indigo-400">{sub.plan || 'FREE'}</p>
                      </div>
                      <div>
                        <span className="text-[var(--color-ink-muted-48)]">Status:</span>
                        <p className="font-bold text-emerald-600 dark:text-emerald-400">{sub.status || 'ACTIVE'}</p>
                      </div>
                      <div>
                        <span className="text-[var(--color-ink-muted-48)]">Billing Cycle:</span>
                        <p className="font-medium">{sub.billing_cycle || 'MONTHLY'}</p>
                      </div>
                      <div>
                        <span className="text-[var(--color-ink-muted-48)]">Payment Status:</span>
                        <p className="font-bold text-emerald-600 dark:text-emerald-400">{data.payment_status || 'PAID'}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'conversations' && (
                <div className="space-y-2">
                  {conversations.length === 0 ? (
                    <p className="text-xs text-[var(--color-ink-muted-48)]">No conversation history for this user.</p>
                  ) : (
                    conversations.map((c: any) => (
                      <div key={c.id} className="flex items-center justify-between rounded-xl border border-[var(--color-hairline)] p-3 bg-[var(--color-canvas)] text-xs">
                        <div>
                          <p className="font-semibold text-[var(--color-ink)]">{c.title || 'Untitled Chat'}</p>
                          <p className="text-[10px] text-[var(--color-ink-muted-48)] font-mono">{c.id}</p>
                        </div>
                        <div className="text-right">
                          <span className="px-2 py-0.5 rounded bg-[var(--color-canvas-parchment)] text-[10px] font-bold">
                            {c.message_count} messages
                          </span>
                          <p className="text-[10px] text-[var(--color-ink-muted-48)] mt-0.5">
                            {c.created_at ? new Date(c.created_at).toLocaleDateString() : ''}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'activities' && (
                <div className="space-y-2">
                  {activities.length === 0 ? (
                    <p className="text-xs text-[var(--color-ink-muted-48)]">No activity logged for this user.</p>
                  ) : (
                    activities.map((act: any) => (
                      <div key={act.id} className="rounded-xl border border-[var(--color-hairline)] p-3 bg-[var(--color-canvas)] text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-500/10 text-blue-600">
                            {act.activity_type}
                          </span>
                          <span className="text-[10px] text-[var(--color-ink-muted-48)]">
                            {act.timestamp ? new Date(act.timestamp).toLocaleString() : 'N/A'}
                          </span>
                        </div>
                        {act.metadata && (
                          <p className="text-[11px] font-mono text-[var(--color-ink-muted-80)]">
                            {JSON.stringify(act.metadata)}
                          </p>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
