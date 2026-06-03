export interface QueryHistoryEntry {
  sql: string
  connId: string
  database: string
  ran_at: number
}

export interface SavedQuery {
  id: string
  title: string
  sql: string
  saved_at: number
}

const MAX_HISTORY = 30

export function addQueryHistoryEntry(
  history: QueryHistoryEntry[],
  entry: QueryHistoryEntry,
): QueryHistoryEntry[] {
  const sql = entry.sql.trim()
  if (!sql) return history

  const deduped = history.filter(item => item.sql.trim() !== sql)
  return [{ ...entry, sql }, ...deduped].slice(0, MAX_HISTORY)
}

export function buildSavedQuery(sql: string, now = Date.now()): SavedQuery {
  const trimmed = sql.trim()
  const firstLine = trimmed.split('\n').find(line => line.trim())?.trim() || '未命名查询'

  return {
    id: `saved-${now}`,
    title: firstLine.slice(0, 80),
    sql: trimmed,
    saved_at: now,
  }
}

export function toggleSavedQuery(saved: SavedQuery[], sql: string, now = Date.now()): SavedQuery[] {
  const trimmed = sql.trim()
  if (!trimmed) return saved

  if (saved.some(item => item.sql.trim() === trimmed)) {
    return saved.filter(item => item.sql.trim() !== trimmed)
  }

  return [buildSavedQuery(trimmed, now), ...saved]
}
