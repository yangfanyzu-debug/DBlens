<script setup lang="ts">
import { watch } from 'vue'
import { RouterView } from 'vue-router'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
watch(() => theme.current, (t) => {
  document.querySelector('.app-layout')?.classList.toggle('theme-dark', t === 'dark')
}, { immediate: true })
</script>

<template>
  <RouterView />
</template>
