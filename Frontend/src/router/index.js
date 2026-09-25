import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import api from '../api/api'




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
      meta: { requiresAuth: true }
    },
    {
      path: '/messages',
      name: 'messages',
      component: () => import('../views/MessagesView.vue'), 
      meta: { requiresAuth: true }
    },
    {
      path: '/services',
      name: 'services',
      component: () => import('../views/ServicesView.vue'), 
      meta: { requiresAuth: true }
    },
    {
      path: '/reglog',
      name: 'reglog',
      component: () => import('../views/Reglog.vue'), 
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue'), 
    },
    {
      path: '/portal-dashboard',
      name: 'portal-dashboard',
      component: () => import('../views/Pdashboard.vue'), 
      meta: { requiresAuth: true }
    },
    {
      path: '/portfolio',
      name: 'portfolio',
      component: () => import('../views/PortfolioView.vue'), 
      meta: { requiresAuth: true }
    },
    {
      path: '/payment-success',
      name: 'PaymentSuccess',
      component: () => import('../views/PaymentSuccess.vue')
    },
    {
      path: '/payment-cancelled',
      name: 'PaymentCancelled',
      component: () => import('../views/PaymentCancelled.vue')
    }
  ],
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
    console.log("ROUTER GUARD RUNNING")

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

    if (requiresAuth) {
        console.log("CALLING CHECK AUTH")

        try {
            const res = await api.get("/check-auth/")   // gagamitin na ang baseURL mula sa .env

            console.log(res.data)
            next()

        } catch (e) {
            console.log(e)
            next("/reglog")
        }

    } else {
        next()
    }
})

export default router
