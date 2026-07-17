export type SqlRow = Record<string, any>

function quoteIdentifier(name: string) {
  return `\`${name.replace(/`/g, '``')}\``
}

export function formatSqlValue(value: any): string {
  if (value === null || value === undefined) return 'NULL'
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : 'NULL'
  if (typeof value === 'boolean') return value ? '1' : '0'
  const text = value instanceof Date ? value.toISOString().slice(0, 19).replace('T', ' ') : String(value)
  return `'${text.replace(/'/g, "''")}'`
}

export function buildInsertSql(table: string, columns: string[], rows: SqlRow[]) {
  const colSql = columns.map(quoteIdentifier).join(', ')
  return rows
    .map(row => {
      const values = columns.map(col => formatSqlValue(row[col])).join(', ')
      return `INSERT INTO ${quoteIdentifier(table)} (${colSql}) VALUES (${values});`
    })
    .join('\n')
}

export function buildUpdateSql(table: string, columns: string[], rows: SqlRow[], whereColumn = columns[0]) {
  if (!whereColumn) return ''
  const updateColumns = columns.filter(col => col !== whereColumn)
  return rows
    .filter(row => row[whereColumn] !== null && row[whereColumn] !== undefined && row[whereColumn] !== '')
    .map(row => {
      const assignments = updateColumns
        .map(col => `${quoteIdentifier(col)} = ${formatSqlValue(row[col])}`)
        .join(', ')
      return `UPDATE ${quoteIdentifier(table)} SET ${assignments} WHERE ${quoteIdentifier(whereColumn)} = ${formatSqlValue(row[whereColumn])};`
    })
    .join('\n')
}
