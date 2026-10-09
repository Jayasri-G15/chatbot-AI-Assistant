import type { Conversation, DocumentInfo, Message } from '../types/chat'

const BASE = '/api/v1'

class ApiError extends Error {
  code: string
  constructor(code: string, message: string) {
    super(message)
    this.code = code
  }
}

async function parseJsonResponse(res: Response) {
  try {
    const text = await res.text()
    if (!text || !text.trim()) return null
    return JSON.parse(text)
  } catch {
    return null
  }
}

async function handle<T>(res: Response): Promise<T> {
  const body = await parseJsonResponse(res)
  if (!res.ok) {
    const err = body?.error
    const message = err?.message ?? (typeof body?.detail === 'string' ? body.detail : body?.detail?.error?.message ?? 'Something went wrong.')
    throw new ApiError(err?.code ?? 'UNKNOWN_ERROR', message)
  }
  if (res.status === 204) return undefined as T
  return body as T
}

function getAuthHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = localStorage.getItem('crm_auth_token')
  const headers: Record<string, string> = { ...extra }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

export const api = {
  listConversations: () =>
    fetch(`${BASE}/conversations`, { headers: getAuthHeaders() }).then((r) => handle<Conversation[]>(r)),

  createConversation: () =>
    fetch(`${BASE}/conversations`, { method: 'POST', headers: getAuthHeaders() }).then((r) => handle<Conversation>(r)),

  renameConversation: (id: string, title: string) =>
    fetch(`${BASE}/conversations/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ title }),
    }).then((r) => handle<Conversation>(r)),

  deleteConversation: (id: string) =>
    fetch(`${BASE}/conversations/${id}`, { method: 'DELETE', headers: getAuthHeaders() }).then((r) => handle<void>(r)),

  listMessages: (conversationId: string) =>
    fetch(`${BASE}/conversations/${conversationId}/messages`, { headers: getAuthHeaders() }).then((r) => handle<Message[]>(r)),

  listDocuments: (conversationId: string) =>
    fetch(`${BASE}/conversations/${conversationId}/documents`, { headers: getAuthHeaders() }).then((r) => handle<DocumentInfo[]>(r)),

  uploadDocument: (conversationId: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return fetch(`${BASE}/conversations/${conversationId}/documents`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: formData,
    }).then((r) => handle<DocumentInfo>(r))
  },

  deleteDocument: (conversationId: string, documentId: string) =>
    fetch(`${BASE}/conversations/${conversationId}/documents/${documentId}`, { method: 'DELETE', headers: getAuthHeaders() }).then((r) =>
      handle<void>(r),
    ),
}

export { ApiError }

export async function* streamMessage(
  conversationId: string,
  content: string,
  documentIds?: string[],
  signal?: AbortSignal,
): AsyncGenerator<
  | { type: 'delta'; content: string }
  | { type: 'agent_step'; agent: string; action: string }
  | { type: 'error'; message: string }
  | { type: 'done' }
> {
  const res = await fetch(`${BASE}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({ content, document_ids: documentIds ?? [] }),
    signal,
  })


  if (!res.ok || !res.body) {
    const body = await parseJsonResponse(res)
    throw new ApiError(body?.error?.code ?? 'UNKNOWN_ERROR', body?.error?.message ?? 'Something went wrong.')
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const parts = buffer.split('\n\n')
    buffer = parts.pop() ?? ''
    for (const part of parts) {
      const line = part.trim()
      if (!line.startsWith('data:')) continue
      const json = line.slice(5).trim()
      if (!json) continue
      yield JSON.parse(json)
    }
  }
}
