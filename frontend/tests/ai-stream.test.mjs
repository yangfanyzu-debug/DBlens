import { test } from 'node:test'
import assert from 'node:assert/strict'

const { streamAiChat } = await import('../src/api/ai.ts')

function createPayload() {
  return {
    connId: 'conn-1',
    database: 'main',
    editorSql: '',
    selectedSql: '',
    schema: null,
    message: '生成查询',
    history: [],
  }
}

test('streamAiChat rejects when the SSE stream ends before a done event', async () => {
  const originalFetch = globalThis.fetch
  const originalDocument = globalThis.document
  const encoder = new TextEncoder()

  globalThis.document = { cookie: '' }
  globalThis.fetch = async () => new Response(new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode('event: delta\ndata: {"content":"SELECT"}\n\n'))
      controller.close()
    },
  }), {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  })

  try {
    await assert.rejects(
      streamAiChat(createPayload(), { onDelta() {} }),
      /AI 响应意外中断/,
    )
  } finally {
    globalThis.fetch = originalFetch
    globalThis.document = originalDocument
  }
})

test('streamAiChat resolves after receiving a done event', async () => {
  const originalFetch = globalThis.fetch
  const originalDocument = globalThis.document
  const encoder = new TextEncoder()
  const deltas = []

  globalThis.document = { cookie: '' }
  globalThis.fetch = async () => new Response(new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(
        'event: delta\ndata: {"content":"SELECT 1"}\n\n' +
        'event: done\ndata: {}\n\n',
      ))
      controller.close()
    },
  }), {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  })

  try {
    await streamAiChat(createPayload(), {
      onDelta(content) {
        deltas.push(content)
      },
    })
    assert.deepEqual(deltas, ['SELECT 1'])
  } finally {
    globalThis.fetch = originalFetch
    globalThis.document = originalDocument
  }
})
