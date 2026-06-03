import { test } from 'node:test'
import assert from 'node:assert/strict'

const {
  getColumnStorageKey,
  getResultLimitNotice,
} = await import('../src/utils/resultTableUx.ts')

test('getColumnStorageKey scopes saved width by connection, database, and column', () => {
  assert.equal(
    getColumnStorageKey('conn-1', 'orders', 'created_at'),
    'dblens:column-width:conn-1:orders:created_at',
  )
})

test('getResultLimitNotice warns when result count reaches likely preview limit', () => {
  assert.equal(
    getResultLimitNotice({ row_count: 1000, rows: Array.from({ length: 1000 }) }),
    '已显示 1000 行，结果可能已被限制。需要完整数据时请使用导出。',
  )
})

test('getResultLimitNotice stays quiet for small result sets', () => {
  assert.equal(getResultLimitNotice({ row_count: 12, rows: Array.from({ length: 12 }) }), '')
})
