<template>
  <el-dialog v-model="visible" title="导出数据" width="400px">
    <el-form label-width="80px" size="small">
      <el-form-item label="格式">
        <el-radio-group v-model="format">
          <el-radio value="csv">CSV</el-radio>
          <el-radio value="json">JSON</el-radio>
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="doExport">导出</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Tab } from '@/stores/tabs'
import { exportData } from '@/api/data'

const props = defineProps<{ visible: boolean; tab: Tab }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void }>()
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const format = ref('csv')

async function doExport() {
  const { blob, filename } = await exportData(props.tab.connId!, props.tab.database!, props.tab.table!, format.value)
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  visible.value = false
}
</script>
