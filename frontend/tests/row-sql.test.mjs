import { test } from 'node:test'
import assert from 'node:assert/strict'

const { buildInsertSql, buildUpdateSql, formatSqlValue } = await import('../src/utils/rowSql.ts')

test('formatSqlValue escapes strings and preserves SQL nulls', () => {
  assert.equal(formatSqlValue(null), 'NULL')
  assert.equal(formatSqlValue(undefined), 'NULL')
  assert.equal(formatSqlValue("O'Reilly"), "'O''Reilly'")
  assert.equal(formatSqlValue(12), '12')
  assert.equal(formatSqlValue(false), '0')
})

test('buildInsertSql creates insert statements for selected rows', () => {
  const sql = buildInsertSql('categories', ['id', 'label', 'created_at'], [
    { id: 1, label: "Bob's", created_at: null },
  ])

  assert.equal(
    sql,
    "INSERT INTO `categories` (`id`, `label`, `created_at`) VALUES (1, 'Bob''s', NULL);",
  )
})

test('buildUpdateSql uses the first column as where column by default', () => {
  const sql = buildUpdateSql('categories', ['id', 'label', 'sort_order'], [
    { id: 5, label: 'test', sort_order: 10 },
  ])

  assert.equal(
    sql,
    "UPDATE `categories` SET `label` = 'test', `sort_order` = 10 WHERE `id` = 5;",
  )
})

test('buildUpdateSql skips rows without where values', () => {
  assert.equal(buildUpdateSql('categories', ['id', 'label'], [{ id: null, label: 'x' }]), '')
})
