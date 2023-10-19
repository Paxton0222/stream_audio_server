import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/radio/:room/:channel',
      name: 'radio',
      component: () => import("../views/RadioView.vue") 
    },
    // 设置404页面
    {
      path: '/:catchAll(.*)',
      component: () => import("../views/NotFound.vue"),
      name: 'NotFound',
    },
  ]
})

export default router
