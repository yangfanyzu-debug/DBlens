<script setup lang="ts">
import { computed, watch } from 'vue'
import { RouterView } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { buildRuoYiLoginUrl } from '@/utils/ruoyiLogin'

const theme = useThemeStore()
const authStore = useAuthStore()
const { loading, ready, error, isAuthenticated } = storeToRefs(authStore)
const ruoyiLoginUrl = computed(() => {
  return buildRuoYiLoginUrl({
    configuredLoginUrl: import.meta.env.VITE_RUOYI_LOGIN_URL,
    origin: window.location.origin,
    currentPath: window.location.pathname,
    currentSearch: window.location.search,
    currentHash: window.location.hash,
  })
})

watch(() => theme.current, (t) => {
  document.querySelector('.app-layout')?.classList.toggle('theme-dark', t === 'dark')
}, { immediate: true })
</script>

<template>
  <div v-if="loading || !ready" class="app-shell-state">
    <el-result icon="info" title="正在校验登录状态" sub-title="请稍候，正在从 RuoYi 同步当前用户信息。" />
  </div>
  <div v-else-if="!isAuthenticated" class="app-shell-state">
    <el-result icon="warning" title="无法获取当前登录用户" :sub-title="error || '请从 RuoYi 登录后进入 DBLens。'">
      <template #extra>
        <div class="login-actions">
          <el-button type="primary" :href="ruoyiLoginUrl" tag="a">前往 RuoYi 登录</el-button>
          <a class="login-link" :href="ruoyiLoginUrl" target="_blank" rel="noreferrer">{{ ruoyiLoginUrl }}</a>
        </div>
      </template>
    </el-result>
  </div>
  <RouterView v-else />
</template>

<style scoped>
.app-shell-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 24px;
  background: linear-gradient(180deg, var(--shell-backdrop-soft) 0%, var(--shell-backdrop) 100%);
}

.login-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.login-link {
  font-size: 13px;
  color: var(--accent-blue);
  word-break: break-all;
}
</style>
