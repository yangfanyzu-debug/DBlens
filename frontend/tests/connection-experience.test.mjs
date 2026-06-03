import { test } from 'node:test'
import assert from 'node:assert/strict'

const {
  getConnectionEnvironment,
  getConnectionEndpoint,
  getTestFeedback,
} = await import('../src/utils/connectionExperience.ts')

test('getConnectionEnvironment marks localhost connections as local', () => {
  assert.deepEqual(getConnectionEnvironment({ host: '127.0.0.1' }), {
    label: '本地',
    tone: 'info',
  })
})

test('getConnectionEnvironment marks production-like names as production', () => {
  assert.deepEqual(getConnectionEnvironment({ name: 'prod-orders', host: '10.0.0.8' }), {
    label: '生产',
    tone: 'danger',
  })
})

test('getConnectionEndpoint includes database when available', () => {
  assert.equal(
    getConnectionEndpoint({ host: 'db.internal', port: 3306, database: 'orders' }),
    'db.internal:3306 / orders',
  )
})

test('getTestFeedback explains a successful connection target', () => {
  assert.deepEqual(
    getTestFeedback(
      { success: true, message: 'OK', latency_ms: 42 },
      { host: 'db.internal', port: 3306, database: 'orders' },
    ),
    {
      type: 'success',
      title: '连接成功',
      detail: '已连接到 db.internal:3306 / orders，耗时 42ms。',
    },
  )
})

test('getTestFeedback adds practical advice for authentication failures', () => {
  assert.deepEqual(
    getTestFeedback(
      { success: false, message: 'Access denied for user root', latency_ms: 12 },
      { host: 'db.internal', port: 3306 },
    ),
    {
      type: 'error',
      title: '认证失败',
      detail: 'Access denied for user root。请检查用户名、密码，以及该账号是否允许从当前来源访问。',
    },
  )
})
