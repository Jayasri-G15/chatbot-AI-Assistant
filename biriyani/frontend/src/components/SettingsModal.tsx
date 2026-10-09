import type { ThemeMode } from '../hooks/useTheme'
import { useAuth } from '../hooks/useAuth'

function maskEmail(email: string) {
  if (!email || !email.includes('@')) return email
  const [name, domain] = email.split('@')
  if (name.length <= 2) return `${name[0]}*@${domain}`
  return `${name[0]}${'*'.repeat(name.length - 2)}${name[name.length - 1]}@${domain}`
}

function maskPhone(phone?: string | null) {
  if (!phone) return null
  const clean = phone.trim()
  if (clean.length < 6) return '****'
  return `${clean.slice(0, 3)}${'*'.repeat(clean.length - 6)}${clean.slice(-3)}`
}

interface Props {
  isOpen: boolean
  onClose: () => void
  theme: ThemeMode
  onThemeChange: (theme: ThemeMode) => void
}

export function SettingsModal({ isOpen, onClose, theme, onThemeChange }: Props) {
  const { user, logout } = useAuth()

  if (!isOpen) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
    >
      <div
        className="w-full max-w-md rounded-2xl bg-[var(--color-canvas)] border border-[var(--color-hairline)] p-6 shadow-xl transition-all space-y-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-3 border-b border-[var(--color-hairline)]">
          <h2 id="settings-title" className="text-xl font-bold text-[var(--color-ink)]">
            User Settings
          </h2>
          <button
            onClick={onClose}
            aria-label="Close Settings"
            className="rounded-lg p-1.5 text-[var(--color-ink-muted-48)] hover:bg-[var(--color-canvas-parchment)] hover:text-[var(--color-ink)] transition"
          >
            ✕
          </button>
        </div>

        {/* Profile Section */}
        {user && (
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-ink-muted-48)]">Account Profile</h3>
            <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] p-3.5 space-y-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-[var(--color-ink)]">{user.name}</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                  user.role === 'ADMIN' ? 'bg-amber-500/10 text-amber-600' : 'bg-blue-500/10 text-blue-600'
                }`}>
                  {user.role}
                </span>
              </div>
              <p className="font-mono text-[var(--color-ink-muted-80)]">{maskEmail(user.email)}</p>
              {user.phone && <p className="font-mono text-[var(--color-ink-muted-48)]">{maskPhone(user.phone)}</p>}
            </div>
          </div>
        )}

        {/* Appearance Section */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-[var(--color-ink-muted-48)]">Appearance</h3>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => onThemeChange('light')}
              className={`flex flex-col items-center gap-2 rounded-xl border p-3 transition cursor-pointer ${
                theme === 'light'
                  ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 ring-2 ring-[var(--color-primary)]/20'
                  : 'border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] hover:border-[var(--color-ink-muted-48)]'
              }`}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-100 text-amber-600 text-lg">
                ☀️
              </div>
              <div className="text-center">
                <span className="block text-xs font-medium text-[var(--color-ink)]">Light Mode</span>
              </div>
            </button>

            <button
              type="button"
              onClick={() => onThemeChange('dark')}
              className={`flex flex-col items-center gap-2 rounded-xl border p-3 transition cursor-pointer ${
                theme === 'dark'
                  ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 ring-2 ring-[var(--color-primary)]/20'
                  : 'border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] hover:border-[var(--color-ink-muted-48)]'
              }`}
            >
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-slate-100 text-lg">
                🌙
              </div>
              <div className="text-center">
                <span className="block text-xs font-medium text-[var(--color-ink)]">Dark Mode</span>
              </div>
            </button>
          </div>
        </div>

        {/* Session Section */}
        <div className="pt-3 border-t border-[var(--color-hairline)] flex items-center justify-between">
          <button
            onClick={() => {
              logout()
              onClose()
            }}
            className="px-4 py-2 rounded-xl border border-red-500/30 bg-red-500/10 text-red-600 text-xs font-semibold hover:bg-red-500/20 transition cursor-pointer"
          >
            Log Out
          </button>
          <button
            onClick={onClose}
            className="rounded-xl bg-[var(--color-primary)] px-5 py-2 text-xs font-semibold text-white hover:bg-[var(--color-primary-focus)] transition cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  )
}
