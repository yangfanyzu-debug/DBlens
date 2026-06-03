import { test } from 'node:test'
import assert from 'node:assert/strict'

const {
  addQueryHistoryEntry,
  buildSavedQuery,
  toggleSavedQuery,
} = await import('../src/utils/queryHistory.ts')

test('addQueryHistoryEntry stores newest unique SQL first', () => {
  const next = addQueryHistoryEntry(
    [{ sql: 'select 1', database: 'db1', connId: 'a', ran_at: 10 }],
    { sql: 'select 2', database: 'db1', connId: 'a', ran_at: 20 },
  )

  assert.deepEqual(next.map(entry => entry.sql), ['select 2', 'select 1'])
})

test('addQueryHistoryEntry moves repeated SQL to the top', () => {
  const next = addQueryHistoryEntry(
    [
      { sql: 'select 1', database: 'db1', connId: 'a', ran_at: 10 },
      { sql: 'select 2', database: 'db1', connId: 'a', ran_at: 20 },
    ],
    { sql: 'select 1', database: 'db1', connId: 'a', ran_at: 30 },
  )

  assert.deepEqual(next, [
    { sql: 'select 1', database: 'db1', connId: 'a', ran_at: 30 },
    { sql: 'select 2', database: 'db1', connId: 'a', ran_at: 20 },
  ])
})

test('buildSavedQuery uses the first SQL line as a readable title', () => {
  assert.deepEqual(buildSavedQuery('select * from orders\nwhere id = 1', 99), {
    id: 'saved-99',
    title: 'select * from orders',
    sql: 'select * from orders\nwhere id = 1',
    saved_at: 99,
  })
})

test('toggleSavedQuery adds and removes saved queries by SQL', () => {
  const saved = toggleSavedQuery([], 'select 1', 10)
  assert.equal(saved.length, 1)
  assert.deepEqual(toggleSavedQuery(saved, 'select 1', 20), [])
})
