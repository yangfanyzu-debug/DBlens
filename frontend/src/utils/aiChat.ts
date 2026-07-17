export type AiRole = 'user' | 'assistant'

export interface AiMessage {
  role: AiRole
  content: string
}

export interface AiSchemaContext {
  tables: string[]
  columns: Record<string, any[]>
}

export interface AiChatContext {
  connId: string
  database: string
  editorSql: string
  selectedSql: string
  schema: AiSchemaContext | null
}

export function appendAiDelta(messages: AiMessage[], delta: string): AiMessage[] {
  const last = messages[messages.length - 1]
  if (last?.role === 'assistant') {
    return [
      ...messages.slice(0, -1),
      { ...last, content: last.content + delta },
    ]
  }

  return [...messages, { role: 'assistant', content: delta }]
}

export function extractSqlBlocks(content: string): string[] {
  const blocks: string[] = []
  const pattern = /```(?:sql)?\s*([\s\S]*?)```/gi
  let match: RegExpExecArray | null

  while ((match = pattern.exec(content)) !== null) {
    const sql = match[1]?.trim()
    if (sql) blocks.push(sql)
  }

  return blocks
}
