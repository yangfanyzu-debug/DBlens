import { test } from 'node:test'
import assert from 'node:assert/strict'

const { assessSqlRisk } = await import('../src/utils/sqlRisk.ts')

test('assessSqlRisk returns safe for read-only selects', () => {
  assert.deepEqual(assessSqlRisk('select * from users limit 20'), {
    risky: false,
    level: 'none',
    title: '',
    reasons: [],
  })
})

test('assessSqlRisk warns on delete without where', () => {
  const risk = assessSqlRisk('delete from users')

  assert.equal(risk.risky, true)
  assert.equal(risk.level, 'high')
  assert.equal(risk.title, '危险 SQL 需要确认')
  assert.deepEqual(risk.reasons, ['DELETE 未包含 WHERE 条件，可能删除整表数据。'])
})

test('assessSqlRisk warns on update without where', () => {
  const risk = assessSqlRisk('update users set active = 0')

  assert.equal(risk.risky, true)
  assert.equal(risk.level, 'high')
  assert.deepEqual(risk.reasons, ['UPDATE 未包含 WHERE 条件，可能更新整表数据。'])
})

test('assessSqlRisk warns on destructive DDL', () => {
  const risk = assessSqlRisk('drop table users; truncate table logs;')

  assert.equal(risk.risky, true)
  assert.equal(risk.level, 'high')
  assert.deepEqual(risk.reasons, [
    'DROP 会删除数据库对象。',
    'TRUNCATE 会清空整表数据。',
  ])
})
