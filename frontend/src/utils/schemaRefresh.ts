import type { QueryResult } from '@/stores/query'

export const DB_SCHEMA_CHANGED_EVENT = 'dblens:db-schema-changed'

export interface DbSchemaChangedDetail {
  connId: string
  database: string
}

const SCHEMA_CHANGE_PATTERN = /^\s*(create|alter|drop|rename|truncate)\b/i

export function queryResultChangesSchema(statements: QueryResult[] = []) {
  return statements.some(stmt =>
    SCHEMA_CHANGE_PATTERN.test(stmt.sql || '') || SCHEMA_CHANGE_PATTERN.test(stmt.type || '')
  )
}

export function emitDbSchemaChanged(detail: DbSchemaChangedDetail) {
  window.dispatchEvent(new CustomEvent<DbSchemaChangedDetail>(DB_SCHEMA_CHANGED_EVENT, { detail }))
}

export function onDbSchemaChanged(handler: (detail: DbSchemaChangedDetail) => void) {
  const listener = (event: Event) => {
    handler((event as CustomEvent<DbSchemaChangedDetail>).detail)
  }
  window.addEventListener(DB_SCHEMA_CHANGED_EVENT, listener)
  return () => window.removeEventListener(DB_SCHEMA_CHANGED_EVENT, listener)
}
