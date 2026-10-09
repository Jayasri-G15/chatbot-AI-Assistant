import { useState, useEffect } from 'react'
import { CustomerDetailModal } from './CustomerDetailModal'

function maskEmail(email: string) {
  if (!email || !email.includes('@')) return email
  const [name, domain] = email.split('@')
  if (name.length <= 2) return `${name[0]}*@${domain}`
  return `${name[0]}${'*'.repeat(name.length - 2)}${name[name.length - 1]}@${domain}`
}

function maskPhone(phone?: string | null) {
  if (!phone) return '—'
  const clean = phone.trim()
  if (clean.length < 6) return '****'
  return `${clean.slice(0, 3)}${'*'.repeat(clean.length - 6)}${clean.slice(-3)}`
}

export function CustomerList() {
  const [users, setUsers] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [subFilter, setSubFilter] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null)

  useEffect(() => {
    async function fetchUsers() {
      try {
        setIsLoading(true)
        const token = localStorage.getItem('crm_auth_token')
        const params = new URLSearchParams({
          search,
          role: roleFilter,
          status: statusFilter,
          subscription: subFilter,
          page: page.toString(),
          limit: '10',
        })
        const res = await fetch(`/api/v1/admin/users?${params.toString()}`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        })
        const json = await res.json().catch(() => ({}))
        if (json.success || json.items) {
          setUsers(json.items || json.data?.items || [])
          setTotal(json.total || json.data?.total || 0)
        }
      } catch (err) {
        console.error('Failed to fetch CRM users:', err)
      } finally {
        setIsLoading(false)
      }
    }
    const timer = setTimeout(fetchUsers, 300)
    return () => clearTimeout(timer)
  }, [search, roleFilter, statusFilter, subFilter, page])

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Search & Filter Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[var(--color-ink)]">CRM Customer Directory</h2>
          <p className="text-xs text-[var(--color-ink-muted-48)]">
            Showing {total} real registered user account{total !== 1 ? 's' : ''}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <input
            type="text"
            placeholder="Search name, email…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-3.5 py-1.5 text-xs text-[var(--color-ink)] placeholder-[var(--color-ink-muted-48)] outline-none ring-2 ring-transparent focus:ring-[var(--color-primary-focus)]"
          />

          <select
            value={roleFilter}
            onChange={(e) => {
              setRoleFilter(e.target.value)
              setPage(1)
            }}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-2.5 py-1.5 text-xs text-[var(--color-ink)] outline-none"
          >
            <option value="">All Roles</option>
            <option value="ADMIN">ADMIN</option>
            <option value="USER">USER</option>
          </select>

          <select
            value={subFilter}
            onChange={(e) => {
              setSubFilter(e.target.value)
              setPage(1)
            }}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-2.5 py-1.5 text-xs text-[var(--color-ink)] outline-none"
          >
            <option value="">All Plans</option>
            <option value="FREE">FREE</option>
            <option value="PRO">PRO</option>
            <option value="PREMIUM">PREMIUM</option>
            <option value="ENTERPRISE">ENTERPRISE</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            className="rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] px-2.5 py-1.5 text-xs text-[var(--color-ink)] outline-none"
          >
            <option value="">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="DEACTIVATED">DEACTIVATED</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto rounded-xl border border-[var(--color-hairline)] bg-[var(--color-canvas)] shadow-2xs">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-[var(--color-hairline)] bg-[var(--color-canvas-parchment)] font-semibold text-[var(--color-ink-muted-48)] uppercase tracking-wider">
              <th className="p-3">User</th>
              <th className="p-3">Email (Masked)</th>
              <th className="p-3">Phone (Masked)</th>
              <th className="p-3">Role</th>
              <th className="p-3">Subscription</th>
              <th className="p-3">Status</th>
              <th className="p-3">Logins</th>
              <th className="p-3">Conversations</th>
              <th className="p-3">Last Login</th>
              <th className="p-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-hairline)]">
            {isLoading ? (
              <tr>
                <td colSpan={10} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  Loading real customer data…
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={10} className="py-12 text-center text-sm text-[var(--color-ink-muted-48)]">
                  No matching registered user profiles found.
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr
                  key={u.user_id || u.id}
                  onClick={() => setSelectedUserId(u.user_id || u.id)}
                  className="hover:bg-[var(--color-canvas-parchment)]/60 cursor-pointer transition"
                >
                  <td className="p-3 font-semibold text-[var(--color-ink)]">{u.name}</td>
                  <td className="p-3 text-[var(--color-ink-muted-80)] font-mono text-[11px]">{maskEmail(u.email)}</td>
                  <td className="p-3 text-[var(--color-ink-muted-80)] font-mono text-[11px]">{maskPhone(u.phone)}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      u.role === 'ADMIN' ? 'bg-amber-500/10 text-amber-600' : 'bg-blue-500/10 text-blue-600'
                    }`}>
                      {u.role}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      u.subscription_plan === 'PRO' ? 'bg-purple-500/10 text-purple-600' :
                      u.subscription_plan === 'PREMIUM' ? 'bg-indigo-500/10 text-indigo-600' :
                      'bg-gray-500/10 text-gray-600'
                    }`}>
                      {u.subscription_plan || 'FREE'}
                    </span>
                  </td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-600">
                      {u.account_status || 'ACTIVE'}
                    </span>
                  </td>
                  <td className="p-3 font-semibold text-[var(--color-ink)]">{u.login_count ?? 1}</td>
                  <td className="p-3 font-semibold text-[var(--color-ink)]">{u.conversation_count ?? 0}</td>
                  <td className="p-3 text-[11px] text-[var(--color-ink-muted-48)]">
                    {u.last_login ? new Date(u.last_login).toLocaleString() : 'N/A'}
                  </td>
                  <td className="p-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedUserId(u.user_id || u.id)
                      }}
                      className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-[var(--color-primary)]/10 text-[var(--color-primary)] hover:bg-[var(--color-primary)]/20 transition"
                    >
                      View Profile
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-xs text-[var(--color-ink-muted-48)] pt-1">
        <span>Page {page} of {Math.ceil(total / 10) || 1}</span>
        <div className="flex gap-2">
          <button
            disabled={page <= 1}
            onClick={() => setPage(p => p - 1)}
            className="px-3 py-1.5 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas)] disabled:opacity-40 hover:bg-[var(--color-canvas-parchment)] transition"
          >
            Previous
          </button>
          <button
            disabled={page >= Math.ceil(total / 10)}
            onClick={() => setPage(p => p + 1)}
            className="px-3 py-1.5 rounded-lg border border-[var(--color-hairline)] bg-[var(--color-canvas)] disabled:opacity-40 hover:bg-[var(--color-canvas-parchment)] transition"
          >
            Next
          </button>
        </div>
      </div>

      {selectedUserId && (
        <CustomerDetailModal userId={selectedUserId} onClose={() => setSelectedUserId(null)} />
      )}
    </div>
  )
}
