import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Connection, ConnectionForm } from '@/api/connections'
import * as api from '@/api/connections'

export const useConnectionsStore = defineStore('connections', () => {
  const connections = ref<Connection[]>([])
  const activeConnId = ref<string | null>(null)

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
  }

  return { connections, activeConnId, fetchAll, create, update, remove, connect }
})
