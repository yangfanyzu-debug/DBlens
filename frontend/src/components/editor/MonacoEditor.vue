<template>
  <div ref="containerRef" class="monaco-container" />
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as monaco from 'monaco-editor'
import { format as sqlFormat } from 'sql-formatter'
import { useSchemaStore } from '@/stores/schema'
import { useThemeStore } from '@/stores/theme'

const props = defineProps<{ connId: string; database: string }>()
const emit = defineEmits<{ (e: 'execute', sql: string): void }>()

const containerRef = ref<HTMLElement>()
const schemaStore = useSchemaStore()
const themeStore = useThemeStore()
let editor: monaco.editor.IStandaloneCodeEditor | null = null
let completionDisposable: monaco.IDisposable | null = null

function registerCompletion() {
  completionDisposable?.dispose()
  completionDisposable = monaco.languages.registerCompletionItemProvider('sql', {
    provideCompletionItems(model, position) {
      const schema = schemaStore.getSchema(props.connId, props.database)
      if (!schema) return { suggestions: [] }
      const word = model.getWordUntilPosition(position)
      const range = { startLineNumber: position.lineNumber, endLineNumber: position.lineNumber, startColumn: word.startColumn, endColumn: word.endColumn }
      const suggestions: monaco.languages.CompletionItem[] = []
      for (const tbl of schema.tables) {
        suggestions.push({ label: tbl, kind: monaco.languages.CompletionItemKind.Class, insertText: tbl, range })
        for (const col of schema.columns[tbl] ?? []) {
          suggestions.push({ label: `${tbl}.${col.name}`, kind: monaco.languages.CompletionItemKind.Field, insertText: col.name, range })
        }
      }
      return { suggestions }
    },
  })
}

onMounted(() => {
  if (!containerRef.value) return
  editor = monaco.editor.create(containerRef.value, {
    value: '-- 在此输入 SQL\n',
    language: 'sql',
    theme: themeStore.current === 'dark' ? 'vs-dark' : 'vs',
    fontSize: 14,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    automaticLayout: true,
  })

  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
    const sel = editor!.getSelection()
    const selectedText = sel && !sel.isEmpty() ? editor!.getModel()!.getValueInRange(sel) : ''
    emit('execute', selectedText || editor!.getValue())
  })

  registerCompletion()
})

watch(() => [props.connId, props.database], registerCompletion)

watch(() => themeStore.current, (t) => {
  editor?.updateOptions({ theme: t === 'dark' ? 'vs-dark' : 'vs' })
})

onUnmounted(() => {
  completionDisposable?.dispose()
  editor?.dispose()
})

function getValue() { return editor?.getValue() ?? '' }
function layout() { editor?.layout() }
function format() {
  const val = editor?.getValue() ?? ''
  try {
    editor?.setValue(sqlFormat(val, { language: 'sql' }))
  } catch { /* ignore format errors */ }
}

defineExpose({ getValue, format, layout })
</script>

<style scoped>
.monaco-container {
  width: 100%;
  height: 100%;
}
</style>
