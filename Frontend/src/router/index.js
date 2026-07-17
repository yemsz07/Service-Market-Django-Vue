import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import axios from 'axios'

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
  ],
})

// Navigation guard
router.beforeEach(async (to, from, next) => {
    console.log("ROUTER GUARD RUNNING")

    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

    if (requiresAuth) {
        console.log("CALLING CHECK AUTH")

        try {
            const res = await axios.get(
                "http://127.0.0.1:8000/api/check-auth/",
                {
                    withCredentials: true
                }
            )

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
