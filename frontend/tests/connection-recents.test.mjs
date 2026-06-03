import { test } from 'node:test'
import assert from 'node:assert/strict'

const {
  buildConnectionSearchText,
  createConnectionCopy,
  markConnectionUsed,
  sortConnectionsByRecentUse,
} = await import('../src/utils/connectionRecents.ts')

test('buildConnectionSearchText includes connection fields users search for', () => {
  assert.equal(
    buildConnectionSearchText({
      name: 'orders-prod',
      db_type: 'mysql',
      host: 'db.internal',
      database: 'orders',
      group_name: 'production',
    }),
    'orders-prod mysql db.internal orders production',
  )
})

test('createConnectionCopy clears secrets and uses a copy name', () => {
  assert.deepEqual(
    createConnectionCopy({
      name: 'orders',
      db_type: 'mysql',
      host: 'db.internal',
      port: 3306,
      username: 'root',
      password: 'secret',
      database: 'orders',
      group_name: 'prod',
      ssh_enabled: false,
      ssh_port: 22,
      ssh_password: 'ssh-secret',
      ssh_private_key: 'private-key',
      ssl_enabled: false,
    }),
    {
      name: 'orders 副本',
      db_type: 'mysql',
      host: 'db.internal',
      port: 3306,
      username: 'root',
      password: '',
      database: 'orders',
      group_name: 'prod',
      ssh_enabled: false,
      ssh_port: 22,
      ssh_password: '',
      ssh_private_key: '',
      ssl_enabled: false,
    },
  )
})

test('markConnectionUsed records the latest timestamp for a connection', () => {
  assert.deepEqual(markConnectionUsed({ a: 10 }, 'b', 20), { a: 10, b: 20 })
  assert.deepEqual(markConnectionUsed({ a: 10 }, 'a', 30), { a: 30 })
})

test('sortConnectionsByRecentUse orders recently used connections first', () => {
  const sorted = sortConnectionsByRecentUse(
    [{ id: 'a', name: 'A' }, { id: 'b', name: 'B' }, { id: 'c', name: 'C' }],
    { c: 10, a: 30 },
  )

  assert.deepEqual(sorted.map(conn => conn.id), ['a', 'c', 'b'])
})
