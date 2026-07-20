import type { AiChatContext, AiMessage } from '@/utils/aiChat'

interface StreamHandlers {
  onDelta: (content: string) => void
  onDone?: () => void
  onError?: (message: string) => void
}

export interface AiChatPayload extends AiChatContext {
  message: string
  history: AiMessage[]
}

export async function streamAiChat(
  payload: AiChatPayload,
  handlers: StreamHandlers,
  signal?: AbortSignal,
) {
  const response = await fetch('/dblens-api/ai/chat/stream', {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({
      conn_id: payload.connId,
      database: payload.database,
      message: payload.message,
      editor_sql: payload.editorSql,
      selected_sql: payload.selectedSql,
      history: payload.history,
      schema: payload.schema ?? { tables: [], columns: {} },
    }),
    signal,
  })

  if (!response.ok) {
    throw new Error(await readError(response))
  }
  if (!response.body) {
    throw new Error('浏览器不支持流式响应')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let completed = false
  let failed = false
  const streamHandlers: StreamHandlers = {
    ...handlers,
    onDone() {
      completed = true
      handlers.onDone?.()
    },
    onError(message) {
      failed = true
      handlers.onError?.(message)
    },
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    buffer = consumeSseBuffer(buffer, streamHandlers)
  }

  buffer += decoder.decode()
  consumeSseBuffer(buffer, streamHandlers)
  if (!completed && !failed) {
    throw new Error('AI 响应意外中断，请重试')
  }
}

function buildHeaders() {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream',
  }
  const token = getRuoYiToken()
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

function getRuoYiToken() {
  const tokenPair = document.cookie
    .split('; ')
    .find(item => item.startsWith('Admin-Token='))
  if (!tokenPair) return null
  const value = tokenPair.slice('Admin-Token='.length)
  return value ? decodeURIComponent(value) : null
}

function consumeSseBuffer(buffer: string, handlers: StreamHandlers) {
  const parts = buffer.split('\n\n')
  const rest = parts.pop() ?? ''
  for (const part of parts) handleSseBlock(part, handlers)
  return rest
}

function handleSseBlock(block: string, handlers: StreamHandlers) {
  const event = block.split('\n').find(line => line.startsWith('event:'))?.slice('event:'.length).trim()
  const data = block.split('\n').find(line => line.startsWith('data:'))?.slice('data:'.length).trim()
  const payload = data ? JSON.parse(data) : {}

  if (event === 'delta') handlers.onDelta(payload.content ?? '')
  if (event === 'done') handlers.onDone?.()
  if (event === 'error') handlers.onError?.(payload.message ?? 'AI 请求失败')
}

async function readError(response: Response) {
  try {
    const data = await response.json()
    return data.detail || data.message || response.statusText
  } catch {
    return response.statusText
  }
}
