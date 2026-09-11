<template>
  <el-drawer v-model="visible" title="行详情" size="min(600px, 100vw)" append-to-body destroy-on-close>
    <div class="detail-sticky">
    <div class="detail-toolbar">
      <span>第 {{ index + 1 }} / {{ rows.length }} 行</span>
      <el-tooltip content="上一行"><el-button :icon="ArrowLeft" :disabled="index <= 0" aria-label="上一行" @click="index--" /></el-tooltip>
      <el-tooltip content="下一行"><el-button :icon="ArrowRight" :disabled="index >= rows.length - 1" aria-label="下一行" @click="index++" /></el-tooltip>
      <el-button :icon="CopyDocument" @click="copy(JSON.stringify(row, null, 2))">复制 JSON</el-button>
    </div>
    <el-input v-model="search" :prefix-icon="Search" placeholder="搜索字段或值" clearable aria-label="搜索字段或值" />
    <div class="field-count">{{ fields.length }} / {{ columns.length }} 个字段</div>
    </div>
    <dl class="detail-fields">
      <div v-for="field in fields" :key="field.position" class="detail-field">
        <dt>{{ field.name }}</dt>
        <dd>
          <div class="field-value" :class="{ collapsible: field.display.length > 120 || field.display.split('\n').length > 5, expanded: expanded.has(field.position), 'empty-value': field.value == null || field.value === '' }">{{ field.display }}</div>
          <div v-if="field.display.length > 120 || field.display.split('\n').length > 5" class="field-actions">
            <el-button link type="primary" :icon="expanded.has(field.position) ? ArrowUp : ArrowDown" :aria-expanded="expanded.has(field.position)" @click="toggle(field.position)">{{ expanded.has(field.position) ? '收起' : '展开' }}</el-button>
            <el-button link :icon="FullScreen" @click="fullField = field">完整查看</el-button>
          </div>
        </dd>
        <el-tooltip content="复制值">
          <el-button text :icon="CopyDocument" :aria-label="'复制 ' + field.name" @click="copy(field.value == null ? 'NULL' : typeof field.value === 'string' ? field.value : JSON.stringify(field.value, null, 2))" />
        </el-tooltip>
      </div>
    </dl>
    <el-empty v-if="!fields.length" description="无匹配字段" :image-size="64" />
  </el-drawer>
  <el-dialog :model-value="Boolean(fullField)" :title="fullField?.name ?? '字段详情'" width="min(960px, 94vw)" append-to-body destroy-on-close @update:model-value="value => { if (!value) fullField = null }">
    <pre class="full-value">{{ fullField?.display }}</pre>
    <template #footer>
      <el-button :icon="CopyDocument" @click="copy(rawValue(fullField?.value))">复制完整值</el-button>
      <el-button @click="fullField = null">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ArrowLeft, ArrowRight, ArrowUp, ArrowDown, FullScreen, CopyDocument, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { copyTextToClipboard } from '@/utils/clipboard'

const props = defineProps<{ columns: string[]; rows: Record<string, any>[] }>()
const visible = defineModel<boolean>({ default: false })
const index = defineModel<number>('index', { default: 0 })
const search = ref('')
const expanded = ref(new Set<number>())
const fullField = ref<{ name: string; display: string; value: any } | null>(null)
const row = computed(() => props.rows[index.value] ?? {})
watch(visible, value => { if (value) search.value = '' })
watch([row, visible], () => {
  expanded.value = new Set()
  fullField.value = null
})

function toggle(position: number) {
  if (expanded.value.has(position)) expanded.value.delete(position)
  else expanded.value.add(position)
}

function rawValue(value: any): string {
  return value == null ? 'NULL' : typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

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
.detail-sticky { position: sticky; top: -20px; z-index: 1; background: var(--el-bg-color); padding-top: 20px; margin-top: -20px; padding-bottom: 1px; }
.field-value { white-space: pre-wrap; overflow-wrap: anywhere; }
.field-value.collapsible { display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 5; overflow: hidden; max-height: 8em; }
.field-value.expanded { display: block; max-height: 280px; overflow: auto; }
.field-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
.field-actions :deep(.el-button) { margin: 0; }
.full-value { margin: 0; max-height: 60vh; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; line-height: 1.6; }
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
