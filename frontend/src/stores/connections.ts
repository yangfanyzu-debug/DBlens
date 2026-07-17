import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Connection, ConnectionForm } from '@/api/connections'
import * as api from '@/api/connections'
import { markConnectionUsed, type ConnectionUseMap } from '@/utils/connectionRecents'

const RECENTS_KEY = 'dblens:connection-recents'

function loadRecents(): ConnectionUseMap {
  if (typeof localStorage === 'undefined') return {}
  try {
    return JSON.parse(localStorage.getItem(RECENTS_KEY) || '{}')
  } catch {
    return {}
  }
}

function saveRecents(recents: ConnectionUseMap) {
  if (typeof localStorage === 'undefined') return
  localStorage.setItem(RECENTS_KEY, JSON.stringify(recents))
}

export const useConnectionsStore = defineStore('connections', () => {
  const connections = ref<Connection[]>([])
  const activeConnId = ref<string | null>(null)
  const activeDatabaseByConn = ref<Record<string, string>>({})
  const recentUse = ref<ConnectionUseMap>(loadRecents())

  async function fetchAll() {
    connections.value = await api.listConnections()
  }

  async function create(form: ConnectionForm) {
    const conn = await api.createConnection(form)
    connections.value.push(conn)
    return conn
  }

  async function update(id: string, form: ConnectionForm) {
    const conn = await api.updateConnection(id, form)
    const idx = connections.value.findIndex(c => c.id === id)
    if (idx >= 0) connections.value[idx] = conn
    return conn
  }

  async function remove(id: string) {
    await api.deleteConnection(id)
    connections.value = connections.value.filter(c => c.id !== id)
    if (activeConnId.value === id) activeConnId.value = null
  }

  async function connect(id: string) {
    await api.openConnection(id)
    activeConnId.value = id
    recentUse.value = markConnectionUsed(recentUse.value, id)
    saveRecents(recentUse.value)
  }

  function setActiveDatabase(connId: string, database: string) {
    activeDatabaseByConn.value[connId] = database
  }

  return { connections, activeConnId, activeDatabaseByConn, recentUse, fetchAll, create, update, remove, connect, setActiveDatabase }
})
