interface ConnectionLike {
  id?: string
  name?: string
  db_type?: string
  host?: string
  port?: number
  username?: string
  password?: string
  database?: string
  group_name?: string
  ssh_enabled?: boolean
  ssh_host?: string
  ssh_port?: number
  ssh_username?: string
  ssh_password?: string
  ssh_private_key?: string
  ssl_enabled?: boolean
}

export type ConnectionUseMap = Record<string, number>

export function buildConnectionSearchText(conn: ConnectionLike): string {
  return [
    conn.name,
    conn.db_type,
    conn.host,
    conn.database,
    conn.group_name,
  ].filter(Boolean).join(' ').toLowerCase()
}

export function createConnectionCopy<T extends ConnectionLike>(conn: T): Omit<T, 'id'> {
  const { id: _id, ...copy } = conn
  return {
    ...copy,
    name: `${conn.name || '未命名连接'} 副本`,
    password: '',
    ssh_password: '',
    ssh_private_key: '',
  }
}

export function markConnectionUsed(recents: ConnectionUseMap, connId: string, now = Date.now()): ConnectionUseMap {
  return { ...recents, [connId]: now }
}

export function sortConnectionsByRecentUse<T extends { id: string }>(connections: T[], recents: ConnectionUseMap): T[] {
  return [...connections].sort((a, b) => (recents[b.id] ?? 0) - (recents[a.id] ?? 0))
}

export function formatLastUsed(timestamp?: number): string {
  if (!timestamp) return '未使用'

  return new Date(timestamp).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}
