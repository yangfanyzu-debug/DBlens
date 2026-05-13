import { test } from 'node:test'
import assert from 'node:assert/strict'

const { formatCellValue } = await import('../src/utils/displayFormat.ts')

test('formatCellValue displays ISO datetime strings with a space separator', () => {
  assert.equal(formatCellValue('2026-05-09T10:23:45'), '2026-05-09 10:23:45')
})

test('formatCellValue keeps non-date strings unchanged', () => {
  assert.equal(formatCellValue('TASK-2026-05-09T10:23:45'), 'TASK-2026-05-09T10:23:45')
})

test('formatCellValue preserves null and number values', () => {
  assert.equal(formatCellValue(null), null)
  assert.equal(formatCellValue(42), 42)
})
