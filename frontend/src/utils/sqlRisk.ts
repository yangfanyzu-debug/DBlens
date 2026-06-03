export interface SqlRisk {
  risky: boolean
  level: 'none' | 'medium' | 'high'
  title: string
  reasons: string[]
}

export function assessSqlRisk(sql: string): SqlRisk {
  const normalized = stripSqlComments(sql).toLowerCase()
  const statements = normalized
    .split(';')
    .map(statement => statement.trim())
    .filter(Boolean)

  const reasons: string[] = []

  for (const statement of statements) {
    if (/^drop\s+/.test(statement)) {
      reasons.push('DROP 会删除数据库对象。')
    }
    if (/^truncate\s+/.test(statement)) {
      reasons.push('TRUNCATE 会清空整表数据。')
    }
    if (/^delete\s+from\s+/.test(statement) && !/\bwhere\b/.test(statement)) {
      reasons.push('DELETE 未包含 WHERE 条件，可能删除整表数据。')
    }
    if (/^update\s+/.test(statement) && !/\bwhere\b/.test(statement)) {
      reasons.push('UPDATE 未包含 WHERE 条件，可能更新整表数据。')
    }
  }

  if (!reasons.length) {
    return { risky: false, level: 'none', title: '', reasons: [] }
  }

  return {
    risky: true,
    level: 'high',
    title: '危险 SQL 需要确认',
    reasons,
  }
}

function stripSqlComments(sql: string): string {
  return sql
    .replace(/\/\*[\s\S]*?\*\//g, ' ')
    .replace(/--.*$/gm, ' ')
    .replace(/#.*$/gm, ' ')
}
