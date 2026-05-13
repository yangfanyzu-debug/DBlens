export interface TreeSearchPart {
  text: string
  match: boolean
}

export function getTreeStoreRoot(store: any) {
  return store?.state?.root ?? store?.root ?? null
}

export function expandTreeNode(store: any, node: any): boolean {
  if (!node) return false

  if (typeof store?.expandNode === 'function') {
    store.expandNode(node)
    return true
  }

  if (typeof node.expand === 'function') {
    node.expand()
    return true
  }

  if ('expanded' in node) {
    node.expanded = true
    return true
  }

  return false
}

export function collapseTreeNode(store: any, node: any): boolean {
  if (!node) return false

  if (typeof store?.collapseNode === 'function') {
    store.collapseNode(node)
    return true
  }

  if (typeof node.collapse === 'function') {
    node.collapse()
    return true
  }

  if ('expanded' in node) {
    node.expanded = false
    return true
  }

  return false
}

export function matchesTreeSearch(label: unknown, query: string): boolean {
  const normalizedQuery = query.trim().toLowerCase()
  if (!normalizedQuery) return true
  return String(label ?? '').toLowerCase().includes(normalizedQuery)
}

export function splitTreeSearchLabel(label: unknown, query: string): TreeSearchPart[] {
  const text = String(label ?? '')
  const normalizedQuery = query.trim().toLowerCase()
  if (!normalizedQuery) return [{ text, match: false }]

  const lowerText = text.toLowerCase()
  const start = lowerText.indexOf(normalizedQuery)
  if (start < 0) return [{ text, match: false }]

  const end = start + normalizedQuery.length
  const parts: TreeSearchPart[] = []
  if (start > 0) parts.push({ text: text.slice(0, start), match: false })
  parts.push({ text: text.slice(start, end), match: true })
  if (end < text.length) parts.push({ text: text.slice(end), match: false })
  return parts
}
