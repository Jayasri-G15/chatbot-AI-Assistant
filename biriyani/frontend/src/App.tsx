import { useEffect, useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { ChatWindow } from './components/ChatWindow'
import { CRMView } from './components/crm/CRMView'
import { SettingsModal } from './components/SettingsModal'
import { useTheme } from './hooks/useTheme'
import {
  useConversations,
  useCreateConversation,
  useDeleteConversation,
  useRenameConversation,
} from './hooks/useConversations'

export default function App() {
  const { theme, setTheme } = useTheme()
  const { data: conversations = [], isLoading, isError } = useConversations()
  const createConversation = useCreateConversation()
  const deleteConversation = useDeleteConversation()
  const renameConversation = useRenameConversation()
  const [activeId, setActiveId] = useState<string | null>(null)
  const [activeView, setActiveView] = useState<'chat' | 'crm'>('chat')
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

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
            Biriyani AI {activeView === 'crm' ? '• CRM Dashboard' : ''}
          </span>
        </div>
        <button
          onClick={() => setIsSettingsOpen(true)}
          aria-label="Settings"
          className="rounded-lg p-1.5 text-lg text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)]"
        >
          ⚙️
        </button>
      </header>

      <div className="hidden h-full shrink-0 md:block">
        <Sidebar
          conversations={conversations}
          activeId={activeId}
          activeView={activeView}
          isLoading={isLoading}
          isError={isError}
          onSelect={handleSelect}
          onNew={handleNew}
          onDelete={handleDelete}
          onRename={(id, title) => renameConversation.mutate({ id, title })}
          onNavigateView={(view) => setActiveView(view)}
          onOpenSettings={() => setIsSettingsOpen(true)}
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
              isLoading={isLoading}
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
            />
          </div>
        </div>
      )}

      <div className="min-h-0 flex-1 overflow-hidden">
        {activeView === 'chat' ? (
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
