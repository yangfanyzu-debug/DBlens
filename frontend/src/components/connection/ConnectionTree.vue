<template>
  <div class="conn-tree">
    <div v-for="(group, gname) in grouped" :key="gname" class="group">
      <div class="group-header" @click="toggleGroup(gname)">
        <el-icon class="chevron" :class="{ expanded: expanded[gname] }"><CaretRight /></el-icon>
        <span>{{ gname || '默认' }}</span>
        <span class="group-count">{{ group.length }}</span>
      </div>
      <div v-show="expanded[gname]" class="group-items">
        <div
          v-for="conn in group" :key="conn.id"
          class="conn-item"
          :class="{ active: activeConnId === conn.id }"
          @click="onConnect(conn)"
          @contextmenu.prevent="showMenu($event, conn)"
        >
          <div class="conn-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <span class="conn-name">{{ conn.name }}</span>
          <el-tag size="small" class="db-tag" :type="dbTagType(conn.db_type) || undefined">{{ conn.db_type }}</el-tag>
        </div>
      </div>
    </div>
    <div v-if="!connections.length" class="empty">
      <el-icon :size="28"><DocumentAdd /></el-icon>
      <span>暂无连接</span>
    </div>

    <!-- context menu -->
    <div v-if="menuConn" class="ctx-menu" :style="menuStyle">
      <div class="ctx-item" @click="onEdit">
        <el-icon><Edit /></el-icon> 编辑
      </div>
      <div class="ctx-item danger" @click="onDelete">
        <el-icon><Delete /></el-icon> 删除
      </div>
      <div class="ctx-divider" />
      <div class="ctx-item cancel" @click="menuConn = null">取消</div>
    </div>

    <ConnectionForm v-model:visible="editVisible" :initial="editConn" @saved="editConn = null" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import { storeToRefs } from 'pinia'
import { CaretRight, Connection, DocumentAdd, Edit, Delete } from '@element-plus/icons-vue'
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
      if (!(key in expanded)) expanded[key] = true
    }
    g[key].push(c)
  }
  return g
})

function dbTagType(db_type: string) {
  if (db_type === 'mysql') return 'primary'
  if (db_type === 'postgresql') return 'success'
  return 'info'
}

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
.conn-tree { padding: 6px 0; flex: 1; overflow-y: auto; }

.group-header {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 14px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  user-select: none;
  transition: color 0.15s;
}
.group-header:hover { color: var(--text-secondary); }

.chevron {
  transition: transform 0.2s ease;
  font-size: 10px;
}
.chevron.expanded { transform: rotate(90deg); }

.group-count {
  margin-left: auto;
  background: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 10px;
}

.group { margin-bottom: 8px; }
.group-items { margin-bottom: 2px; }

.conn-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px 7px 20px;
  min-height: 28px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: all 0.12s ease;
  border-left: 2px solid transparent;
}
.conn-item:hover {
  background: rgba(88, 166, 255, 0.06);
  color: var(--text-primary);
  border-left-color: rgba(88, 166, 255, 0.3);
}
.conn-item.active {
  background: var(--glow-blue);
  color: var(--accent-blue);
  border-left-color: var(--accent-blue);
}

.conn-icon { display: flex; align-items: center; opacity: 0.6; }
.conn-item:hover .conn-icon,
.conn-item.active .conn-icon { opacity: 1; }

.conn-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.db-tag {
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  opacity: 0.9;
  border: none;
  min-width: 38px;
  justify-content: center;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px 16px;
  color: var(--text-muted);
  font-size: 13px;
}

.ctx-menu {
  position: fixed;
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 9999;
  min-width: 140px;
  padding: 4px;
  backdrop-filter: blur(8px);
}
.ctx-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  cursor: pointer;
  font-size: 13px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  transition: all 0.1s;
}
.ctx-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.ctx-item.danger { color: var(--accent-red); }
.ctx-item.danger:hover { background: rgba(248, 81, 73, 0.1); }
.ctx-divider { height: 1px; background: var(--border-muted); margin: 4px 0; }
</style>
