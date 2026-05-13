import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import assert from 'node:assert/strict'

const styleSource = readFileSync(new URL('../src/style.css', import.meta.url), 'utf8')

test('global styles do not request external Google font assets', () => {
  assert.doesNotMatch(styleSource, /fonts\.googleapis\.com/)
  assert.doesNotMatch(styleSource, /fonts\.gstatic\.com/)
})
