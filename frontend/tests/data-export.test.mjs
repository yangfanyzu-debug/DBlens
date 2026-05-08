import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import assert from 'node:assert/strict'

const source = readFileSync(new URL('../src/api/data.ts', import.meta.url), 'utf8')

test('exportData uses the authenticated HTTP client for downloads', () => {
  assert.match(source, /export const exportData[\s\S]*http\.get/)
  assert.match(source, /responseType:\s*['"]blob['"]/)
  assert.doesNotMatch(source, /export const exportData[\s\S]*=>\s*`\/dblens-api\/data/)
})
