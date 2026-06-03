interface ResultLike {
  row_count: number
  rows: unknown[]
}

const LIKELY_LIMIT = 1000

export function getColumnStorageKey(connId: string, database: string, column: string): string {
  return `dblens:column-width:${connId}:${database}:${column}`
}

export function getResultLimitNotice(result: ResultLike): string {
  if (result.row_count >= LIKELY_LIMIT && result.rows.length >= LIKELY_LIMIT) {
    return `已显示 ${result.rows.length} 行，结果可能已被限制。需要完整数据时请使用导出。`
  }

  return ''
}
