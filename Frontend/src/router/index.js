import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/buynsell',
      name: 'buynsell',
      component: () => import('../views/BuynsellView.vue'), 
    },
    {
      path: '/messages',
      name: 'messages',
      component: () => import('../views/MessagesView.vue'), 
    },
    {
      path: '/services',
      name: 'services',
      component: () => import('../views/ServicesView.vue'), 
    },
  ],
})

export default router
