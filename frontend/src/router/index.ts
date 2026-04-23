import { createRouter, createWebHashHistory } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [{ path: '/', component: AppLayout }],
})

export default router
