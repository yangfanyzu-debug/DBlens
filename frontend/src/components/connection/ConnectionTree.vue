<template>
  <div class="conn-tree">
    <div v-for="(group, gname) in grouped" :key="gname" class="group">
      <div class="group-header" @click="toggleGroup(gname)">
        <el-icon><ArrowRight v-if="!expanded[gname]" /><ArrowDown v-else /></el-icon>
        <span>{{ gname || '默认' }}</span>
      </div>
      <div v-show="expanded[gname]">
        <div
          v-for="conn in group" :key="conn.id"
          class="conn-item"
          :class="{ active: activeConnId === conn.id }"
          @click="onConnect(conn)"
          @contextmenu.prevent="showMenu($event, conn)"
        >
          <el-icon><Connection /></el-icon>
          <span>{{ conn.name }}</span>
          <el-tag size="small" class="db-tag">{{ conn.db_type }}</el-tag>
        </div>
      </div>
    </div>
    <div v-if="!connections.length" class="empty">暂无连接</div>

    <!-- context menu -->
    <div v-if="menuConn" class="ctx-menu" :style="menuStyle">
      <div class="ctx-item" @click="onEdit">编辑</div>
      <div class="ctx-item danger" @click="onDelete">删除</div>
      <div class="ctx-item cancel" @click="menuConn = null">取消</div>
    </div>

    <ConnectionForm v-model:visible="editVisible" :initial="editConn" @saved="editConn = null" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { ArrowRight, ArrowDown, Connection } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useConnectionsStore } from '@/stores/connections'
import ConnectionForm from './ConnectionForm.vue'

const emit = defineEmits<{ (e: 'open-db-tree', connId: string): void }>()

const store = useConnectionsStore()
const { connections, activeConnId } = storeToRefs(store)

const expanded = reactive<Record<string, boolean>>({})
const menuConn = ref<any>(null)
const menuStyle = ref({})
const editVisible = ref(false)
const editConn = ref<any>(null)

onMounted(() => {
  store.fetchAll()
  document.addEventListener('click', closeMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeMenu)
})

function closeMenu() {
  menuConn.value = null
}

const grouped = computed(() => {
  const g: Record<string, any[]> = {}
  for (const c of connections.value) {
    const key = c.group_name || ''
    if (!g[key]) {
      g[key] = []
      if (!(key in expanded)) expanded[key] = true  // auto-expand new groups
    }
    g[key].push(c)
  }
  return g
})

function toggleGroup(name: string) {
  expanded[name] = !expanded[name]
}

async function onConnect(conn: any) {
  try {
    await store.connect(conn.id)
    emit('open-db-tree', conn.id)
  } catch (e: any) {
    ElMessage.error(e.message)
  }
}

function showMenu(e: MouseEvent, conn: any) {
  menuConn.value = conn
  menuStyle.value = { top: e.clientY + 'px', left: e.clientX + 'px' }
}

function onEdit() {
  const conn = menuConn.value
  menuConn.value = null
  if (!conn) return
  editConn.value = conn
  editVisible.value = true
}

async function onDelete() {
  const conn = menuConn.value
  menuConn.value = null
  if (!conn) return
  try {
    await ElMessageBox.confirm(`确认删除连接 "${conn.name}"？`, '删除', { type: 'warning' })
    await store.remove(conn.id)
    ElMessage.success('已删除')
  } catch {
    // user cancelled
  }
}
</script>

<style scoped>
.conn-tree { padding: 4px 0; flex: 1; overflow-y: auto; }
.group-header { display: flex; align-items: center; gap: 4px; padding: 4px 12px; cursor: pointer; font-size: 12px; color: var(--el-text-color-secondary); user-select: none; }
.conn-item { display: flex; align-items: center; gap: 6px; padding: 5px 20px; cursor: pointer; font-size: 13px; }
.conn-item:hover { background: var(--el-fill-color-light); }
.conn-item.active { background: var(--el-color-primary-light-9); color: var(--el-color-primary); }
.db-tag { margin-left: auto; }
.empty { padding: 12px; color: var(--el-text-color-placeholder); font-size: 13px; text-align: center; }
.ctx-menu { position: fixed; background: var(--el-bg-color); border: 1px solid var(--el-border-color); border-radius: 4px; box-shadow: var(--el-box-shadow-light); z-index: 9999; min-width: 100px; }
.ctx-item { padding: 8px 16px; cursor: pointer; font-size: 13px; }
.ctx-item:hover { background: var(--el-fill-color-light); }
.ctx-item.danger { color: var(--el-color-danger); }
</style>
