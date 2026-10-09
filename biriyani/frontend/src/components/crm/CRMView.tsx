import { useState } from 'react'
import { AnalyticsOverview } from './AnalyticsOverview'
import { CustomerList } from './CustomerList'
import { SubscriptionsView } from './SubscriptionsView'
import { PaymentsView } from './PaymentsView'
import { ActivitiesView } from './ActivitiesView'
import { CRMAssistantView } from './CRMAssistantView'

export function CRMView() {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'subscriptions' | 'payments' | 'activities' | 'assistant'>('overview')

  return (
    <div className="flex h-full flex-col bg-[var(--color-canvas-parchment)] p-4 sm:p-6 overflow-hidden">
      {/* Top Header Navigation Tabs */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[var(--color-hairline)] bg-[var(--color-canvas)] px-6 py-3 rounded-2xl shadow-xs mb-4 gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">📊</span>
          <span className="font-bold text-lg text-[var(--color-ink)]">Admin CRM Dashboard</span>
        </div>
        <div className="flex flex-wrap gap-1 bg-[var(--color-canvas-parchment)] p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'overview'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'users'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Users
          </button>
          <button
            onClick={() => setActiveTab('subscriptions')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'subscriptions'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Subscriptions
          </button>
          <button
            onClick={() => setActiveTab('payments')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'payments'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Payments
          </button>
          <button
            onClick={() => setActiveTab('activities')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              activeTab === 'activities'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            Activity Audit
          </button>
          <button
            onClick={() => setActiveTab('assistant')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1 ${
              activeTab === 'assistant'
                ? 'bg-[var(--color-canvas)] text-[var(--color-primary)] shadow-xs'
                : 'text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]'
            }`}
          >
            🤖 AI CRM Assistant
          </button>
        </div>
      </div>

      {/* Main Active Tab Container */}
      <div className="flex-1 min-h-0 flex flex-col">
        {activeTab === 'overview' && <AnalyticsOverview />}
        {activeTab === 'users' && <CustomerList />}
        {activeTab === 'subscriptions' && <SubscriptionsView />}
        {activeTab === 'payments' && <PaymentsView />}
        {activeTab === 'activities' && <ActivitiesView />}
        {activeTab === 'assistant' && <CRMAssistantView />}
      </div>
    </div>
  )
}
