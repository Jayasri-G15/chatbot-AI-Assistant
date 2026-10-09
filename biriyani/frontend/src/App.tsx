import { useEffect, useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { ChatWindow } from './components/ChatWindow'
import { CRMView } from './components/crm/CRMView'
import { SettingsModal } from './components/SettingsModal'
import { AuthView } from './components/AuthView'
import { useTheme } from './hooks/useTheme'
import { useAuth } from './hooks/useAuth'
import {
  useConversations,
  useCreateConversation,
  useDeleteConversation,
  useRenameConversation,
} from './hooks/useConversations'

export default function App() {
  const { theme, setTheme } = useTheme()
  const { user, isLoading: isAuthLoading } = useAuth()
  const { data: conversations = [], isLoading: isConvLoading, isError } = useConversations()
  const createConversation = useCreateConversation()
  const deleteConversation = useDeleteConversation()
  const renameConversation = useRenameConversation()
  const [activeId, setActiveId] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<'chat' | 'crm'>('chat')
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  // Ensure non-admin users cannot stay on CRM view
  useEffect(() => {
    if (user && user.role !== 'ADMIN' && activeView === 'crm') {
      setActiveView('chat')
    }
  }, [user, activeView])

  useEffect(() => {
    if (!activeId && conversations.length > 0) {
      setActiveId(conversations[0].id)
    }
  }, [conversations, activeId])

  const handleNew = async () => {
    const created = await createConversation.mutateAsync()
    setActiveId(created.id)
    setActiveView('chat')
    setIsDrawerOpen(false)
  }

  const handleDelete = async (id: string) => {
    await deleteConversation.mutateAsync(id)
    if (activeId === id) setActiveId(null)
  }

  const handleSelect = (id: string) => {
    setActiveId(id)
    setActiveView('chat')
    setIsDrawerOpen(false)
  }

  // Loading state
  if (isAuthLoading) {
    return (
      <div className="flex h-dvh w-screen items-center justify-center bg-[var(--color-canvas-parchment)] text-sm text-[var(--color-ink-muted-48)] font-medium">
        Initializing AI Assistant…
      </div>
    )
  }

  // Unauthenticated flow: Render opaque standalone AuthView (no chatbot leak behind!)
  if (!user) {
    return <AuthView initialMode="login" />
  }

  return (
    <div className="flex h-dvh w-screen flex-col overflow-hidden bg-[var(--color-canvas-parchment)] md:flex-row text-[var(--color-ink)] transition-colors">
      <header className="flex h-12 shrink-0 items-center justify-between border-b border-[var(--color-hairline)] bg-[var(--color-canvas)] px-4 md:hidden">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsDrawerOpen(true)}
            aria-label="Open menu"
            className="btn-press rounded-lg p-1.5 text-lg text-[var(--color-ink)] hover:bg-[var(--color-canvas-parchment)]"
          >
            ☰
          </button>
          <span className="font-semibold text-sm text-[var(--color-ink)]">
            AI Assistant {activeView === 'crm' ? '• CRM Dashboard' : ''}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-[var(--color-canvas-parchment)] border border-[var(--color-hairline)] text-[var(--color-ink)]"
          >
            {user.name}
          </button>
          <button
            onClick={() => setIsSettingsOpen(true)}
            aria-label="Settings"
            className="rounded-lg p-1.5 text-lg text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]"
          >
            ⚙️
          </button>
        </div>
      </header>

      <div className="hidden h-full shrink-0 md:block">
        <Sidebar
          conversations={conversations}
          activeId={activeId}
          activeView={activeView}
          isLoading={isConvLoading}
          isError={isError}
          onSelect={handleSelect}
          onNew={handleNew}
          onDelete={handleDelete}
          onRename={(id, title) => renameConversation.mutate({ id, title })}
          onNavigateView={(view) => setActiveView(view)}
          onOpenSettings={() => setIsSettingsOpen(true)}
          onOpenAuth={() => setIsSettingsOpen(true)}
        />
      </div>

      {isDrawerOpen && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/40 backdrop-blur-xs" onClick={() => setIsDrawerOpen(false)} />
          <div className="product-shadow absolute inset-y-0 left-0 w-[85%] max-w-72">
            <Sidebar
              conversations={conversations}
              activeId={activeId}
              activeView={activeView}
              isLoading={isConvLoading}
              isError={isError}
              onSelect={handleSelect}
              onNew={handleNew}
              onDelete={handleDelete}
              onRename={(id, title) => renameConversation.mutate({ id, title })}
              onNavigateView={(view) => {
                setActiveView(view)
                setIsDrawerOpen(false)
              }}
              onOpenSettings={() => {
                setIsDrawerOpen(false)
                setIsSettingsOpen(true)
              }}
              onOpenAuth={() => {
                setIsDrawerOpen(false)
                setIsSettingsOpen(true)
              }}
            />
          </div>
        </div>
      )}

      <div className="min-h-0 flex-1 overflow-hidden">
        {activeView === 'chat' || user.role !== 'ADMIN' ? (
          <ChatWindow conversationId={activeId} />
        ) : (
          <CRMView />
        )}
      </div>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        theme={theme}
        onThemeChange={setTheme}
      />
    </div>
  )
}
