import { test } from 'node:test'
import assert from 'node:assert/strict'

const {
  buildInsertValues,
  buildTableChangePayload,
  isInsertedRowChange,
} = await import('../src/utils/tableChanges.ts')

test('insert payload omits every unfilled column', () => {
  const values = buildInsertValues(
    {
      id: null,
      label: 'test',
      parent_id: '',
      icon: undefined,
      sort_order: '10',
      created_at: null,
    },
    ['id', 'label', 'parent_id', 'icon', 'sort_order', 'created_at'],
  )

  assert.deepEqual(values, { label: 'test', sort_order: '10' })
})

test('table change payload drops empty inserts', () => {
  const payload = buildTableChangePayload(
    [{ op: 'insert', values: { id: null, label: '', created_at: null } }],
    ['id', 'label', 'created_at'],
  )

  assert.deepEqual(payload, [])
})

test('inserted row is matched by row reference', () => {
  const row = { id: null, label: 'test' }

  assert.equal(isInsertedRowChange(row, [{ op: 'insert', values: row }]), true)
})
