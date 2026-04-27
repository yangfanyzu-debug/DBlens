import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { getCurrentUser, type CurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<CurrentUser | null>(null)
  const loading = ref(false)
  const ready = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)
  const isAdmin = computed(() => Boolean(user.value?.is_admin))

  async function bootstrap() {
    loading.value = true
    error.value = null
    try {
      const response = await getCurrentUser()
      user.value = response.user
    } catch (err) {
      user.value = null
      error.value = err instanceof Error ? err.message : '请从 RuoYi 登录后进入 DBLens'
    } finally {
      loading.value = false
      ready.value = true
    }
  }

  return {
    user,
    loading,
    ready,
    error,
    isAuthenticated,
    isAdmin,
    bootstrap,
  }
})
