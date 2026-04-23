<template>
  <div class="result-table-wrap">
    <div v-if="stmt.affected_rows !== null && stmt.affected_rows !== undefined" class="affected">
      影响行数：{{ stmt.affected_rows }}
    </div>
    <el-table
      v-else
      :data="tableData"
      size="small"
      border
      stripe
      height="100%"
      style="width:100%"
    >
      <el-table-column
        v-for="col in stmt.columns"
        :key="col"
        :prop="col"
        :label="col"
        min-width="120"
        sortable
        show-overflow-tooltip
      />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { QueryResult } from '@/stores/query'

const props = defineProps<{ stmt: QueryResult }>()

const tableData = computed(() =>
  props.stmt.rows.map(row => {
    const obj: Record<string, any> = {}
    props.stmt.columns.forEach((col, i) => { obj[col] = row[i] })
    return obj
  })
)
</script>

<style scoped>
.result-table-wrap { height: 100%; overflow: auto; }
.affected { padding: 16px; color: var(--el-text-color-secondary); }
</style>
