<template>
  <el-drawer v-model="visible" :title="isEdit ? '编辑连接' : '新建连接'" size="480px" @close="reset">
    <el-form :model="form" label-width="90px" size="small">
      <el-form-item label="连接名称" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="数据库类型" required>
        <el-select v-model="form.db_type" style="width:100%">
          <el-option label="MySQL" value="mysql" />
          <el-option label="PostgreSQL" value="postgresql" />
          <el-option label="SQLite" value="sqlite" />
        </el-select>
      </el-form-item>
      <template v-if="form.db_type !== 'sqlite'">
        <el-form-item label="主机">
          <el-input v-model="form.host" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="form.port" :min="1" :max="65535" style="width:100%" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </template>
      <el-form-item label="数据库名">
        <el-input v-model="form.database" :placeholder="form.db_type === 'sqlite' ? '文件路径' : '默认数据库'" />
      </el-form-item>
      <el-form-item label="分组">
        <el-input v-model="form.group_name" />
      </el-form-item>

      <el-divider>
        SSH 隧道
        <el-tooltip content="通过跳板机 SSH 隧道连接数据库，适用于云数据库等无法直接访问的场景" placement="top">
          <el-icon style="margin-left:4px;cursor:pointer"><InfoFilled /></el-icon>
        </el-tooltip>
      </el-divider>
      <el-form-item label="启用 SSH">
        <el-switch v-model="form.ssh_enabled" />
      </el-form-item>
      <template v-if="form.ssh_enabled">
        <el-form-item label="SSH 主机">
          <el-input v-model="form.ssh_host" />
        </el-form-item>
        <el-form-item label="SSH 端口">
          <el-input-number v-model="form.ssh_port" :min="1" :max="65535" style="width:100%" />
        </el-form-item>
        <el-form-item label="SSH 用户名">
          <el-input v-model="form.ssh_username" />
        </el-form-item>
        <el-form-item label="SSH 密码">
          <el-input v-model="form.ssh_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="私钥">
          <el-input v-model="form.ssh_private_key" type="textarea" :rows="3" placeholder="PEM 内容" />
        </el-form-item>
      </template>

      <el-divider>
        SSL
        <el-tooltip content="对数据库连接启用 TLS 加密传输，防止密码和数据在网络上明文传输" placement="top">
          <el-icon style="margin-left:4px;cursor:pointer"><InfoFilled /></el-icon>
        </el-tooltip>
      </el-divider>
      <el-form-item label="启用 SSL">
        <el-switch v-model="form.ssl_enabled" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="onTest" :loading="testing">测试连接</el-button>
      <el-button type="primary" @click="onSave" :loading="saving">保存</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { useConnectionsStore } from '@/stores/connections'
import { testConnection } from '@/api/connections'
import type { ConnectionForm } from '@/api/connections'

const props = defineProps<{ visible: boolean; initial?: any }>()
const emit = defineEmits<{ (e: 'update:visible', v: boolean): void; (e: 'saved'): void }>()

const store = useConnectionsStore()
const visible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
const isEdit = computed(() => !!props.initial?.id)
const saving = ref(false)
const testing = ref(false)

const defaultForm = (): ConnectionForm => ({
  name: '', db_type: 'mysql', host: '127.0.0.1', port: 3306,
  username: 'root', password: '', database: '',
  group_name: '', ssh_enabled: false, ssh_host: '', ssh_port: 22,
  ssh_username: '', ssh_password: '', ssh_private_key: '',
  ssl_enabled: false,
})

const form = ref<ConnectionForm>(defaultForm())

watch(() => props.initial, (v) => {
  if (v) form.value = { ...defaultForm(), ...v, password: '' }
  else form.value = defaultForm()
}, { immediate: true })

function reset() { form.value = defaultForm() }

async function onSave() {
  saving.value = true
  try {
    if (isEdit.value) await store.update(props.initial.id, form.value)
    else await store.create(form.value)
    ElMessage.success('保存成功')
    emit('saved')
    visible.value = false
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    saving.value = false
  }
}

async function onTest() {
  if (!props.initial?.id) {
    ElMessage.warning('请先保存连接再测试')
    return
  }
  testing.value = true
  try {
    const r = await testConnection(props.initial.id)
    ElMessage[r.success ? 'success' : 'error'](r.message)
  } catch (e: any) {
    ElMessage.error(e.message)
  } finally {
    testing.value = false
  }
}
</script>
