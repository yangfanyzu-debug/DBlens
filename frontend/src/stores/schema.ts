import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/databases'

interface ColumnDef {
  name: string
  type: string
  nullable: boolean
  default: any
  comment: string | null
  primary_key: boolean
  auto_increment: boolean
}

interface DbSchema {
  tables: string[]
  columns: Record<string, ColumnDef[]>
}

export const useSchemaStore = defineStore('schema', () => {
  // { connId: { dbName: DbSchema } }
  const cache = ref<Record<string, Record<string, DbSchema>>>({})

  async function loadSchema(connId: string, database: string) {
    if (cache.value[connId]?.[database]) return
    const schema = await api.getSchema(connId, database)
    if (!cache.value[connId]) cache.value[connId] = {}
    cache.value[connId][database] = schema
  }

  function getSchema(connId: string, database: string): DbSchema | null {
    return cache.value[connId]?.[database] ?? null
  }

  function clearConnection(connId: string) {
    delete cache.value[connId]
  }

  return { cache, loadSchema, getSchema, clearConnection }
})
