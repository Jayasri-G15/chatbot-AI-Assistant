import { useState, useEffect } from 'react'

interface Props {
  customerId: string
  onClose: () => void
}

export function CustomerDetailModal({ customerId, onClose }: Props) {
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'info' | 'contacts' | 'deals' | 'activities'>('info')

  useEffect(() => {
    async function fetchDetails() {
      try {
        setIsLoading(true)
        const res = await fetch(`/api/v1/customers/${customerId}`)
        const json = await res.json()
        if (json.success) {
          setData(json.data)
        }
      } catch (err) {
        console.error('Failed to load customer details:', err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchDetails()
  }, [customerId])

  if (!customerId) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="w-full max-w-3xl max-h-[85vh] flex flex-col rounded-2xl bg-[var(--color-canvas)] border border-[var(--color-hairline)] shadow-xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)]">
          <div>
            <h2 className="text-xl font-bold text-[var(--color-ink)]">
              {isLoading ? 'Loading Customer…' : data?.customer?.name}
            </h2>
            {data?.customer?.company && (
              <p className="text-xs text-[var(--color-ink-muted-48)]">{data.customer.company}</p>
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
          <div className="flex border-b border-[var(--color-hairline)] px-6 bg-[var(--color-canvas)] gap-4 text-sm font-medium">
            <button
              onClick={() => setActiveTab('info')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'info'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Profile Info
            </button>
            <button
              onClick={() => setActiveTab('contacts')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'contacts'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Contacts ({data.contacts.length})
            </button>
            <button
              onClick={() => setActiveTab('deals')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'deals'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Deals ({data.deals.length})
            </button>
            <button
              onClick={() => setActiveTab('activities')}
              className={`py-3 border-b-2 transition ${
                activeTab === 'activities'
                  ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                  : 'border-transparent text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
              }`}
            >
              Activities ({data.activities.length})
            </button>
          </div>
        )}

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
              Loading customer details…
            </div>
          ) : !data ? (
            <div className="py-12 text-center text-sm text-red-600">
              Customer details could not be retrieved.
            </div>
          ) : (
            <>
              {activeTab === 'info' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Email</span>
                    <p className="text-sm font-medium mt-1 text-[var(--color-ink)]">{data.customer.email || 'N/A'}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Phone</span>
                    <p className="text-sm font-medium mt-1 text-[var(--color-ink)]">{data.customer.phone || 'N/A'}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Company</span>
                    <p className="text-sm font-medium mt-1 text-[var(--color-ink)]">{data.customer.company}</p>
                  </div>
                  <div className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas-parchment)]/30">
                    <span className="text-xs font-semibold text-[var(--color-ink-muted-48)] uppercase">Customer ID</span>
                    <p className="text-xs font-mono mt-1 text-[var(--color-ink-muted-80)]">{data.customer.id}</p>
                  </div>
                </div>
              )}

              {activeTab === 'contacts' && (
                <div className="space-y-3">
                  {data.contacts.length === 0 ? (
                    <p className="text-sm text-[var(--color-ink-muted-48)]">No contacts associated with this customer.</p>
                  ) : (
                    data.contacts.map((cnt: any) => (
                      <div key={cnt.id} className="flex items-center justify-between rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas)] shadow-2xs">
                        <div>
                          <p className="font-semibold text-sm text-[var(--color-ink)]">{cnt.name}</p>
                          <p className="text-xs text-[var(--color-ink-muted-48)]">{cnt.role} • {cnt.email}</p>
                        </div>
                        <span className="text-xs font-mono text-[var(--color-ink-muted-48)]">{cnt.phone}</span>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'deals' && (
                <div className="space-y-3">
                  {data.deals.length === 0 ? (
                    <p className="text-sm text-[var(--color-ink-muted-48)]">No deals found for this customer.</p>
                  ) : (
                    data.deals.map((d: any) => (
                      <div key={d.id} className="flex items-center justify-between rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas)] shadow-2xs">
                        <div>
                          <p className="font-semibold text-sm text-[var(--color-ink)]">{d.title}</p>
                          <p className="text-xs text-[var(--color-ink-muted-48)]">
                            Status: <span className="font-semibold uppercase">{d.status}</span>
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-sm text-emerald-600 dark:text-emerald-400">
                            ₹{d.value.toLocaleString()}
                          </p>
                          {d.close_date && (
                            <p className="text-xs text-[var(--color-ink-muted-48)]">
                              Close: {new Date(d.close_date).toLocaleDateString()}
                            </p>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'activities' && (
                <div className="space-y-3">
                  {data.activities.length === 0 ? (
                    <p className="text-sm text-[var(--color-ink-muted-48)]">No recent activities logged.</p>
                  ) : (
                    data.activities.map((act: any) => (
                      <div key={act.id} className="rounded-xl border border-[var(--color-hairline)] p-4 bg-[var(--color-canvas)] shadow-2xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="px-2 py-0.5 rounded text-xs font-bold uppercase bg-blue-500/10 text-blue-600">
                            {act.type}
                          </span>
                          <span className="text-xs text-[var(--color-ink-muted-48)]">
                            {new Date(act.activity_date).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="font-semibold text-sm text-[var(--color-ink)]">{act.subject}</p>
                        {act.notes && (
                          <p className="text-xs text-[var(--color-ink-muted-80)] mt-1">{act.notes}</p>
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
