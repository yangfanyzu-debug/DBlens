import { test } from 'node:test'
import assert from 'node:assert/strict'

globalThis.document = { cookie: '' }

const { default: http } = await import('../src/api/http.ts')

test('GET API requests bypass browser cache revalidation', async () => {
  const handler = http.interceptors.request.handlers.at(-1).fulfilled
  const config = await handler({
    method: 'get',
    url: '/connections',
    params: { group: 'default' },
    headers: {},
  })

  assert.equal(config.headers['Cache-Control'], 'no-store')
  assert.equal(config.headers.Pragma, 'no-cache')
  assert.equal(config.headers.Expires, '0')
  assert.equal(config.params.group, 'default')
  assert.match(config.params._ts, /^\d+$/)
})
