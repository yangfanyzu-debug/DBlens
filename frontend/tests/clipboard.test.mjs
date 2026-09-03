import { test } from 'node:test'
import assert from 'node:assert/strict'

import { copyTextToClipboard } from '../src/utils/clipboard.ts'

function setup(t, clipboard, result = true) {
  let selected = false
  let removed = false
  let copied
  const textarea = {
    value: '', style: {}, focus() {}, select() { selected = true },
  }
  const previousNavigator = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { clipboard } })
  const previous = Object.getOwnPropertyDescriptor(globalThis, 'document')
  Object.defineProperty(globalThis, 'document', { configurable: true, value: {
    createElement: () => textarea,
    body: { appendChild() {}, removeChild() { removed = true } },
    execCommand(command) {
      assert.equal(command, 'copy')
      assert.equal(selected, true)
      if (result instanceof Error) throw result
      if (result) copied = textarea.value
      return result
    },
  } })
  t.after(() => {
    if (previousNavigator) Object.defineProperty(globalThis, 'navigator', previousNavigator)
    else delete globalThis.navigator
    if (previous) Object.defineProperty(globalThis, 'document', previous)
    else delete globalThis.document
  })
  return { copied: () => copied, removed: () => removed }
}

test('HTTP page without Clipboard API copies through selected textarea', async (t) => {
  const state = setup(t, undefined)
  await copyTextToClipboard('SELECT 1;\n-- 中文')
  assert.equal(state.copied(), 'SELECT 1;\n-- 中文')
  assert.equal(state.removed(), true)
})

test('blocked Clipboard API falls back to textarea copy', async (t) => {
  const state = setup(t, { writeText: async () => { throw new Error('Denied') } })
  await copyTextToClipboard('SELECT 2;')
  assert.equal(state.copied(), 'SELECT 2;')
})

test('failed copy rejects instead of reporting success and removes textarea', async (t) => {
  const state = setup(t, undefined, false)
  await assert.rejects(copyTextToClipboard('SELECT 3;'), /Clipboard copy failed/)
  assert.equal(state.removed(), true)
})

test('copy exception still removes temporary textarea', async (t) => {
  const state = setup(t, undefined, new Error('Denied'))
  await assert.rejects(copyTextToClipboard('SELECT 4;'), /Denied/)
  assert.equal(state.removed(), true)
})

test('available Clipboard API receives the SQL', async (t) => {
  let copied
  const state = setup(t, { writeText: async (text) => { copied = text } })
  await copyTextToClipboard('SELECT 5;')
  assert.equal(copied, 'SELECT 5;')
  assert.equal(state.removed(), false)
})
