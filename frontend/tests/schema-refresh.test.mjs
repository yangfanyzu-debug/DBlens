import { test } from 'node:test'
import assert from 'node:assert/strict'

const { queryResultChangesSchema } = await import('../src/utils/schemaRefresh.ts')

test('queryResultChangesSchema detects table-affecting statements', () => {
  assert.equal(queryResultChangesSchema([{ sql: 'CREATE TABLE demo (id int)', type: 'CREATE' }]), true)
  assert.equal(queryResultChangesSchema([{ sql: 'alter table demo add column name varchar(20)', type: 'ALTER' }]), true)
  assert.equal(queryResultChangesSchema([{ sql: 'drop table demo', type: 'DROP' }]), true)
  assert.equal(queryResultChangesSchema([{ sql: 'select * from demo', type: 'SELECT' }]), false)
})
