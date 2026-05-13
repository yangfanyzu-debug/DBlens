import { test } from 'node:test'
import assert from 'node:assert/strict'

const { getSqlToExecute } = await import('../src/utils/sqlSelection.ts')

test('getSqlToExecute returns selected SQL when selection has content', () => {
  assert.equal(
    getSqlToExecute('select * from users', 'select * from users;\nselect * from orders;'),
    'select * from users',
  )
})

test('getSqlToExecute returns full SQL when selection is empty', () => {
  assert.equal(
    getSqlToExecute('', 'select * from users;\nselect * from orders;'),
    'select * from users;\nselect * from orders;',
  )
})

test('getSqlToExecute returns full SQL when selection is only whitespace', () => {
  assert.equal(getSqlToExecute('   \n', 'select 1'), 'select 1')
})
