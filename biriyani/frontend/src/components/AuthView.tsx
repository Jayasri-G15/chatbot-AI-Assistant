import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'

interface Props {
  initialMode?: 'login' | 'signup'
}

export function AuthView({ initialMode = 'login' }: Props) {
  const { login, signup } = useAuth()
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // Body scroll lock
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = ''
    }
  }, [])

  // Keyboard navigation & ESC handler
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && mode === 'signup') {
        switchMode('login')
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [mode])

  const resetForm = () => {
    setName('')
    setEmail('')
    setPhone('')
    setPassword('')
    setConfirmPassword('')
    setShowPassword(false)
    setShowConfirmPassword(false)
    setError(null)
  }

  const switchMode = (targetMode: 'login' | 'signup') => {
    resetForm()
    setMode(targetMode)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (mode === 'signup') {
      if (!name.trim()) {
        setError('Please enter your full name.')
        return
      }
      if (!email.trim() || !email.includes('@')) {
        setError('Please enter a valid email address.')
        return
      }
      if (password.length < 6) {
        setError('Password must be at least 6 characters long.')
        return
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match.')
        return
      }
    } else {
      if (!email.trim() || !password) {
        setError('Please enter your email and password.')
        return
      }
    }

    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email.trim(), password)
      } else {
        // Confirm password is validated on client and NEVER sent to API
        await signup(name.trim(), email.trim(), password, phone.trim() || undefined)
      }
    } catch (err: any) {
      const msg = err.message || 'Authentication failed. Please check your credentials.'
      if (msg.toLowerCase().includes('user_exists') || msg.toLowerCase().includes('already exists')) {
        setError('An account with this email already exists. Please sign in.')
      } else {
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--color-canvas-parchment)] p-4 overflow-y-auto">
      <div className="w-full max-w-md rounded-3xl bg-[var(--color-canvas)] border border-[var(--color-hairline)] shadow-2xl overflow-hidden p-6 sm:p-8 space-y-6">
        {/* Header Branding */}
        <div className="flex items-center justify-between pb-2 border-b border-[var(--color-hairline)]">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--color-primary)] text-white text-xl font-bold shadow-xs">
              🤖
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">AI Assistant</h1>
              <p className="text-[11px] font-medium text-[var(--color-ink-muted-48)]">
                {mode === 'login' ? 'Sign in to your account' : 'Create a new account'}
              </p>
            </div>
          </div>

          {/* Close/Exit X Button in Signup mode returns to Login */}
          {mode === 'signup' && (
            <button
              type="button"
              onClick={() => switchMode('login')}
              title="Return to Sign In"
              className="rounded-xl p-2 text-lg text-[var(--color-ink-muted-48)] hover:bg-[var(--color-canvas-parchment)] hover:text-[var(--color-ink)] transition cursor-pointer"
            >
              ✕
            </button>
          )}
        </div>

        {/* Form Container */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3.5 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-xs font-medium leading-relaxed">
              ⚠️ {error}
            </div>
          )}

          {mode === 'signup' && (
            <div>
              <label htmlFor="signup-name" className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">
                Full Name <span className="text-red-500">*</span>
              </label>
              <input
                id="signup-name"
                type="text"
                required
                autoComplete="name"
                placeholder="Enter your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)]/30 px-3.5 py-2.5 text-sm text-[var(--color-ink)] placeholder-[var(--color-ink-muted-48)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)] transition"
              />
            </div>
          )}

          <div>
            <label htmlFor="auth-email" className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">
              Email Address <span className="text-red-500">*</span>
            </label>
            <input
              id="auth-email"
              type="email"
              required
              autoComplete="email"
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)]/30 px-3.5 py-2.5 text-sm text-[var(--color-ink)] placeholder-[var(--color-ink-muted-48)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)] transition"
            />
          </div>

          {mode === 'signup' && (
            <div>
              <label htmlFor="signup-phone" className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">
                Phone Number (Optional)
              </label>
              <input
                id="signup-phone"
                type="tel"
                autoComplete="tel"
                placeholder="+91 XXXXX XXXXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)]/30 px-3.5 py-2.5 text-sm text-[var(--color-ink)] placeholder-[var(--color-ink-muted-48)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)] transition"
              />
            </div>
          )}

          <div>
            <label htmlFor="auth-password" className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">
              Password <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                id="auth-password"
                type={showPassword ? 'text' : 'password'}
                required
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                placeholder={mode === 'signup' ? 'Create a password' : 'Enter your password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)]/30 px-3.5 py-2.5 pr-10 text-sm text-[var(--color-ink)] placeholder-[var(--color-ink-muted-48)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)] transition"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                title={showPassword ? 'Hide password' : 'Show password'}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 text-sm text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)] cursor-pointer"
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          {mode === 'signup' && (
            <div>
              <label htmlFor="signup-confirm-password" className="block text-xs font-semibold text-[var(--color-ink-muted-80)] mb-1">
                Confirm Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="signup-confirm-password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  autoComplete="new-password"
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)]/30 px-3.5 py-2.5 pr-10 text-sm text-[var(--color-ink)] placeholder-[var(--color-ink-muted-48)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)] transition"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  title={showConfirmPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 text-sm text-[var(--color-ink-muted-48)] hover:text-[var(--color-ink)] cursor-pointer"
                >
                  {showConfirmPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-[var(--color-primary)] text-white font-bold text-sm hover:bg-[var(--color-primary-focus)] transition shadow-xs disabled:opacity-50 cursor-pointer mt-2"
          >
            {loading
              ? mode === 'login'
                ? 'Signing in…'
                : 'Creating account…'
              : mode === 'login'
              ? 'Sign In'
              : 'Create Account'}
          </button>

          <div className="pt-4 border-t border-[var(--color-hairline)] text-center">
            <p className="text-xs text-[var(--color-ink-muted-48)]">
              {mode === 'login' ? "Don't have an account?" : 'Already have an account?'}
              <button
                type="button"
                onClick={() => switchMode(mode === 'login' ? 'signup' : 'login')}
                className="ml-1 text-[var(--color-primary)] font-bold hover:underline cursor-pointer"
              >
                {mode === 'login' ? 'Create Account' : 'Sign In'}
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  )
}
