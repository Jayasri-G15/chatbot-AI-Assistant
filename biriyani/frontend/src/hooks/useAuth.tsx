import { useState, useEffect, createContext, useContext, type ReactNode } from 'react'

export interface UserProfile {
  id: string
  name: string
  email: string
  phone?: string | null
  role: 'ADMIN' | 'USER'
}

interface AuthContextType {
  user: UserProfile | null
  token: string | null
  isLoading: boolean
  login: (email: string, pass: string) => Promise<void>
  signup: (name: string, email: string, pass: string, phone?: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => {
    const t = localStorage.getItem('crm_auth_token')
    return t && t !== 'undefined' ? t : null
  })
  const [user, setUser] = useState<UserProfile | null>(() => {
    try {
      const cached = localStorage.getItem('crm_auth_user')
      return cached && cached !== 'undefined' ? JSON.parse(cached) : null
    } catch {
      return null
    }
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function checkAuth() {
      if (!token) {
        setUser(null)
        setIsLoading(false)
        return
      }

      try {
        const res = await fetch('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (res.ok) {
          const data = await res.json()
          setUser(data)
          localStorage.setItem('crm_auth_user', JSON.stringify(data))
        } else {
          setToken(null)
          setUser(null)
          localStorage.removeItem('crm_auth_token')
          localStorage.removeItem('crm_auth_user')
        }
      } catch (e) {
        console.error('Auth verification error:', e)
        setToken(null)
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }
    checkAuth()
  }, [token])

  const login = async (email: string, pass: string) => {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password: pass }),
    })
    const json = await res.json()
    if (!res.ok) {
      throw new Error(json.detail?.error?.message || json.detail || 'Invalid email or password.')
    }
    setToken(json.access_token)
    setUser(json.user)
    localStorage.setItem('crm_auth_token', json.access_token)
    localStorage.setItem('crm_auth_user', JSON.stringify(json.user))
  }

  const signup = async (name: string, email: string, pass: string, phone?: string) => {
    const res = await fetch('/api/v1/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password: pass, phone }),
    })
    const json = await res.json()
    if (!res.ok) {
      throw new Error(json.detail?.error?.message || json.detail || 'Signup failed.')
    }
    setToken(json.access_token)
    setUser(json.user)
    localStorage.setItem('crm_auth_token', json.access_token)
    localStorage.setItem('crm_auth_user', JSON.stringify(json.user))
  }

  const logout = () => {
    if (token) {
      fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {})
    }
    setToken(null)
    setUser(null)
    localStorage.removeItem('crm_auth_token')
    localStorage.removeItem('crm_auth_user')
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
