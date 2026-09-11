<template>
  <el-drawer v-model="visible" title="行详情" size="min(600px, 100vw)" append-to-body destroy-on-close>
    <div class="detail-toolbar">
      <span>第 {{ index + 1 }} / {{ rows.length }} 行</span>
      <el-tooltip content="上一行"><el-button :icon="ArrowLeft" :disabled="index <= 0" aria-label="上一行" @click="index--" /></el-tooltip>
      <el-tooltip content="下一行"><el-button :icon="ArrowRight" :disabled="index >= rows.length - 1" aria-label="下一行" @click="index++" /></el-tooltip>
      <el-button :icon="CopyDocument" @click="copy(JSON.stringify(row, null, 2))">复制 JSON</el-button>
    </div>
    <el-input v-model="search" :prefix-icon="Search" placeholder="搜索字段或值" clearable aria-label="搜索字段或值" />
    <div class="field-count">{{ fields.length }} / {{ columns.length }} 个字段</div>
    <dl class="detail-fields">
      <div v-for="field in fields" :key="field.position" class="detail-field">
        <dt>{{ field.name }}</dt>
        <dd :class="{ 'empty-value': field.value == null || field.value === '' }">{{ field.display }}</dd>
        <el-tooltip content="复制值">
          <el-button text :icon="CopyDocument" :aria-label="'复制 ' + field.name" @click="copy(field.value == null ? 'NULL' : typeof field.value === 'string' ? field.value : JSON.stringify(field.value, null, 2))" />
        </el-tooltip>
      </div>
    </dl>
    <el-empty v-if="!fields.length" description="无匹配字段" :image-size="64" />
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ArrowLeft, ArrowRight, CopyDocument, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { copyTextToClipboard } from '@/utils/clipboard'

const props = defineProps<{ columns: string[]; rows: Record<string, any>[] }>()
const visible = defineModel<boolean>({ default: false })
const index = defineModel<number>('index', { default: 0 })
const search = ref('')
const row = computed(() => props.rows[index.value] ?? {})
watch(visible, value => { if (value) search.value = '' })

function display(value: any): string {
  if (value == null) return 'NULL'
  if (value === '') return '空字符串'
  if (typeof value === 'object') return JSON.stringify(value, null, 2)
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value)
      if (parsed !== null && typeof parsed === 'object') return JSON.stringify(parsed, null, 2)
    } catch { /* Plain text is displayed unchanged. */ }
  }
  return String(value)
}

const fields = computed(() => props.columns.map((name, position) => ({
  name, position, value: row.value[name], display: display(row.value[name]),
})).filter(field => `${field.name}\n${field.display}`.toLocaleLowerCase().includes(search.value.toLocaleLowerCase())))

async function copy(value: string) {
  try {
    await copyTextToClipboard(value)
    ElMessage.success('已复制')
  } catch (error: any) {
    ElMessage.error(error?.message || '复制失败')
  }
}
</script>

<style scoped>
.detail-toolbar { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.detail-toolbar > span { margin-right: auto; font-size: 13px; }
.detail-toolbar :deep(.el-button + .el-button) { margin-left: 0; }
.field-count { margin: 12px 0; color: var(--el-text-color-secondary); font-size: 12px; }
.detail-fields { margin: 0; }
.detail-field { display: grid; grid-template-columns: minmax(0, 150px) minmax(0, 1fr) 32px; gap: 12px; padding: 14px 0; border-bottom: 1px solid var(--el-border-color); align-items: start; }
dt { font-size: 13px; font-weight: 600; overflow-wrap: anywhere; }
dd { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; font-family: monospace; font-size: 13px; line-height: 1.6; }
.empty-value { color: var(--el-text-color-secondary); font-style: italic; }
@media (max-width: 480px) {
  .detail-field { grid-template-columns: minmax(0, 1fr) 32px; gap: 8px; }
  dt { grid-column: 1; }
  dd { grid-column: 1; }
  .detail-field > :last-child { grid-column: 2; grid-row: 1 / 3; }
}
</style>
