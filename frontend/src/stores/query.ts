import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  addQueryHistoryEntry,
  toggleSavedQuery,
  type QueryHistoryEntry,
  type SavedQuery,
} from '@/utils/queryHistory'

export interface QueryResult {
  sql: string
  type: string
  columns: string[]
  rows: any[][]
  row_count: number
  affected_rows: number | null
  execution_ms: number
}

export interface QueryState {
  status: 'idle' | 'running' | 'success' | 'error' | 'killed'
  statements: QueryResult[]
  total_ms: number
  error: string | null
}

const HISTORY_KEY = 'dblens:query-history'
const SAVED_KEY = 'dblens:saved-queries'

function loadJson<T>(key: string, fallback: T): T {
  if (typeof localStorage === 'undefined') return fallback
  try {
    return JSON.parse(localStorage.getItem(key) || '') as T
  } catch {
    return fallback
  }
}

function saveJson<T>(key: string, value: T) {
  if (typeof localStorage === 'undefined') return
  localStorage.setItem(key, JSON.stringify(value))
}

export const useQueryStore = defineStore('query', () => {
  const results = ref<Record<string, QueryState>>({})
  const history = ref<QueryHistoryEntry[]>(loadJson<QueryHistoryEntry[]>(HISTORY_KEY, []))
  const savedQueries = ref<SavedQuery[]>(loadJson<SavedQuery[]>(SAVED_KEY, []))

  function setRunning(queryId: string) {
    results.value[queryId] = { status: 'running', statements: [], total_ms: 0, error: null }
  }

  function setResult(queryId: string, data: any) {
    results.value[queryId] = {
      status: data.status,
      statements: data.statements ?? [],
      total_ms: data.total_ms ?? 0,
      error: data.error ?? null,
    }
  }

  function getResult(queryId: string): QueryState | null {
    return results.value[queryId] ?? null
  }

  function recordHistory(entry: QueryHistoryEntry) {
    history.value = addQueryHistoryEntry(history.value, entry)
    saveJson(HISTORY_KEY, history.value)
  }

  function toggleSaved(sql: string) {
    savedQueries.value = toggleSavedQuery(savedQueries.value, sql)
    saveJson(SAVED_KEY, savedQueries.value)
  }

  function clearHistory() {
    history.value = []
    saveJson(HISTORY_KEY, history.value)
  }

  return {
    results,
    history,
    savedQueries,
    setRunning,
    setResult,
    getResult,
    recordHistory,
    toggleSaved,
    clearHistory,
  }
})
