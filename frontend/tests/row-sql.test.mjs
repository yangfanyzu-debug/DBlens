import { test } from 'node:test'
import assert from 'node:assert/strict'

const { buildInsertSql, buildUpdateSql, formatSqlValue } = await import('../src/utils/rowSql.ts')
const { inferSingleSelectTableName } = await import('../src/utils/sqlTableName.ts')

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

test('buildUpdateSql accepts an explicit where column', () => {
  const sql = buildUpdateSql('categories', ['label', 'id', 'sort_order'], [
    { id: 5, label: 'test', sort_order: 10 },
  ], 'id')

  assert.equal(
    sql,
    "UPDATE `categories` SET `label` = 'test', `sort_order` = 10 WHERE `id` = 5;",
  )
})

test('buildUpdateSql skips rows without where values', () => {
  assert.equal(buildUpdateSql('categories', ['id', 'label'], [{ id: null, label: 'x' }]), '')
})

test('build SQL quotes qualified table names', () => {
  assert.equal(
    buildInsertSql('ry-cloud.categories', ['id'], [{ id: 1 }]),
    'INSERT INTO `ry-cloud`.`categories` (`id`) VALUES (1);',
  )
})

test('inferSingleSelectTableName extracts safe single table selects', () => {
  assert.equal(inferSingleSelectTableName('select * from categories'), 'categories')
  assert.equal(inferSingleSelectTableName('select c.id from `ry-cloud`.`categories` c where c.id = 1'), 'ry-cloud.categories')
  assert.equal(inferSingleSelectTableName('select * from categories as c order by id desc'), 'categories')
})

test('inferSingleSelectTableName rejects complex result sources', () => {
  assert.equal(inferSingleSelectTableName('select * from categories c join users u on u.id = c.id'), null)
  assert.equal(inferSingleSelectTableName('select * from categories union select * from users'), null)
  assert.equal(inferSingleSelectTableName('with x as (select * from categories) select * from x'), null)
  assert.equal(inferSingleSelectTableName('select * from (select * from categories) x'), null)
  assert.equal(inferSingleSelectTableName('select * from categories, users'), null)
})
