import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'

interface Props {
  isOpen: boolean
  onClose: () => void
  initialMode?: 'login' | 'signup'
}

export function AuthModal({ isOpen, onClose, initialMode = 'login' }: Props) {
  const { user, login, signup, logout } = useAuth()
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (mode === 'signup') {
      if (!name.trim()) {
        setError('Full Name is required.')
        return
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters.')
        return
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match.')
        return
      }
    }

    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email, password)
      } else {
        await signup(name.trim(), email.trim(), password, phone.trim() || undefined)
      }
      onClose()
    } catch (err: any) {
      setError(err.message || 'Authentication failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs">
      <div className="w-full max-w-md rounded-2xl bg-[var(--color-canvas)] border border-[var(--color-hairline)] shadow-2xl overflow-hidden p-6 space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-[var(--color-ink)]">
            {user ? 'Account Settings' : mode === 'login' ? 'Sign In' : 'Create Account'}
          </h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-lg text-[var(--color-ink-muted-48)] hover:bg-black/5 dark:hover:bg-white/10"
          >
            ✕
          </button>
        </div>

        {user ? (
          <div className="space-y-4">
            <div className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-[var(--color-ink)]">{user.name}</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${
                  user.role === 'ADMIN' ? 'bg-amber-500/10 text-amber-600' : 'bg-blue-500/10 text-blue-600'
                }`}>
                  {user.role}
                </span>
              </div>
              <p className="text-xs text-[var(--color-ink-muted-80)]">{user.email}</p>
              {user.phone && <p className="text-xs font-mono text-[var(--color-ink-muted-48)]">{user.phone}</p>}
            </div>

            <button
              onClick={() => {
                logout()
                onClose()
              }}
              className="w-full py-2.5 rounded-xl border border-red-500/30 bg-red-500/10 text-red-600 font-semibold text-sm hover:bg-red-500/20 transition"
            >
              Log Out
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 text-xs font-medium">
                ⚠️ {error}
              </div>
            )}

            {mode === 'signup' && (
              <div>
                <label className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Jayasri"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3.5 py-2 text-sm text-[var(--color-ink)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)]"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">Email Address</label>
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3.5 py-2 text-sm text-[var(--color-ink)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)]"
              />
            </div>

            {mode === 'signup' && (
              <div>
                <label className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">Phone Number</label>
                <input
                  type="text"
                  placeholder="+91 98765 43210"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3.5 py-2 text-sm text-[var(--color-ink)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)]"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3.5 py-2 text-sm text-[var(--color-ink)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)]"
              />
            </div>

            {mode === 'signup' && (
              <div>
                <label className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">Confirm Password</label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3.5 py-2 text-sm text-[var(--color-ink)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)]"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-xl bg-[var(--color-primary)] text-white font-semibold text-sm hover:bg-[var(--color-primary-focus)] transition disabled:opacity-50"
            >
              {loading ? 'Processing…' : mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>

            <div className="pt-3 border-t border-[var(--color-hairline)] text-center">
              <p className="text-xs text-[var(--color-ink-muted-48)]">
                {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
                <button
                  type="button"
                  onClick={() => {
                    setMode(mode === 'login' ? 'signup' : 'login')
                    setError(null)
                  }}
                  className="ml-1 text-[var(--color-primary)] font-semibold hover:underline"
                >
                  {mode === 'login' ? 'Create account' : 'Sign In'}
                </button>
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
