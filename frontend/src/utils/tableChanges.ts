export interface TableChange {
  op: string
  pk_col?: string
  pk_val?: string
  values?: Record<string, any>
}

function hasInsertValue(value: any) {
  return value !== null && value !== undefined && value !== ''
}

export function buildInsertValues(row: Record<string, any>, columnNames: string[]) {
  const values: Record<string, any> = {}
  for (const name of columnNames) {
    if (hasInsertValue(row[name])) values[name] = row[name]
  }
  return values
}

export function buildTableChangePayload(changes: TableChange[], columnNames: string[]) {
  return changes
    .map(change => {
      if (change.op !== 'insert') return change
      return { ...change, values: buildInsertValues(change.values || {}, columnNames) }
    })
    .filter(change => change.op !== 'insert' || Object.keys(change.values || {}).length > 0)
}

export function isInsertedRowChange(row: Record<string, any>, changes: TableChange[]) {
  return changes.some(change => change.op === 'insert' && change.values === row)
}
