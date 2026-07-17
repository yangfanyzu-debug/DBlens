import { test } from 'node:test'
import assert from 'node:assert/strict'

const { appendAiDelta, extractSqlBlocks } = await import('../src/utils/aiChat.ts')

test('appendAiDelta appends streamed content to the last assistant message', () => {
  const messages = [{ role: 'assistant', content: 'SELECT' }]

  assert.deepEqual(appendAiDelta(messages, ' 1'), [
    { role: 'assistant', content: 'SELECT 1' },
  ])
})

test('appendAiDelta creates an assistant message when the last message is user', () => {
  const messages = [{ role: 'user', content: '写 SQL' }]

  assert.deepEqual(appendAiDelta(messages, 'SELECT 1'), [
    { role: 'user', content: '写 SQL' },
    { role: 'assistant', content: 'SELECT 1' },
  ])
})

test('extractSqlBlocks returns fenced SQL code blocks', () => {
  assert.deepEqual(extractSqlBlocks('说明\n```sql\nSELECT * FROM users;\n```'), [
    'SELECT * FROM users;',
  ])
})
