import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type Theme = 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
  const current = ref<Theme>('light')

  function toggle() {
    current.value = current.value === 'dark' ? 'light' : 'dark'
  }

  function set(t: Theme) {
    current.value = t
  }

  return { current, toggle, set }
})
