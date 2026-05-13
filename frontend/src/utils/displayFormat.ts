const ISO_DATETIME_PATTERN = /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(\.\d+)?(Z|[+-]\d{2}:\d{2})?$/

export function formatCellValue(value: unknown): unknown {
  if (typeof value !== 'string') return value

  const match = ISO_DATETIME_PATTERN.exec(value)
  if (!match) return value

  return `${match[1]} ${match[2]}`
}
