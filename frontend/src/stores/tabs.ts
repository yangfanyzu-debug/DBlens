import { defineStore } from 'pinia'
import { ref } from 'vue'

export type TabType = 'editor' | 'table'

export interface Tab {
  id: string
  type: TabType
  title: string
  connId: string
  database?: string
  table?: string
}

export const useTabsStore = defineStore('tabs', () => {
  const tabs = ref<Tab[]>([])
  const activeTabId = ref<string | null>(null)

  function openEditorTab(connId: string, database?: string) {
    const id = `editor-${Date.now()}`
    tabs.value.push({ id, type: 'editor', title: 'SQL Editor', connId, database })
    activeTabId.value = id
    return id
  }

  function openTableTab(connId: string, database: string, table: string) {
    const existing = tabs.value.find(t => t.type === 'table' && t.connId === connId && t.database === database && t.table === table)
    if (existing) { activeTabId.value = existing.id; return existing.id }
    const id = `table-${connId}-${database}-${table}`
    tabs.value.push({ id, type: 'table', title: table, connId, database, table })
    activeTabId.value = id
    return id
  }

  function closeTab(id: string) {
    const idx = tabs.value.findIndex(t => t.id === id)
    tabs.value.splice(idx, 1)
    if (activeTabId.value === id) {
      activeTabId.value = tabs.value[Math.max(0, idx - 1)]?.id ?? null
    }
  }

  function closeOtherTabs(id: string) {
    const tab = tabs.value.find(t => t.id === id)
    if (!tab) return
    tabs.value = [tab]
    activeTabId.value = tab.id
  }

  function closeAllTabs() {
    tabs.value = []
    activeTabId.value = null
  }

  function renameTab(id: string, title: string) {
    const tab = tabs.value.find(t => t.id === id)
    if (tab) tab.title = title
  }

  return { tabs, activeTabId, openEditorTab, openTableTab, closeTab, closeOtherTabs, closeAllTabs, renameTab }
})
