import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import App from './App.vue'
import { useAuthStore } from './stores/auth'
import './style.css'

const pinia = createPinia()
const authStore = useAuthStore(pinia)

await authStore.bootstrap()

createApp(App).use(pinia).use(ElementPlus).use(router).mount('#app')
