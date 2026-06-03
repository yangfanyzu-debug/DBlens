type Tone = 'success' | 'warning' | 'danger' | 'info'

interface ConnectionLike {
  name?: string
  host?: string
  port?: number
  database?: string
  group_name?: string
}

interface TestResultLike {
  success: boolean
  message: string
  latency_ms?: number | null
}

export function getConnectionEnvironment(conn: ConnectionLike): { label: string; tone: Tone } {
  const text = [conn.name, conn.group_name, conn.database, conn.host].filter(Boolean).join(' ').toLowerCase()
  const host = conn.host?.trim().toLowerCase()

  if (host === '127.0.0.1' || host === 'localhost' || host === '::1') {
    return { label: '本地', tone: 'info' }
  }

  if (/\b(prod|production|prd)\b|生产/.test(text)) {
    return { label: '生产', tone: 'danger' }
  }

  if (/\b(staging|stage|pre|uat)\b|预发|灰度/.test(text)) {
    return { label: '预发', tone: 'warning' }
  }

  if (/\b(test|testing|dev|demo)\b|测试|开发/.test(text)) {
    return { label: '测试', tone: 'success' }
  }

  return { label: '未标记', tone: 'info' }
}

export function getConnectionEndpoint(conn: ConnectionLike): string {
  const host = conn.host?.trim() || '未填写主机'
  const port = conn.port ? `:${conn.port}` : ''
  const database = conn.database?.trim()

  return database ? `${host}${port} / ${database}` : `${host}${port}`
}

export function getTestFeedback(
  result: TestResultLike,
  conn: ConnectionLike,
): { type: 'success' | 'error'; title: string; detail: string } {
  if (result.success) {
    const latency = typeof result.latency_ms === 'number' ? `，耗时 ${result.latency_ms}ms` : ''
    return {
      type: 'success',
      title: '连接成功',
      detail: `已连接到 ${getConnectionEndpoint(conn)}${latency}。`,
    }
  }

  const message = result.message || '连接失败'
  return {
    type: 'error',
    title: classifyFailure(message),
    detail: `${message}。${getFailureAdvice(message)}`,
  }
}

function classifyFailure(message: string): string {
  const normalized = message.toLowerCase()

  if (normalized.includes('access denied') || normalized.includes('authentication') || normalized.includes('password')) {
    return '认证失败'
  }
  if (normalized.includes('timeout') || normalized.includes('refused') || normalized.includes('unreachable')) {
    return '网络不可达'
  }
  if (normalized.includes('unknown database') || normalized.includes('does not exist')) {
    return '数据库不存在'
  }

  return '连接失败'
}

function getFailureAdvice(message: string): string {
  const normalized = message.toLowerCase()

  if (normalized.includes('access denied') || normalized.includes('authentication') || normalized.includes('password')) {
    return '请检查用户名、密码，以及该账号是否允许从当前来源访问。'
  }
  if (normalized.includes('timeout') || normalized.includes('refused') || normalized.includes('unreachable')) {
    return '请检查主机、端口、防火墙和安全组配置。'
  }
  if (normalized.includes('unknown database') || normalized.includes('does not exist')) {
    return '请确认数据库名是否正确，或先创建该数据库。'
  }

  return '请检查连接参数后重试。'
}
