import { useState } from 'react'
import { CustomerList } from './CustomerList'
import { DealsView } from './DealsView'
import { ActivitiesView } from './ActivitiesView'
import { LeadsView } from './LeadsView'

export function CRMView() {
  const [activeTab, setActiveTab] = useState<'customers' | 'leads' | 'deals' | 'activities'>('customers')

  return (
    <div className="flex h-full flex-col bg-[var(--color-canvas-parchment)] p-4 sm:p-6 overflow-hidden">
      {/* Top Header Navigation Tabs */}
      <div className="flex items-center justify-between border-b border-[var(--color-hairline)] bg-[var(--color-canvas)] px-6 py-2.5 rounded-2xl shadow-xs mb-4">
        <div className="flex items-center gap-2">
          <span className="text-xl">📊</span>
          <span className="font-bold text-lg text-[var(--color-ink)]">CRM Dashboard</span>
        </div>
        <div className="flex gap-1 bg-[var(--color-canvas-parchment)] p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('customers')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'customers'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Customers
          </button>
          <button
            onClick={() => setActiveTab('leads')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'leads'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Leads
          </button>
          <button
            onClick={() => setActiveTab('deals')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'deals'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Deals
          </button>
          <button
            onClick={() => setActiveTab('activities')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'activities'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Activities
          </button>
        </div>
      </div>

      {/* Main Active Tab Container */}
      <div className="flex-1 min-h-0">
        {activeTab === 'customers' && <CustomerList />}
        {activeTab === 'leads' && <LeadsView />}
        {activeTab === 'deals' && <DealsView />}
        {activeTab === 'activities' && <ActivitiesView />}
      </div>
    </div>
  )
}
