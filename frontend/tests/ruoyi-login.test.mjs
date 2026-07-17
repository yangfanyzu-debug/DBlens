import { test } from 'node:test'
import assert from 'node:assert/strict'

const { buildRuoYiLoginUrl } = await import('../src/utils/ruoyiLogin.ts')

test('RuoYi login URL redirects back to current DBLens page by default', () => {
  const url = buildRuoYiLoginUrl({
    configuredLoginUrl: '',
    origin: 'http://192.168.0.140',
    currentPath: '/dblens/',
    currentSearch: '',
    currentHash: '#/connections',
  })

  assert.equal(url, 'http://192.168.0.140/login?redirect=%2Fdblens%2F%23%2Fconnections')
})

test('RuoYi login URL preserves configured query parameters', () => {
  const url = buildRuoYiLoginUrl({
    configuredLoginUrl: 'http://192.168.0.140/login?tenant=main',
    origin: 'http://localhost:5173',
    currentPath: '/dblens/',
    currentSearch: '?from=timeout',
    currentHash: '',
  })

  assert.equal(url, 'http://192.168.0.140/login?tenant=main&redirect=%2Fdblens%2F%3Ffrom%3Dtimeout')
})
