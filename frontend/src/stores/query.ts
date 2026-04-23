import { defineStore } from 'pinia'
import { ref } from 'vue'

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

export const useQueryStore = defineStore('query', () => {
  const results = ref<Record<string, QueryState>>({})

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

  return { results, setRunning, setResult, getResult }
})
